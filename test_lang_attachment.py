import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Users, LanguageProficiency

def run_test():
    # 1. Create a dummy user
    user, created = Users.objects.get_or_create(
        email="test_lang_user@example.com", 
        defaults={"first_name": "Test", "role": "Employee"}
    )
    user.set_password("password123")
    user.save()

    # Allow testserver in ALLOWED_HOSTS for APIClient tests
    from django.conf import settings
    settings.ALLOWED_HOSTS.append('testserver')
    
    try:
        # 2. Setup API Client
        client = APIClient()
        client.force_authenticate(user=user)

        # 3. Create a dummy file
        file_content = b"This is a test language certificate file."
        uploaded_file = SimpleUploadedFile("test_lang_cert.pdf", file_content, content_type="application/pdf")

        # 4. Make POST request to /api/my-languages/
        # Note: We use marks=85 because there is a validation check in LanguageProficiencySerializer 
        # to block 'French', 90, 'B2', 'Advanced' as it's default test data from the frontend.
        data = {
            "language": "French",
            "general_marks": 85,
            "cefr_level": "B2",
            "speaking_level": "Advanced",
            "writing_level": "Intermediate",
            "reading_level": "Advanced",
            "attachment": uploaded_file
        }

        print("Sending POST request to /api/my-languages/ with attachment...")
        response = client.post('/api/my-languages/', data, format='multipart')

        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {getattr(response, 'data', response.content)}")

        if response.status_code == 201:
            print("\nSuccess! The endpoint accepted the request with the file attachment.")
            lang_id = getattr(response, 'data', {}).get('id')
            lang = LanguageProficiency.objects.get(id=lang_id)
            if lang.attachment:
                print(f"Saved attachment file path in DB: {lang.attachment.name}")
                print(f"File size: {lang.attachment.size} bytes")
            else:
                print("Error: The request succeeded but the attachment field is empty in the database.")
        else:
            print("\nFailed to create language proficiency.")

    finally:
        # Cleanup
        print("\nCleaning up dummy user...")
        user.delete()

if __name__ == "__main__":
    run_test()
