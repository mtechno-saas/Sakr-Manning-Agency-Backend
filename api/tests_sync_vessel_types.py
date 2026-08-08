"""
Tests for the sync_vessel_types management command.
"""
import io
from django.core.management import call_command
from django.test import TestCase

from core.models import VesselType


class SyncVesselTypesCommandTests(TestCase):

    def setUp(self):
        # The migration 0005 seeds these legacy rows on the test DB.
        # Use get_or_create so this is idempotent across test runs.
        for name in ("Container Ships", "Bulk Carriers", "Tankers",
                     "Ro-Ro Ships", "Passenger Ships", "Fishing Vessels",
                     "Recreational", "Offshore Support Vessels",
                     "Icebreakers", "Tugboats"):
            VesselType.objects.get_or_create(name=name)

    def _call(self, *args):
        out = io.StringIO()
        call_command("sync_vessel_types", *args, stdout=out)
        return out.getvalue()

    def test_dry_run_makes_no_changes(self):
        before = VesselType.objects.count()
        output = self._call("--dry-run")
        after = VesselType.objects.count()
        self.assertEqual(before, after, "Dry run must not write")
        self.assertIn("dry run", output.lower())

    def test_adds_canonical_names_missing_from_db(self):
        # Make sure none of these canonical names exist before the test
        for canonical in ("VLCC", "Aframax", "FPSO", "Cable Layer",
                          "Pipe Layer", "LNG Carrier"):
            VesselType.objects.filter(name=canonical).delete()

        self._call()

        for name in ("VLCC", "Aframax", "FPSO", "Cable Layer",
                     "Pipe Layer", "LNG Carrier"):
            self.assertTrue(
                VesselType.objects.filter(name=name).exists(),
                f"Expected VesselType named {name!r} to be created",
            )

    def test_does_not_delete_existing_rows(self):
        """The command is add-only; existing rows must be preserved."""
        existing_count = VesselType.objects.count()
        # Add a non-canonical row (someone's custom name)
        VesselType.objects.create(name="ZZZ-Internal-Test-Type")
        before = VesselType.objects.count()

        self._call()

        after = VesselType.objects.count()
        self.assertGreaterEqual(after, before)
        # The custom row survives
        self.assertTrue(
            VesselType.objects.filter(name="ZZZ-Internal-Test-Type").exists(),
            "Non-canonical rows must be preserved"
        )

    def test_idempotent_on_second_run(self):
        self._call()
        count_after_first = VesselType.objects.count()
        output = self._call()
        count_after_second = VesselType.objects.count()
        self.assertEqual(count_after_first, count_after_second)
        self.assertIn("All canonical names already present", output)

    def test_existing_canonical_rows_unchanged(self):
        existing = VesselType.objects.create(name="VLCC")
        self._call()
        existing.refresh_from_db()
        self.assertEqual(existing.name, "VLCC")
        # No duplicate should be created (VesselType.name is unique)
        self.assertEqual(VesselType.objects.filter(name="VLCC").count(), 1)
