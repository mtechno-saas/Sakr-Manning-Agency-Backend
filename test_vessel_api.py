import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from rest_framework.test import APIClient
from api.models import Users

def test_vessel_types_endpoint():
    # 1. Create a dummy user
    user, created = Users.objects.get_or_create(
        email="test_lang_user2@example.com", 
        defaults={"first_name": "Test", "role": "Employee"}
    )
    user.set_password("password123")
    user.save()

    # Allow testserver in ALLOWED_HOSTS for APIClient tests
    from django.conf import settings
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('testserver')
        
    try:
        # 2. Setup API Client
        client = APIClient()
        client.force_authenticate(user=user)

        # 3. Hit the core endpoint
        print("Sending GET request to /api/core/vessel-types/...")
        response = client.get('/api/core/vessel-types/')
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")

        # 4. Hit the api endpoint
        print("\nSending GET request to /api/vessel-types/...")
        response2 = client.get('/api/vessel-types/')
        print(f"Status Code: {response2.status_code}")
        print(f"Response Data: {response2.data}")

    finally:
        # Cleanup
        print("\nCleaning up dummy user...")
        user.delete()

if __name__ == "__main__":
    test_vessel_types_endpoint()
