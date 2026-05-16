import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from rest_framework.test import APIRequestFactory
from api.views import DocumentViewSet

factory = APIRequestFactory()
data = {
    "email": "mahmoudddffr_test2@gmail.com",
    "first_name": "mahmoudddffr",
    "rank_ids": [1, "Master"],
    "title": "Test Application"
}

request = factory.post('/api/documents/', data=data, format='json')
view = DocumentViewSet.as_view({'post': 'create'})
response = view(request)

print("Status:", response.status_code)
print("Data:", response.data)
