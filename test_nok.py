import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users, NextOfKin
from api.serializer import NextOfKinSerializer

user = Users.objects.filter(role='Admin').first()
employee = Users.objects.exclude(role='Admin').first()

print(f"Admin: {user}, Employee: {employee}")

data = {
    'user': employee.id if employee else 1,
    'full_name': 'Test Nok',
    'relationship': 'Wife',
    'address_country': 'US',
    'phone': '123456789'
}

serializer = NextOfKinSerializer(data=data)
if serializer.is_valid():
    try:
        nok = serializer.save()
        print("Success:", nok.id)
    except Exception as e:
        print("Exception:", type(e), str(e))
else:
    print("Errors:", serializer.errors)
