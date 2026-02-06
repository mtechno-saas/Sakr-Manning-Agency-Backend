from django.core.management.base import BaseCommand
from api.models import Certificate, CERTIFICATES


class Command(BaseCommand):
    help = 'Load certificate types from CERTIFICATES constant into the database'

    def handle(self, *args, **options):
        """
        Populate the Certificate model with all predefined certificate types.
        Users will select from these when adding their certificate instances.
        """
        created_count = 0
        updated_count = 0
        
        for code, name in CERTIFICATES:
            certificate, created = Certificate.objects.update_or_create(
                code=code,
                defaults={'name': name}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created certificate: {name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'• Updated certificate: {name}')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Certificate loading complete!\n'
                f'   Created: {created_count}\n'
                f'   Updated: {updated_count}\n'
                f'   Total: {len(CERTIFICATES)} certificate types available\n'
            )
        )
