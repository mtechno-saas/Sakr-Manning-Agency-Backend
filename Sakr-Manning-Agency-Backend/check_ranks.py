
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings') 
django.setup()

from api.models import Rank

print("--- START RANK CHECK ---")
ranks = list(Rank.objects.values_list('id', 'name'))
print(f"Total Ranks: {len(ranks)}")
for r_id, r_name in ranks:
    print(f"ID: {r_id}, Name: {r_name}")

if 26 in [r[0] for r in ranks]:
    print("Rank 26 EXISTS.")
else:
    print("Rank 26 DOES NOT EXIST.")
print("--- END RANK CHECK ---")
