"""
Tests for the sync_country_flags management command.

The command seeds core.Flag with the canonical country list (matching
the frontend form's hardcoded list) while keeping the legacy
parenthesised-name rows from migration 0004 for backward compatibility
with historical Company records.
"""
import io
from django.core.management import call_command
from django.test import TestCase

from core.models import Flag


class SyncCountryFlagsCommandTests(TestCase):

    def setUp(self):
        # The migration 0004_populate_flags may have already seeded these
        # legacy alias rows. Create them idempotently.
        for name in ("United States of America", "Cabo Verde",
                     "Congo (Congo-Brazzaville)"):
            Flag.objects.get_or_create(name=name)
        # Make sure none of the canonical-name rows exist before each test
        # so we can assert the command adds them.
        for canonical in ("United States", "Cape Verde", "Taiwan",
                          "Vatican City", "Czech Republic", "Myanmar",
                          "Palestine", "Congo"):
            Flag.objects.filter(name=canonical).delete()

    def _call(self, *args):
        out = io.StringIO()
        call_command("sync_country_flags", *args, stdout=out)
        return out.getvalue()

    def test_dry_run_makes_no_changes(self):
        before = Flag.objects.count()
        output = self._call("--dry-run")
        after = Flag.objects.count()
        self.assertEqual(before, after, "Dry run must not write")
        self.assertIn("dry run", output.lower())

    def test_adds_canonical_names_missing_from_db(self):
        """After running, frontend-named countries must all be present."""
        self.assertFalse(Flag.objects.filter(name="United States").exists())
        self.assertFalse(Flag.objects.filter(name="Cape Verde").exists())
        self.assertFalse(Flag.objects.filter(name="Taiwan").exists())

        self._call()  # apply

        for name in ["United States", "Cape Verde", "Taiwan", "Vatican City",
                     "Czech Republic", "Myanmar", "Palestine", "Congo"]:
            self.assertTrue(
                Flag.objects.filter(name=name).exists(),
                f"Expected Flag named {name!r} to be created",
            )

    def test_preserves_legacy_alias_rows(self):
        """The migration rows must be kept for backward compat."""
        self._call()
        self.assertTrue(Flag.objects.filter(name="United States of America").exists())
        self.assertTrue(Flag.objects.filter(name="Cabo Verde").exists())
        self.assertTrue(Flag.objects.filter(name="Congo (Congo-Brazzaville)").exists())

    def test_idempotent_on_second_run(self):
        """Re-running must be a no-op once seeded."""
        self._call()
        count_after_first = Flag.objects.count()
        output = self._call()
        count_after_second = Flag.objects.count()
        self.assertEqual(count_after_first, count_after_second)
        self.assertIn("All canonical names already present", output)

    def test_existing_canonical_rows_unchanged(self):
        """If a canonical row already exists, don't touch it."""
        existing = Flag.objects.create(name="United States")
        self._call()
        existing.refresh_from_db()
        self.assertEqual(existing.name, "United States")
        # No duplicate should be created (Flag.name is unique)
        self.assertEqual(
            Flag.objects.filter(name="United States").count(),
            1,
        )
