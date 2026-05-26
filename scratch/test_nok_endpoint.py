import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

# Get or create admin user
admin, _ = User.objects.get_or_create(
    email="admin_nok_test@example.com",
    defaults={
        "first_name": "Admin",
        "role": "Admin",
    }
)

# Get or create employee user
employee, _ = User.objects.get_or_create(
    email="employee_nok_test@example.com",
    defaults={
        "first_name": "Employee",
        "role": "Employee",
    }
)

client = APIClient()
client.force_authenticate(user=admin)

# Payload matching the frontend request:
payload = {
    "user": employee.id,
    "full_name": "Jane Doe",
    "relationship": "Wife",
    "address_country": "US",
    "phone": "123456789"
}

try:
    response = client.post(
        f"/api/users/next-of-kin/?user={employee.id}",
        payload,
        format="json",
        HTTP_HOST="localhost"
    )
    print("Status code:", response.status_code)
    print("Response content:", response.content.decode())
except Exception as e:
    import traceback
    traceback.print_exc()
