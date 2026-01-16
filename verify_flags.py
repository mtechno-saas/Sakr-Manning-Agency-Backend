import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from core.models import Flag
count = Flag.objects.count()
print(f"Count: {count}")
with open("flag_count.txt", "w") as f:
    f.write(str(count))
