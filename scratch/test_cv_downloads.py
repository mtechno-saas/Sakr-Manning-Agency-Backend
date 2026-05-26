import os
import sys
import django

# Setup Django path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from django.test import Client
from api.models import Users, CVSubmission
from django.core.files.uploadedfile import SimpleUploadedFile

def run_tests():
    c = Client()
    # Get or create test user
    user = Users.objects.first()
    if not user:
        user = Users.objects.create(
            email="test_cv_downloads@example.com",
            first_name="Test",
            last_name="All"
        )
        user_created = True
    else:
        user_created = False

    # Attach dummy CV submission
    dummy_file = SimpleUploadedFile("dummy_cv.pdf", b"pdf content", content_type="application/pdf")
    cv_sub = CVSubmission.objects.create(
        user=user,
        cv_file=dummy_file,
        status='Pending'
    )

    url = f"/api/cv-submissions/{cv_sub.id}/download-cv/"
    print(f"Testing GET {url} (ANONYMOUS)...")
    response = c.get(url, HTTP_HOST='localhost')
    if response.status_code == 200:
        print("✅ CV Download Endpoint: SUCCESS (200 OK)")
    else:
        print(f"❌ CV Download Endpoint: FAILED (Status: {response.status_code}, Body: {response.content[:100]})")

    # Verify serializer to_representation includes the absolute path
    from api.serializer import CVSubmissionSerializer
    from django.test.client import RequestFactory
    factory = RequestFactory()
    request = factory.get('/', HTTP_HOST='localhost')
    serializer = CVSubmissionSerializer(cv_sub, context={'request': request})
    data = serializer.data
    cv_file_url = data.get('cv_file')
    print(f"Serialized cv_file URL: {cv_file_url}")
    if cv_file_url and cv_file_url.startswith("http://localhost/api/cv-submissions/"):
        print("✅ CV File URL Serialization: SUCCESS (Absolute URI is correct)")
    else:
        print(f"❌ CV File URL Serialization: FAILED (Got: {cv_file_url})")

    # Clean up
    cv_sub.delete()
    if user_created:
        user.delete()

if __name__ == "__main__":
    run_tests()
