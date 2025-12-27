
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users, Contract, Rank
from companies.models import Company, JobOrder, JobOrderPosition
from ships.models import Ship
from logistics.models import FlightBooking, VisaApplication, JoiningInstruction
from compliance.models import Audit, IncidentReport

def verify():
    print("--- Verifying Workflow Implementation ---")

    # 1. Client & Job Order
    print("\n1. Creating Client & Job Order...")
    company, _ = Company.objects.get_or_create(company_name="Test Shipping Co", defaults={'company_type': 'Ship Owner', 'contact_email': 'test@shipping.com'})
    ship, _ = Ship.objects.get_or_create(ship_name="MV Test Vessel", company=company, defaults={'imo_number': '1234567'})
    
    # Needs a rank
    rank, _ = Rank.objects.get_or_create(code="MST-001", defaults={'name': 'Master'})

    job_order = JobOrder.objects.create(
        company=company,
        ship=ship,
        reference_number=f"JO-VERIFY-{date.today()}",
        request_date=date.today(),
        target_joining_date=date.today(),
        status='Open'
    )
    print(f"✅ Job Order Created: {job_order}")

    job_pos = JobOrderPosition.objects.create(job_order=job_order, rank=rank, quantity=2)
    print(f"✅ Job Order Position Created: {job_pos}")

    # 2. Recruitment (User)
    print("\n2. Creating Candidate...")
    user, _ = Users.objects.get_or_create(email="captain.test@example.com", defaults={
        'first_name': 'Captain', 
        'middle_name': 'Test',
        'is_blacklisted': False
    })
    print(f"✅ User Verified: {user}")

    # 3. Contract
    print("\n3. Creating Contract...")
    contract = Contract.objects.create(
        user=user,
        ship=ship,
        rank=rank,
        sign_on_date=date.today(),
        status='Pending Signature',
        repatriation_terms="Standard Repatriation"
    )
    print(f"✅ Contract Created: {contract}")

    # 4. Logistics
    print("\n4. Creating Logistics...")
    visa = VisaApplication.objects.create(
        user=user,
        contract=contract,
        country="USA",
        visa_type="US C1/D",
        status="Documents Collected"
    )
    print(f"✅ Visa Application Created: {visa}")
    
    flight = FlightBooking.objects.create(
        user=user,
        contract=contract,
        airline="Emirates",
        flight_number="EK123",
        departure_airport="DXB",
        arrival_airport="JFK",
        departure_time="2024-01-01 10:00:00",
        arrival_time="2024-01-01 20:00:00"
    )
    print(f"✅ Flight Booking Created: {flight}")

    # 5. Compliance
    print("\n5. Creating Compliance Records...")
    audit = Audit.objects.create(
        audit_type='MLC',
        audit_date=date.today(),
        auditor_name="John Auditor",
        organization="DNV",
        status="Passed"
    )
    print(f"✅ Audit Created: {audit}")

    print("\n--- Verification Complete: All Systems Go ---")

if __name__ == '__main__':
    try:
        verify()
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()
