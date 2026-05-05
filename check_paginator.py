import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from django.conf import settings
print(settings.REST_FRAMEWORK)

