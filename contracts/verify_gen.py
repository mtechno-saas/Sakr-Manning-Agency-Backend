import os
import django
from datetime import date
import sys

# Setup Django
sys.path.append('/media/storm/New Volume/1-TECHNO SQUARE/SAKR PROJECT')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from contracts.schemas import ContractData
from contracts.utils import fill_contract
from django.conf import settings

def test_fill():
    data = ContractData(
        full_name="John Doe",
        date_of_birth=date(1990, 1, 1),
        marital_status="Single",
        nationality="Testland",
        height_cm=180,
        weight_kg=75,
        place_of_birth="City X",
        shirt_size="L",
        trouser_size="32",
        shoe_size="42",
        education="Test University",
        english_fluency="Fluent",
        address="123 Test St",
        email="john@example.com",
        phone_number="+123456789",
        passport_number="A1234567",
        passport_issue_date=date(2020, 1, 1),
        passport_expiry_date=date(2030, 1, 1),
        passport_issued_by="Authority X",
        seaman_book_number="SB987654",
        seaman_book_issue_date=date(2021, 1, 1),
        seaman_book_expiry_date=date(2031, 1, 1),
        seaman_book_issued_by="Authority Y",
        next_of_kin_name="Jane Doe",
        next_of_kin_relationship="Wife",
        next_of_kin_address="123 Test St",
        next_of_kin_phone="+987654321"
    )
    
    template_path = os.path.join(settings.BASE_DIR, "contracts", "contract", "A NEW APPLICATION - Copy (5).docx")
    output_path = "test_contract.docx"
    
    print(f"Generating contract from {template_path} to {output_path}...")
    try:
        fill_contract(template_path, output_path, data)
        print("Success! User fields mapped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fill()
