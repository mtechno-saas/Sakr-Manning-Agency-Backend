import os
import sys
import django

# Setup Django path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from django.test import Client
from api.models import Users
from django.core.files.uploadedfile import SimpleUploadedFile
from api.serializer import UsersSerializer

def test_serialized_urls():
    # Find any user or create one for testing
    user = Users.objects.first()
    if not user:
        user = Users.objects.create(
            email="test_temp_attachments@example.com",
            first_name="Test",
            last_name="Temp"
        )
        created = True
    else:
        created = False

    # Attach dummy files
    dummy_marlins = SimpleUploadedFile("marlins.pdf", b"pdf content", content_type="application/pdf")
    dummy_ces = SimpleUploadedFile("ces.pdf", b"pdf content", content_type="application/pdf")
    user.marlins_test_attachment = dummy_marlins
    user.ces_test_attachment = dummy_ces
    user.save()

    # Retrieve serializer representation
    serializer = UsersSerializer(user)
    data = serializer.data

    print(f"Marlins attachment URL: {data.get('marlins_test_attachment')}")
    print(f"CES attachment URL: {data.get('ces_test_attachment')}")

    marlins_url = data.get('marlins_test_attachment')
    ces_url = data.get('ces_test_attachment')

    if marlins_url and "/download-document/?type=marlins" in marlins_url:
        print("✅ SUCCESS: Marlins attachment correctly rewritten!")
    else:
        print("❌ FAILURE: Marlins attachment NOT rewritten!")

    if ces_url and "/download-document/?type=ces" in ces_url:
        print("✅ SUCCESS: CES attachment correctly rewritten!")
    else:
        print("❌ FAILURE: CES attachment NOT rewritten!")

    # Clean up
    if created:
        user.delete()

if __name__ == "__main__":
    test_serialized_urls()
