"""
Tests for the sync_ranks management command.
"""
import io
from django.core.management import call_command
from django.test import TestCase

from api.models import Document, Rank


class SyncRanksCommandTests(TestCase):

    def setUp(self):
        # Start every test with a clean slate so POSITION_CHOICES names
        # are exactly the ones the test asserts about.
        Rank.objects.all().delete()

    def _call(self, *args):
        out = io.StringIO()
        call_command("sync_ranks", *args, stdout=out)
        return out.getvalue()

    def test_dry_run_makes_no_changes(self):
        before = Rank.objects.count()
        output = self._call("--dry-run")
        after = Rank.objects.count()
        self.assertEqual(before, after, "Dry run must not write")
        self.assertIn("dry run", output.lower())

    def test_adds_position_choices_missing_from_db(self):
        self.assertEqual(Rank.objects.count(), 0)
        self._call()
        # All 81 POSITION_CHOICES names should now be present
        canonical_names = {c[0] for c in Document.POSITION_CHOICES}
        db_names = set(Rank.objects.values_list("name", flat=True))
        missing = canonical_names - db_names
        self.assertEqual(
            missing, set(),
            f"Expected all POSITION_CHOICES names in DB; missing: {missing}"
        )

    def test_new_rows_get_sync_codes(self):
        self._call()
        new_rows = Rank.objects.filter(code__regex=r"^SYNC-\d{3}$")
        self.assertGreater(new_rows.count(), 0)
        for r in new_rows:
            self.assertTrue(r.code.startswith("SYNC-"))

    def test_does_not_delete_existing_rows(self):
        # Pre-existing custom row (not in POSITION_CHOICES)
        existing = Rank.objects.create(name="ZZZ-Internal-Test-Rank", code="ZZZ-1.000")
        before = Rank.objects.count()
        self._call()
        after = Rank.objects.count()
        self.assertGreaterEqual(after, before)
        self.assertTrue(Rank.objects.filter(id=existing.id).exists())

    def test_idempotent_on_second_run(self):
        self._call()
        count_after_first = Rank.objects.count()
        output = self._call()
        count_after_second = Rank.objects.count()
        self.assertEqual(count_after_first, count_after_second)
        self.assertIn("already in Rank table", output)

    def test_existing_rank_not_duplicated(self):
        # Pre-seed one POSITION_CHOICES name with a non-SYNC code
        Rank.objects.create(name="Master / Captain", code="DO-1.000")
        self._call()
        # The seed row must remain (not duplicated, not renamed)
        self.assertEqual(Rank.objects.filter(code="DO-1.000").count(), 1)
        self.assertTrue(
            Rank.objects.filter(name="Master / Captain", code="DO-1.000").exists()
        )
        # The other 80 POSITION_CHOICES names should still be added
        self.assertGreaterEqual(Rank.objects.count(), 81)
