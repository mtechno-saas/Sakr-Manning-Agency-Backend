"""
Sync the canonical rank list into api.Rank.

Background:
- The frontend's rank dropdown is dynamic (reads from /api/ranks/),
  so unlike flags and principal types, no frontend hardcoded list
  needs mirroring.
- However, `Document.position` is a CharField with a hardcoded
  `POSITION_CHOICES` list of 81 rank names (`api/models.py:952`).
  When a user picks a position in the admin attachments section,
  they pick from those 81 names. But the dynamic Rank table on
  production has only 64 rows, so 17 of the model's hardcoded
  names have no matching Rank row.

This command seeds the missing names from `Document.POSITION_CHOICES`
into the Rank table, auto-generating a `code` of the form
`SYNC-NNN` for each (existing production codes are a mix of
`DO-`, `CUS-`, `DR-`, `TR-` formats with no single convention,
so a new prefix keeps the new entries visually distinct).

Run with:
    python manage.py sync_ranks            # apply
    python manage.py sync_ranks --dry-run  # show what would change
    python manage.py sync_ranks --backup   # write before-state to backups/
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from api.models import Document, Rank


def _allocate_sync_codes(n: int) -> list[str]:
    """
    Allocate n unique 'SYNC-NNN' codes by finding the highest
    existing SYNC-NNN code and generating the next n sequential
    codes. Caller must insert all n in one bulk_create to avoid
    races with re-runs.
    """
    existing = Rank.objects.filter(code__regex=r"^SYNC-\d{3}$").values_list(
        "code", flat=True
    )
    max_n = 0
    for c in existing:
        try:
            max_n = max(max_n, int(c.split("-")[1]))
        except (IndexError, ValueError):
            continue
    return [f"SYNC-{max_n + 1 + i:03d}" for i in range(n)]


class Command(BaseCommand):
    help = (
        "Sync ranks from Document.POSITION_CHOICES into api.Rank. "
        "Idempotent and add-only."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without touching the DB.",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Write current ranks to backups/ranks_before_sync_<ts>.json",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        do_backup = options["backup"]

        before = list(Rank.objects.values("id", "code", "name").order_by("code"))
        before_names = {f["name"] for f in before}

        self.stdout.write(self.style.NOTICE(
            f"Current Rank count: {len(before)}"
        ))

        if do_backup and not dry:
            backup_dir = os.path.join("backups")
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(backup_dir, f"ranks_before_sync_{ts}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(before, fh, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f"Backup written: {path}"))

        # Source list: Document.POSITION_CHOICES (81 hardcoded names)
        canonical_names = [c[0] for c in Document.POSITION_CHOICES]
        to_add = [n for n in canonical_names if n not in before_names]

        if to_add:
            self.stdout.write(self.style.WARNING(
                f"Names in Document.POSITION_CHOICES missing from Rank "
                f"({len(to_add)}): {to_add[:10]}{'...' if len(to_add) > 10 else ''}"
            ))
            if not dry:
                # Allocate codes in one shot BEFORE bulk_create so each
                # row gets a unique SYNC-NNN (bulk_create with
                # ignore_conflicts=True would otherwise drop all but one
                # if we called _next_sync_code() in a loop).
                codes = _allocate_sync_codes(len(to_add))
                new_rows = [
                    Rank(name=n, code=c)
                    for n, c in zip(to_add, codes)
                ]
                Rank.objects.bulk_create(new_rows, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(
                    f"Created {len(new_rows)} new Rank rows with SYNC-NNN codes."
                ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "All Document.POSITION_CHOICES names already in Rank table."
            ))

        after_count = Rank.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Rank count: {len(before)} -> {after_count} "
            f"({'dry run' if dry else 'applied'})"
        ))

        if dry:
            self.stdout.write(self.style.WARNING(
                "\n--dry-run: nothing was written. Re-run without --dry-run to apply."
            ))
