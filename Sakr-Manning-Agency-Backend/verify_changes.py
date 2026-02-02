import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users, Contract
from interviews.models import Interview
from ships.models import Ship
from companies.models import Company

def verify():
    print("Verifying changes...")

    # Clean up previous test data
    Users.objects.filter(email="hr@test.com").delete()
    Users.objects.filter(email="candidate@test.com").delete()
    Company.objects.filter(company_name="Test Co").delete()

    # 1. Verify User Role
    user = Users.objects.create(email="hr@test.com", first_name="HR", role="HR Manager")
    print(f"User created: {user.email}, Role: {user.role}")
    assert user.role == "HR Manager"

    # 2. Verify Contract Fields
    company = Company.objects.create(company_name="Test Co", company_type="Shipping", contact_email="test@co.com")
    ship = Ship.objects.create(ship_name="Test Ship", imo_number="1234567", company=company)
    contract = Contract.objects.create(
        user=user,
        ship=ship,
        sign_on_date=timezone.now().date(),
        status="Pending Signature"
    )
    print(f"Contract created: {contract.status}")
    assert contract.status == "Pending Signature"
    assert hasattr(contract, 'signed_file')
    assert hasattr(contract, 'signed_at')

    # 3. Verify Interview
    candidate = Users.objects.create(email="candidate@test.com", first_name="Candidate")
    interview = Interview.objects.create(
        candidate=candidate,
        interviewer=user,
        date=timezone.now(),
        status="Scheduled"
    )
    print(f"Interview created: {interview}")
    assert interview.status == "Scheduled"

    print("Verification SUCCESS!")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
