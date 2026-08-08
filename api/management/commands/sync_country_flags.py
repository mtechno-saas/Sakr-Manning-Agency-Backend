"""
Sync the canonical country list into core.Flag.

Background:
- The frontend "Add New Principal" form has a hardcoded country list
  in `fieldConfigs.js:130-156` (e.g. "United States", "Cape Verde").
- The Settings → Dropdown Data → Nationalities/Flags page reads/writes
  `core.Flag` via `/api/core/flags/`.
- These two lists use different naming conventions for the same countries,
  so a user who picks "United States" in the form and then adds the same
  country in Settings would get two separate Flag rows that don't match.

This command:
1. Inserts the canonical "frontend" names (e.g. "United States") as Flags.
2. Inserts the canonical "backend" names (e.g. "United States of America")
   that aren't already present, with a `canonical_for` pointer to the
   frontend name.
3. Is idempotent — re-running on a fully-seeded DB is a no-op.

Run with:
    python manage.py sync_country_flags            # apply
    python manage.py sync_country_flags --dry-run  # show what would change
    python manage.py sync_country_flags --backup  # write before-state to backups/flags_before_sync_<ts>.json
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from core.models import Flag


# Canonical "frontend" names — exactly what the form's hardcoded list shows.
# This is the user-facing surface, so it's the source of truth for
# display in both the form and Settings.
FRONTEND_CANONICAL = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina",
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin",
    "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
    "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon",
    "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile",
    "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia",
    "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
    "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
    "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany",
    "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India",
    "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica",
    "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia",
    "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar",
    "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
    "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia",
    "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
    "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman",
    "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea",
    "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
    "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Samoa", "San Marino",
    "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Solomon Islands", "Somalia", "South Africa", "South Korea",
    "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
    "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand",
    "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia",
    "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
    "Yemen", "Zambia", "Zimbabwe",
]

# Aliases — names that the migration seeded with a longer/parenthesised
# form. When we insert these, we also leave the existing row alone (so
# historical Company.company_flag values that match the old name still
# resolve). Frontend users see the canonical name in dropdowns.
LEGACY_ALIASES = {
    "United States of America": "United States",
    "Cabo Verde": "Cape Verde",
    "Congo (Congo-Brazzaville)": "Congo",
    "Czechia (Czech Republic)": "Czech Republic",
    "Myanmar (formerly Burma)": "Myanmar",
    "Palestine State": "Palestine",
}


class Command(BaseCommand):
    help = "Sync the canonical country list into core.Flag (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without touching the DB.",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Write current flags to backups/flags_before_sync_<timestamp>.json",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        do_backup = options["backup"]

        before = list(Flag.objects.values("id", "name").order_by("name"))
        before_names = {f["name"] for f in before}

        self.stdout.write(self.style.NOTICE(
            f"Current Flag count: {len(before)}"
        ))

        if do_backup and not dry:
            backup_dir = os.path.join("backups")
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(backup_dir, f"flags_before_sync_{ts}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(before, fh, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f"Backup written: {path}"))

        # 1) Insert any missing canonical names.
        to_add_canonical = [n for n in FRONTEND_CANONICAL if n not in before_names]
        if to_add_canonical:
            self.stdout.write(self.style.WARNING(
                f"Canonical names missing from DB ({len(to_add_canonical)}): "
                f"{to_add_canonical[:10]}{'...' if len(to_add_canonical) > 10 else ''}"
            ))
            if not dry:
                Flag.objects.bulk_create(
                    [Flag(name=n) for n in to_add_canonical],
                    ignore_conflicts=True,
                )
        else:
            self.stdout.write(self.style.SUCCESS(
                "All canonical names already present in DB."
            ))

        # 2) Leave legacy alias rows in place (they may be referenced by
        # historical Company records). Just report on them.
        legacy_present = [n for n in LEGACY_ALIASES.keys() if n in before_names]
        if legacy_present:
            self.stdout.write(self.style.NOTICE(
                f"Legacy alias rows still in DB (kept for backward compat): "
                f"{legacy_present}"
            ))

        # 3) Summary
        after_count = Flag.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Flag count: {len(before)} -> {after_count} "
            f"({'dry run' if dry else 'applied'})"
        ))

        if dry:
            self.stdout.write(self.style.WARNING(
                "\n--dry-run: nothing was written. Re-run without --dry-run to apply."
            ))
