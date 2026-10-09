from django.test import TestCase

# Create your tests here.
from io import StringIO
from django.core.management import call_command

from core.models import CompanyType


class SeedCompanyTypesCommandTests(TestCase):
    """
    Tests for core/management/commands/seed_company_types.py.

    The command creates the 4 canonical CompanyType rows. Idempotent —
    re-running must not duplicate. Dry-run must not persist.
    """

    def _run(self, **opts):
        out = StringIO()
        call_command("seed_company_types", stdout=out, **opts)
        return out.getvalue()

    def test_creates_all_canonical_rows_on_empty_db(self):
        self.assertEqual(CompanyType.objects.count(), 0)

        out = self._run()

        # The list is the union of the two hardcoded dropdowns in the
        # frontend (fieldConfigs.js has 11, Company.jsx has 8; we keep both
        # covered). If you add a new CompanyType option, bump this number.
        self.assertEqual(CompanyType.objects.count(), 11)
        names = set(CompanyType.objects.values_list("name", flat=True))
        # A representative sample -- the rest are covered by the count check
        self.assertIn("Cruise & Hospitality Manning Principals", names)
        self.assertIn("Cargo Manning Principals", names)
        self.assertIn("Fishing Fleet Manning Principals", names)
        self.assertIn("Full Crew Management Principals", names)
        self.assertIn("Vessel Owner", names)
        self.assertIn("Other", names)
        self.assertIn("Created 11 CompanyType row", out)

    def test_idempotent_second_run_is_a_noop(self):
        self._run()
        first_count = CompanyType.objects.count()

        out = self._run()

        self.assertEqual(CompanyType.objects.count(), first_count)
        self.assertIn("nothing to do", out.lower())
        self.assertIn("already exist", out)

    def test_dry_run_does_not_persist(self):
        self._run(dry_run=True)

        self.assertEqual(CompanyType.objects.count(), 0)

    def test_quiet_suppresses_per_row_detail(self):
        out = self._run(quiet=True)

        self.assertIn("created=11", out)
        # Per-row "+created X" messages are suppressed in quiet mode
        self.assertNotIn("+created", out)

    def test_company_create_succeeds_after_seed(self):
        """End-to-end: after the seed, creating a Company with the
        canonical company_type string works (no more 400 from the
        'Object with name=X does not exist' error)."""
        from companies.models import Company
        self._run()

        c = Company.objects.create(
            company_name="Anglo-Eastern Cruise Management Inc",
            company_type=CompanyType.objects.get(
                name="Cruise & Hospitality Manning Principals"
            ),
        )

        self.assertEqual(
            c.company_type.name, "Cruise & Hospitality Manning Principals"
        )
