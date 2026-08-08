"""
Sync the canonical company type list into core.CompanyType.

Background:
- There is no seed migration for `core.CompanyType` — production
  starts at 0 entries and grows only as admins add new types via
  Settings → Dropdown Data → Principal Types.
- The Add New Principal form's Principal Type dropdown is a
  hardcoded array of 11 values in `fieldConfigs.js:84-96`. So any
  principal saved through that form will have its `company_type`
  field set to one of those 11 strings, but the DB row for that
  type must exist for downstream filtering to work.

This command seeds the 11 canonical names so the DB matches what
the form is producing. It is add-only — never deletes or renames
existing rows.

Run with:
    python manage.py sync_company_types            # apply
    python manage.py sync_company_types --dry-run  # show what would change
    python manage.py sync_company_types --backup   # write before-state to backups/
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from core.models import CompanyType


# Canonical company type list — exactly the 11 values that the
# frontend Add New Principal form's hardcoded dropdown produces
# (fieldConfigs.js:84-96). This is the user-facing surface, so
# these are the names the DB must contain.
CANONICAL = [
    "Cargo Manning Principals",
    "Cruise & Hospitality Manning Principals",
    "Fishing Fleet Manning Principals",
    "Full Crew Management Principals",
    "General Crew Manning Principals",
    "Offshore & Oil/Gas Manning Principals",
    "Vessel Owner",
    "Shipping Manning Principals",
    "Specialized Marine Manning Principals",
    "Temporary / Contract Manning Agencies",
    "Other",
]


class Command(BaseCommand):
    help = "Sync the canonical company type list into core.CompanyType (idempotent, add-only)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without touching the DB.",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Write current company types to backups/company_types_before_sync_<ts>.json",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        do_backup = options["backup"]

        before = list(CompanyType.objects.values("id", "name").order_by("name"))
        before_names = {f["name"] for f in before}

        self.stdout.write(self.style.NOTICE(
            f"Current CompanyType count: {len(before)}"
        ))

        if do_backup and not dry:
            backup_dir = os.path.join("backups")
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(backup_dir, f"company_types_before_sync_{ts}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(before, fh, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f"Backup written: {path}"))

        to_add = [n for n in CANONICAL if n not in before_names]
        if to_add:
            self.stdout.write(self.style.WARNING(
                f"Canonical names missing from DB ({len(to_add)}): {to_add}"
            ))
            if not dry:
                CompanyType.objects.bulk_create(
                    [CompanyType(name=n) for n in to_add],
                    ignore_conflicts=True,
                )
        else:
            self.stdout.write(self.style.SUCCESS(
                "All canonical names already present in DB."
            ))

        after_count = CompanyType.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"CompanyType count: {len(before)} -> {after_count} "
            f"({'dry run' if dry else 'applied'})"
        ))

        if dry:
            self.stdout.write(self.style.WARNING(
                "\n--dry-run: nothing was written. Re-run without --dry-run to apply."
            ))
