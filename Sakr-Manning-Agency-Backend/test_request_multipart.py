import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate
from api.views import UserViewSet
from api.models import Users

factory = APIRequestFactory()
request = factory.post('/api/users/users/', {
    "email": "mahmoudddff3@gmail.com",
    "first_name": "mahmoudddff",
    "rank_ids": [1, "Chief Engineer"]
}, format='multipart')

# Create a mock admin user for auth
user, _ = Users.objects.get_or_create(email="admin_test@test.com", defaults={"role": "Admin", "first_name": "Admin"})
force_authenticate(request, user=user)

view = UserViewSet.as_view({'post': 'create'})
response = view(request)
print("Response Status:", response.status_code)
print("Response Data:", response.data)
