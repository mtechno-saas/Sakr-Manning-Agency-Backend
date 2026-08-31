"""
Deduplicate overlapping SeaService records in the DB.

When a CV is parsed by the Sakr template parser, sea-service records
with overlapping date ranges used to be saved verbatim. A seafarer
who was on two vessels at once showed up in the DB as such. The
/ai/parse/ endpoint now runs `_dedupe_overlapping_sea_service`
before saving, so new uploads are clean.

This command cleans the EXISTING records that were saved before the
dedup fix landed. It applies the same algorithm (half-open overlap,
longer record wins) per user.

Usage:
  # Preview — show what would be deleted, don't touch the DB
  python manage.py dedupe_sea_service --dry-run

  # Apply for real
  python manage.py dedupe_sea_service

  # Just one user
  python manage.py dedupe_sea_service --user 98

  # Print a JSON report
  python manage.py dedupe_sea_service --report report.json

The dedup logic lives in `ai_document.views._dedupe_overlapping_sea_service`
and is reused verbatim here. Records with unparseable dates are kept
as-is (we can't reason about their placement in time).
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import SeaService


def _ss_to_dict(record: SeaService) -> dict:
    """Shrink a SeaService row to the dict shape the dedup helper
    expects. Only the fields the dedup algorithm actually inspects.
    """
    return {
        "id": record.id,
        "vessel_name_imo": record.vessel_name_imo or "",
        "vessel_name": record.vessel_name or "",
        "company_name": record.company_name or "",
        "rank": record.rank or "",
        "signed_on": record.signed_on,
        "signed_off": record.signed_off,
        "period": record.period or "",
    }


class Command(BaseCommand):
    help = (
        "Delete SeaService rows that overlap in time with a longer "
        "SeaService row for the same seafarer. Half-open overlap, "
        "longer record wins."
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
            help="Print what would be deleted, but don't touch the DB.",
        )
        parser.add_argument(
            "--report",
            type=str,
            default=None,
            help="Write a JSON report of the run to this path.",
        )

    def handle(self, *args, **options):
        # Lazy import — the helper lives in ai_document.views and we
        # don't want a hard api -> ai_document import at module load.
        from ai_document.views import _dedupe_overlapping_sea_service

        user_filter = options["user"]
        dry_run = options["dry_run"]
        report_path = options["report"]

        # Pull all SeaService records for the targeted user(s),
        # preserving DB id so we can delete the right rows later.
        qs = SeaService.objects.all().order_by("user_id", "id")
        if user_filter is not None:
            qs = qs.filter(user_id=user_filter)

        # Group by user
        by_user: dict[int, list[SeaService]] = {}
        for record in qs:
            by_user.setdefault(record.user_id, []).append(record)

        if not by_user:
            self.stdout.write(self.style.WARNING(
                "No SeaService records to process."
            ))
            return

        self.stdout.write(
            f"Scanning {qs.count()} SeaService row(s) across "
            f"{len(by_user)} user(s)..."
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes written."))
        self.stdout.write("")

        total_deleted = 0
        total_kept = 0
        total_users_touched = 0
        report = {
            "dry_run": dry_run,
            "scanned_rows": qs.count(),
            "users_processed": 0,
            "rows_deleted": 0,
            "rows_kept": 0,
            "users": [],
        }

        for user_id, records in by_user.items():
            dicts = [_ss_to_dict(r) for r in records]
            kept_dicts, dropped_dicts = _dedupe_overlapping_sea_service(dicts)

            if not dropped_dicts:
                # Nothing to do for this user — keep the report small
                # so admins can see the noise.
                total_kept += len(kept_dicts)
                continue

            total_users_touched += 1
            total_deleted += len(dropped_dicts)
            total_kept += len(kept_dicts)

            user_email = (
                records[0].user.email
                if records and records[0].user
                else f"user#{user_id}"
            )
            self.stdout.write(
                f"  user #{user_id} ({user_email}): "
                f"keep {len(kept_dicts)}, drop {len(dropped_dicts)}"
            )
            for d in dropped_dicts:
                r = d["record"]
                vessel = r.get("vessel_name") or r.get("vessel_name_imo") or "?"
                self.stdout.write(
                    f"    - drop id={r['id']:>4}  {vessel}  "
                    f"{r.get('signed_on') or '?'} -> {r.get('signed_off') or '?'}"
                )

            report["users"].append({
                "user_id": user_id,
                "user_email": user_email,
                "kept": [
                    {"id": d["id"], "vessel": d.get("vessel_name") or d.get("vessel_name_imo"),
                     "signed_on": str(d.get("signed_on")) if d.get("signed_on") else None,
                     "signed_off": str(d.get("signed_off")) if d.get("signed_off") else None}
                    for d in kept_dicts
                ],
                "dropped": [
                    {"id": d["record"]["id"],
                     "vessel": d["record"].get("vessel_name") or d["record"].get("vessel_name_imo"),
                     "signed_on": str(d["record"].get("signed_on")) if d["record"].get("signed_on") else None,
                     "signed_off": str(d["record"].get("signed_off")) if d["record"].get("signed_off") else None,
                     "kept_id": d["kept_record"]["id"],
                     "reason": d["reason"]}
                    for d in dropped_dicts
                ],
            })

            if not dry_run:
                with transaction.atomic():
                    ids_to_delete = [d["record"]["id"] for d in dropped_dicts]
                    SeaService.objects.filter(id__in=ids_to_delete).delete()

        report["users_processed"] = total_users_touched
        report["rows_deleted"] = total_deleted
        report["rows_kept"] = total_kept

        self.stdout.write("")
        self.stdout.write(
            f"  scanned={qs.count()}  "
            f"users_touched={total_users_touched}  "
            f"kept={total_kept}  "
            f"deleted={total_deleted}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run — no changes written. Re-run without --dry-run to apply."
            ))
        elif total_deleted > 0:
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Deleted {total_deleted} overlapping row(s)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\nNothing to dedupe — DB is already clean."
            ))

        if report_path:
            p = Path(report_path)
            p.write_text(
                json.dumps(report, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            self.stdout.write(self.style.SUCCESS(
                f"\nReport written to {p} ({p.stat().st_size:,} bytes)."
            ))
