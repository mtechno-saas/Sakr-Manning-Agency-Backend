"""
Seed the canonical CompanyType rows the system expects.

The ``Company.company_type`` field is a ForeignKey to ``core.CompanyType``.
The ``CompanySerializer`` uses ``SlugRelatedField(slug_field='name')`` so the
frontend sends the name (e.g. ``"Cruise & Hospitality Manning Companies"``)
and we look it up. If the row doesn't exist, the create call returns 400:

    "company_type": ["Object with name=X does not exist."]

The new VPS starts with a fresh DB, so this table is empty until
``seed_real_data.py`` is run -- but that script also creates 14 companies,
18 ships, 60 users, hundreds of contracts. Way too much for a fresh prod
server where you might just want to onboard a single new principal.

This command is the minimal seed: just the 4 canonical CompanyType rows.
Idempotent (``get_or_create``). Use it on any environment that needs the
dropdown to work.

Usage:

    python manage.py seed_company_types
    python manage.py seed_company_types --dry-run     # show what would be created
    python manage.py seed_company_types --quiet       # only print the count
"""
from django.core.management.base import BaseCommand

from core.models import CompanyType


# Canonical list. Keep in sync with the values that ``seed_real_data.py``
# uses (companies_data[i]['type']) and with what the frontend offers in the
# company-type dropdown. If the frontend adds a new option, add it here too
# OR the next deploy on a fresh DB will hit the same 400.
CANONICAL_TYPES = [
    "Full Crew Management Companies",
    "Cruise & Hospitality Manning Companies",
    "Cargo Manning Companies",
    "Offshore & Oil/Gas Manning Companies",
]


class Command(BaseCommand):
    help = (
        "Create the canonical CompanyType rows (4 of them) if they don't "
        "already exist. Idempotent. Use after a fresh-DB deploy or whenever "
        "the frontend company-type dropdown is empty."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be created, but don't write to the DB.",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Only print the final count, no per-row detail.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        quiet = options["quiet"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN -- no changes written."))

        created = 0
        already = 0
        for name in CANONICAL_TYPES:
            exists = CompanyType.objects.filter(name=name).exists()
            if exists:
                already += 1
                if not quiet:
                    self.stdout.write(f"  keep  {name!r}")
                continue

            if dry_run:
                self.stdout.write(f"  +create  {name!r}")
                created += 1
                continue

            CompanyType.objects.create(name=name)
            created += 1
            if not quiet:
                self.stdout.write(self.style.SUCCESS(f"  +created  {name!r}"))

        self.stdout.write("")
        self.stdout.write(
            f"  total={len(CANONICAL_TYPES)}  "
            f"created={created}  already_present={already}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run -- no changes written. Re-run without --dry-run to apply."
            ))
        elif created == 0:
            self.stdout.write(self.style.SUCCESS(
                "\nNothing to do -- all canonical CompanyType rows already exist."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Created {created} CompanyType row(s)."
            ))