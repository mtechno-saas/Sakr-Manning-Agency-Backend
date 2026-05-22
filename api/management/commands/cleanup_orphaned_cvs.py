from django.core.management.base import BaseCommand
from api.models import CVSubmission, Contract


class Command(BaseCommand):
    help = 'Clear ship and company from CV Submissions that have no active contract backing them'

    def handle(self, *args, **options):
        cvs = CVSubmission.objects.filter(company__isnull=False)
        cleaned = 0

        for cv in cvs:
            # Check if there is any active contract for this user + company
            has_contract = Contract.objects.filter(
                user=cv.user,
                company=cv.company,
                status__in=['Pending Signature', 'Signed', 'Active', 'Draft']
            ).exists()

            if not has_contract:
                old_company = cv.company
                old_ship = cv.ship
                cv.company = None
                cv.ship = None
                cv.save(update_fields=['company', 'ship'])
                cleaned += 1
                self.stdout.write(
                    f"  Cleared CV #{cv.id} ({cv.user.first_name}): "
                    f"company={old_company} -> None, ship={old_ship} -> None"
                )

        self.stdout.write(self.style.SUCCESS(f'\nDone! Cleaned {cleaned} orphaned CV Submissions.'))
