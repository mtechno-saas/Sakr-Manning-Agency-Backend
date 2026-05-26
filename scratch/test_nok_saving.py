import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users, NextOfKin
from api.serializer import NextOfKinSerializer

# Create or get employee
employee, created = Users.objects.get_or_create(
    email="test_emp_nok@example.com",
    defaults={
        "first_name": "Test",
        "middle_name": "Employee",
        "role": "Employee",
    }
)

# Admin user
admin, _ = Users.objects.get_or_create(
    email="test_admin_nok@example.com",
    defaults={
        "first_name": "Test",
        "middle_name": "Admin",
        "role": "Admin",
    }
)

print(f"Admin: {admin}, Employee: {employee}")

data = {
    'user': employee.id,
    'full_name': 'Jane Doe',
    'relationship': 'Wife',
    'phone': '123456789'
}

serializer = NextOfKinSerializer(data=data)
if serializer.is_valid():
    try:
        print("Validated data:", serializer.validated_data)
        nok = serializer.save()
        print("Success! NextOfKin created with ID:", nok.id)
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("Serializer validation failed:", serializer.errors)
