"""
Clear the Principal that the blank-FK lookup silently assigned.

The bug
-------
The dashboard's placement modal sends "" for every select the admin did not
touch. CVSubmissionSerializer.to_internal_value resolved the Principal by
name in two steps:

    company = Company.objects.filter(company_name__iexact=source).first()
    if not company:
        company = Company.objects.filter(company_name__icontains=source).first()

With source = "" the exact match finds nothing, but the "contains" match
matches EVERY row -- an empty string is a substring of every string -- so
.first() returned the first row of the table. Every application created
that way was silently attached to that Principal ("3 SEAS SHIPPING"), with
no error anywhere.

The serializer no longer does that (a blank value is dropped before the
lookup -- see api/serializer.py), but the rows written before the fix are
still pointing at the wrong Principal.

Usage
-----
    python manage.py clear_auto_assigned_principals             # dry run
    python manage.py clear_auto_assigned_principals --apply     # do it

Options
-------
--apply           actually change the rows (default: dry run)
--company-id N    the principal to clear (default: the one the bug picked)
--keep-linked     keep the rows linked to a job order -- those were
                  picked by hand, not by the bug
"""

from django.core.management.base import BaseCommand

from api.models import CVSubmission
from companies.models import Company


class Command(BaseCommand):
    help = (
        "Clear the Principal that the blank-FK lookup silently assigned to "
        "CV submissions."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually change the rows (default: dry run).",
        )
        parser.add_argument(
            "--company-id",
            type=int,
            default=None,
            help=(
                "The principal to clear. Default: the one the bug picked "
                "(the first row of the company table)."
            ),
        )
        parser.add_argument(
            "--keep-linked",
            action="store_true",
            help=(
                "Keep the rows linked to a job order -- a job order always "
                "carries its own principal, so those were picked by hand."
            ),
        )

    def handle(self, *args, **options):
        if options["company_id"]:
            company = Company.objects.filter(id=options["company_id"]).first()
        else:
            # Exactly the row the bug picked: Company.objects.first().
            company = Company.objects.first()

        if company is None:
            self.stdout.write(self.style.WARNING("No principal found - nothing to do."))
            return

        queryset = CVSubmission.objects.filter(company=company)
        if not options["keep_linked"]:
            queryset = queryset.filter(job_position__isnull=True)

        self.stdout.write(
            f"Principal: {company.company_name} (id={company.id})"
        )
        self.stdout.write(f"Candidates: {queryset.count()}")

        for cv in queryset.select_related("user", "position").order_by("id"):
            position = cv.position.name if cv.position_id else "-"
            who = cv.user.email or cv.user.full_name
            self.stdout.write(
                f"  cv #{cv.id:<5} {who:<40} position={position:<22} "
                f"created={cv.created_at:%Y-%m-%d %H:%M}"
            )

        if not options["apply"]:
            self.stdout.write(self.style.WARNING(
                "Dry run - nothing changed. Re-run with --apply to clear them."
            ))
            return

        ids = list(queryset.values_list("id", flat=True))
        queryset.update(company=None)
        self.stdout.write(self.style.SUCCESS(
            f"Cleared the Principal on {len(ids)} CV submissions: {ids}"
        ))
