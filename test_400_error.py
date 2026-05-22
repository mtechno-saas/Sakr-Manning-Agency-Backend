import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from django.test import Client

client = Client()
response = client.post('/api/documents/', {}, content_type='application/json')
print("Status:", response.status_code)
print("Content:", response.content.decode('utf-8'))
