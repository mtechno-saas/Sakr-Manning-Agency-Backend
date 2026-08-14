"""
One-shot backfill: scan every JobOrder and, for any whose
positions are all fully filled, set its status to "Full Filled".

Idempotent and additive: only transitions from "Open". Anything
else ("Close", already "Full Filled") is left alone so the
command can be re-run safely.

Run with:
    python manage.py backfill_fulfilled_job_orders
    python manage.py backfill_fulfilled_job_orders --dry-run
"""
from django.core.management.base import BaseCommand

from companies.models import JobOrder


AUTO_PROMOTABLE_STATUSES = {"Open"}


class Command(BaseCommand):
    help = (
        "Backfill JobOrder.status = 'Full Filled' for any job order "
        "whose positions are all fully filled. Idempotent."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without writing.",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]

        candidates = JobOrder.objects.filter(
            status__in=list(AUTO_PROMOTABLE_STATUSES)
        )

        promoted = 0
        already = 0
        skipped = 0
        for jo in candidates.iterator():
            if jo.is_fully_filled():
                if dry:
                    self.stdout.write(
                        f"  [dry-run] WOULD promote: {jo.reference_number} "
                        f"({jo.status} -> Full Filled)"
                    )
                else:
                    jo.status = "Full Filled"
                    jo.save(update_fields=["status", "updated_at"])
                    self.stdout.write(self.style.SUCCESS(
                        f"  Promoted: {jo.reference_number} -> Full Filled"
                    ))
                promoted += 1
            else:
                skipped += 1

        # How many are already Full Filled?
        already = JobOrder.objects.filter(status="Full Filled").count()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done. Promoted: {promoted}, already Full Filled: {already}, "
            f"skipped (not full): {skipped}"
        ))
        if dry:
            self.stdout.write(self.style.WARNING(
                "\n--dry-run: nothing was written. "
                "Re-run without --dry-run to apply."
            ))
