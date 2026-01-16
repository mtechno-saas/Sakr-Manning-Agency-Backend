import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from core.models import Flag

print("Starting flag population...")
created_count = 0
for choice in Flag.FLAG_CHOICES:
    country_name = choice[0]
    flag, created = Flag.objects.get_or_create(name=country_name)
    if created:
        created_count += 1

total_count = Flag.objects.count()
print(f"Created {created_count} new flags.")
print(f"Total flags in database: {total_count}")
