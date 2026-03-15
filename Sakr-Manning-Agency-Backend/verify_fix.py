import os
import django
import sys

# Setup Django environment
sys.path.append('/run/media/storm/TECNO SQUEARE/django test')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users
from api.serializer import UsersSerializer

def verify_fix():
    print("Verifying fix for User Update Status Error...")
    
    # Create or get a test user
    email = "verification_test_user@example.com"
    try:
        user = Users.objects.get(email=email)
        print(f"Found existing test user: {email}")
    except Users.DoesNotExist:
        user = Users.objects.create_user(
            email=email,
            password="TestPassword123!",
            first_name="Test",
            phone_number="+1234567890" # Initial value
        )
        print(f"Created new test user: {email}")

    # Prepare data for update with empty strings
    data = {
        "nationality": "",
        "phone_number": ""
    }
    
    # Test serializer validation
    # We need to pass the instance and data. 
    # Since partial=True is usually used for PATCH requests in DRF, we test that scenario.
    serializer = UsersSerializer(instance=user, data=data, partial=True)
    
    if serializer.is_valid():
        print("✅ Serializer validation PASSED with empty strings.")
        serializer.save()
        print("✅ User updated successfully.")
        
        # specific check
        updated_user = Users.objects.get(email=email)
        print(f"Updated Nationality: '{updated_user.nationality}'")
        print(f"Updated Phone Number: '{updated_user.phone_number}'")
        
        if updated_user.phone_number == "":
             print("✅ Phone number is empty string as expected.")
        else:
             print("⚠️ Warning: Phone number is not empty string (might be null or unchanged).")

    else:
        print("❌ Serializer validation FAILED.")
        print("Errors:", serializer.errors)

if __name__ == "__main__":
    verify_fix()
