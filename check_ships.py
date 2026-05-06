import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from ships.models import Ship
from companies.models import Company

for c in Company.objects.all():
    ships = Ship.objects.filter(company=c)
    if ships.count() > 0:
        print(f"Company: {c.company_name} (ID: {c.id}) has {ships.count()} ships")
        for s in ships:
            print(f"  - Ship: {s.ship_name} (ID: {s.id})")

