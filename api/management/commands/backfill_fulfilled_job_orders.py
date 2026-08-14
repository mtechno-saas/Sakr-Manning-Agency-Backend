"""
One-shot backfill: scan every JobOrder and, for any whose
positions are all fully filled, set its status to "Fulfilled".

Idempotent and additive: only transitions from the
auto-promotable statuses (Pending, Open, In Progress, Active).
Cancelled / Closed / Hold / Fulfilled are left alone so the
command can be re-run safely.

Run with:
    python manage.py backfill_fulfilled_job_orders
    python manage.py backfill_fulfilled_job_orders --dry-run
"""
from django.core.management.base import BaseCommand

from companies.models import JobOrder


AUTO_PROMOTABLE_STATUSES = {"Pending", "Open", "In Progress", "Active"}


class Command(BaseCommand):
    help = (
        "Backfill JobOrder.status = 'Fulfilled' for any job order "
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
                        f"({jo.status} -> Fulfilled)"
                    )
                else:
                    jo.status = "Fulfilled"
                    jo.save(update_fields=["status", "updated_at"])
                    self.stdout.write(self.style.SUCCESS(
                        f"  Promoted: {jo.reference_number} -> Fulfilled"
                    ))
                promoted += 1
            else:
                skipped += 1

        # How many are already Fulfilled?
        already = JobOrder.objects.filter(status="Fulfilled").count()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done. Promoted: {promoted}, already Fulfilled: {already}, "
            f"skipped (not full): {skipped}"
        ))
        if dry:
            self.stdout.write(self.style.WARNING(
                "\n--dry-run: nothing was written. "
                "Re-run without --dry-run to apply."
            ))
