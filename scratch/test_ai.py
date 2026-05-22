import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from ai_document.document_to_json import convert_text_to_json

test_text = """
CURRICULUM VITAE
Name: MOHAMED ALI HASSAN ELDIB
Rank: Chief Engineer
Nationality: Egyptian
Date of Birth: 29/01/1968
Passport: A12345678
Seaman Book: S87654321
Vessel: MT SAKR 1
IMO: 9123456
Rank: Chief Engineer
Sign on: 01-01-2023
Sign off: 01-06-2023
Company: Sakr Shipping
Keywords: passport, seaman, rank, vessel, ship, marine, maritime, stcw, certificate
"""

print("Starting conversion...")
try:
    result = convert_text_to_json(test_text)
    print("Result keys:", result.keys())
    if "error" in result:
        print("Error found in result:", result["error"])
except Exception as e:
    print("Exception occurred:", str(e))
