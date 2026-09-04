"""
Management command: sync_job_order_status
========================================

Walks every JobOrder and reconciles its `status` with the truth:

  - If is_fully_filled() returns True   → status = "Full Filled"
  - Otherwise                            → status = "Open"

This is the one-shot fix for the data that was already in the
"Open" + remaining=0 state before the auto-flip fix (5c78d55f)
landed. New contract creates / deletes are now handled inline by
ContractSerializer.create / ContractViewSet.perform_destroy.

Usage:
  python manage.py sync_job_order_status              # apply
  python manage.py sync_job_order_status --dry-run   # preview only
  python manage.py sync_job_order_status --report out.json

Safe to re-run — it just rewrites status to the correct value.
"""

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from companies.models import JobOrder
import json


class Command(BaseCommand):
    help = (
        "Reconcile JobOrder.status with is_fully_filled() for every "
        "JobOrder in the database. Safe to re-run."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't write changes; just print what would change.",
        )
        parser.add_argument(
            "--report",
            type=str,
            default=None,
            help="Optional path to write a JSON diff report to.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        report_path = options["report"]

        changed = []
        unchanged = 0
        for jo in JobOrder.objects.all().select_related("company"):
            truth = "Full Filled" if jo.is_fully_filled() else "Open"
            if jo.status != truth:
                changed.append({
                    "id": jo.id,
                    "reference_number": jo.reference_number,
                    "company": jo.company.company_name if jo.company else None,
                    "old_status": jo.status,
                    "new_status": truth,
                })
                if not dry_run:
                    jo.status = truth
                    jo.save(update_fields=["status"])
            else:
                unchanged += 1

        verb = "Would change" if dry_run else "Changed"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} {len(changed)} JobOrder row(s); "
            f"{unchanged} already correct."
        ))

        for row in changed:
            self.stdout.write(
                f"  #{row['id']:>4}  {row['reference_number']:<20} "
                f"({row['company']})  "
                f"{row['old_status']!r:<14} -> {row['new_status']!r}"
            )

        if report_path:
            with open(report_path, "w") as f:
                json.dump(changed, f, indent=2, cls=DjangoJSONEncoder)
            self.stdout.write(self.style.SUCCESS(
                f"Report written to {report_path}"
            ))
