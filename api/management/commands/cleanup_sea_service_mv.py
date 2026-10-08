"""
Repair SeaService rows that were corrupted by the old `/`-split parser.

The sea-service parser used to take a "Vessel Name / IMO Number" PDF cell
and do ``cell.split('/')`` to separate the two halves. That silently
broke every vessel whose name contains a ``/`` -- most commonly the
``M/V`` (Motor Vessel), ``S/V`` (Sailing Vessel), ``T/V`` (Tanker?),
``F/V`` (Fishing Vessel) prefix. A real Sakr CV had rows like::

    M/V LILY OF SEA
    M/V SC II
    M/V SIRIOS CEMENT V
    M/V KEMET STAR

The old parser stored::

    vessel_name="M",  imo_number="V LILY OF SEA"
    vessel_name="M",  imo_number="V SC II"
    ...

Every M/V vessel got a bogus IMO number and a vessel name of just "M".

The parser-side fix lives in ``api.seafarer_application_serializers``.
``SeafarerApplicationSerializer._split_vessel_and_imo`` is now idempotent:
it only splits at ``/`` when a real 7-digit IMO is present. New uploads
are clean.

This command is the cleanup for the rows that already exist in the DB.
For each ``SeaService`` row we:

  1. Pick the best "source cell" -- prefer ``vessel_name_imo`` when it
     contains a real 7-digit IMO (that means it was the original raw
     cell from the PDF and the parser never split it). Otherwise
     reconstruct from the broken fields, joining ``vessel_name`` and
     ``imo_number`` with a single ``/`` (no spaces) so the M/V prefix
     is preserved.
  2. Re-run ``_split_vessel_and_imo`` on that source.
  3. If the new ``(vessel_name, imo_number)`` differs from what's stored,
     update the row.

This is safe to re-run -- the new split is idempotent, so a row that's
already correct produces the same result and is left alone.

Usage:

  # Preview -- show what would be rewritten, don't touch the DB
  python manage.py cleanup_sea_service_mv --dry-run

  # Apply for real
  python manage.py cleanup_sea_service_mv

  # Just one user
  python manage.py cleanup_sea_service_mv --user 98

  # Limit how many rows to scan (safety valve on large DBs)
  python manage.py cleanup_sea_service_mv --limit 5000

  # Write a JSON report of every change
  python manage.py cleanup_sea_service_mv --report /tmp/mv_fix.json
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import SeaService


def _reconstruct_source(vessel_name_imo: str, vessel_name: str, imo_number: str) -> str:
    """
    Pick the best source cell to re-run ``_split_vessel_and_imo`` on.

    Preference order:
      1. ``vessel_name_imo`` if it contains a real 7-digit IMO (then it's
         the original raw cell from the PDF; the broken split never
         touched it).
      2. Otherwise, join the (possibly broken) ``vessel_name`` /
         ``imo_number`` fields back together with a single ``/``. We use
         no spaces around the slash because the original PDF cell
         "M/V LILY OF SEA" had no spaces.

    Returns ``""`` when both fields are empty -- the row has no vessel
    info at all, nothing to repair.
    """
    legacy = (vessel_name_imo or "").strip()
    # Re-use the parser's own regex to detect a real IMO. If the legacy
    # field still has one, trust it as the source of truth.
    from api.seafarer_application_serializers import SeafarerApplicationSerializer
    if legacy and SeafarerApplicationSerializer._IMO_NUMBER_RE.search(legacy):
        return legacy

    parts = [p.strip() for p in (vessel_name or "", imo_number or "") if p and p.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return "/".join(parts)


class Command(BaseCommand):
    help = (
        "Repair SeaService rows that were corrupted by the old "
        "Vessel-Name/IMO '/'-split parser (M/V LILY OF SEA bug). "
        "Re-runs the new idempotent split on every row and updates "
        "the DB only when the result differs."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=int,
            default=None,
            help="Only process records for this user id. Default: all users.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be rewritten, but don't touch the DB.",
        )
        parser.add_argument(
            "--report",
            type=str,
            default=None,
            help="Write a JSON report of the run to this path.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Safety valve: process at most N rows. Default: no limit.",
        )

    def handle(self, *args, **options):
        # Lazy import -- the serializer pulls in a lot of model deps and
        # we don't want a hard api -> seafarer_application_serializers
        # import at module load.
        from api.seafarer_application_serializers import SeafarerApplicationSerializer

        split = SeafarerApplicationSerializer()._split_vessel_and_imo

        user_filter = options["user"]
        dry_run = options["dry_run"]
        report_path = options["report"]
        limit = options["limit"]

        qs = SeaService.objects.all().order_by("user_id", "id")
        if user_filter is not None:
            qs = qs.filter(user_id=user_filter)
        if limit is not None:
            qs = qs[:limit]

        rows = list(qs)
        if not rows:
            self.stdout.write(self.style.WARNING(
                "No SeaService records to process."
            ))
            return

        self.stdout.write(
            f"Scanning {len(rows)} SeaService row(s)..."
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN -- no changes written."))
        self.stdout.write("")

        total_fixed = 0
        total_unchanged = 0
        report_rows = []

        # We do per-row atomic writes so a single bad row can't take
        # down the whole batch. With Django's auto-commit this is fine,
        # but the explicit ``transaction.atomic`` makes the intent clear.
        for record in rows:
            source = _reconstruct_source(
                record.vessel_name_imo,
                record.vessel_name,
                record.imo_number,
            )
            new_vessel, new_imo = split(source)

            if new_vessel == (record.vessel_name or "") and new_imo == (record.imo_number or ""):
                total_unchanged += 1
                continue

            total_fixed += 1
            user_email = (
                record.user.email if record.user_id and record.user else f"user#{record.user_id}"
            )
            self.stdout.write(
                f"  fix id={record.id:>5}  user=#{record.user_id} ({user_email})"
            )
            self.stdout.write(
                f"      was:  vessel_name={record.vessel_name!r}  "
                f"imo_number={record.imo_number!r}  "
                f"vessel_name_imo={record.vessel_name_imo!r}"
            )
            self.stdout.write(
                f"      src:  {source!r}"
            )
            self.stdout.write(
                f"      now:  vessel_name={new_vessel!r}  imo_number={new_imo!r}"
            )

            report_rows.append({
                "id": record.id,
                "user_id": record.user_id,
                "user_email": user_email,
                "was_vessel_name": record.vessel_name,
                "was_imo_number": record.imo_number,
                "was_vessel_name_imo": record.vessel_name_imo,
                "source_reconstructed": source,
                "new_vessel_name": new_vessel,
                "new_imo_number": new_imo,
            })

            if not dry_run:
                with transaction.atomic():
                    SeaService.objects.filter(id=record.id).update(
                        vessel_name=new_vessel,
                        imo_number=new_imo,
                    )

        self.stdout.write("")
        self.stdout.write(
            f"  scanned={len(rows)}  fixed={total_fixed}  unchanged={total_unchanged}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run -- no changes written. Re-run without --dry-run to apply."
            ))
        elif total_fixed > 0:
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Repaired {total_fixed} SeaService row(s)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\nNothing to repair -- DB is already clean."
            ))

        if report_path:
            p = Path(report_path)
            p.write_text(
                json.dumps(
                    {
                        "dry_run": dry_run,
                        "scanned_rows": len(rows),
                        "rows_fixed": total_fixed,
                        "rows_unchanged": total_unchanged,
                        "rows": report_rows,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.stdout.write(self.style.SUCCESS(
                f"\nReport written to {p} ({p.stat().st_size:,} bytes)."
            ))