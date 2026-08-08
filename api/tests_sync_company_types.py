"""
Tests for the sync_company_types management command.
"""
import io
from django.core.management import call_command
from django.test import TestCase

from core.models import CompanyType


class SyncCompanyTypesCommandTests(TestCase):

    def setUp(self):
        # No migration seeds these; production starts at 0.
        # Make sure test starts clean of canonical names.
        for name in ("Cargo Manning Principals", "Vessel Owner", "Other"):
            CompanyType.objects.filter(name=name).delete()

    def _call(self, *args):
        out = io.StringIO()
        call_command("sync_company_types", *args, stdout=out)
        return out.getvalue()

    def test_dry_run_makes_no_changes(self):
        before = CompanyType.objects.count()
        output = self._call("--dry-run")
        after = CompanyType.objects.count()
        self.assertEqual(before, after, "Dry run must not write")
        self.assertIn("dry run", output.lower())

    def test_adds_all_canonical_names(self):
        self.assertEqual(CompanyType.objects.count(), 0)
        self._call()
        self.assertEqual(CompanyType.objects.count(), 11)

        for name in (
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
        ):
            self.assertTrue(
                CompanyType.objects.filter(name=name).exists(),
                f"Expected CompanyType named {name!r} to be created",
            )

    def test_does_not_delete_existing_rows(self):
        # Custom row someone added manually
        CompanyType.objects.create(name="ZZZ-Internal-Test-Type")
        before = CompanyType.objects.count()
        self._call()
        after = CompanyType.objects.count()
        self.assertGreaterEqual(after, before)
        # The custom row survives
        self.assertTrue(
            CompanyType.objects.filter(name="ZZZ-Internal-Test-Type").exists(),
            "Non-canonical rows must be preserved"
        )

    def test_idempotent_on_second_run(self):
        self._call()
        count_after_first = CompanyType.objects.count()
        output = self._call()
        count_after_second = CompanyType.objects.count()
        self.assertEqual(count_after_first, count_after_second)
        self.assertIn("All canonical names already present", output)

    def test_existing_canonical_rows_unchanged(self):
        # Pre-create one canonical row to make sure it's not duplicated
        existing = CompanyType.objects.create(name="Vessel Owner")
        self._call()
        existing.refresh_from_db()
        self.assertEqual(existing.name, "Vessel Owner")
        # UNIQUE on name means no duplicates
        self.assertEqual(
            CompanyType.objects.filter(name="Vessel Owner").count(),
            1,
        )
