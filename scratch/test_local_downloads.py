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

def test_anonymous_download():
    client = Client()
    # Find any user or create one for testing
    user = Users.objects.first()
    if not user:
        # Create a temp user with a dummy file
        dummy_file = SimpleUploadedFile("test_passport.pdf", b"pdf content", content_type="application/pdf")
        user = Users.objects.create(
            email="test_temp_download@example.com",
            first_name="Test",
            last_name="Temp",
            passport_attachment=dummy_file
        )
        created = True
        print(f"Created temp user {user.id}")
    else:
        created = False
        # Make sure they have a passport attachment or assign one
        if not user.passport_attachment:
            dummy_file = SimpleUploadedFile("test_passport.pdf", b"pdf content", content_type="application/pdf")
            user.passport_attachment = dummy_file
            user.save()
            print(f"Assigned dummy passport to existing user {user.id}")

    # Build the download URL
    url = f"/api/users/{user.id}/download-document/?type=passport"
    print(f"Requesting URL: {url}")
    
    # Request without any credentials (anonymous)
    response = client.get(url, SERVER_NAME="localhost")
    
    print(f"Response status code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    if response.status_code == 200:
        print("✅ SUCCESS: Anonymous download works!")
    else:
        print(f"❌ FAILURE: Anonymous download failed. Content: {response.content}")

    # Clean up
    if created:
        user.delete()

if __name__ == "__main__":
    test_anonymous_download()
