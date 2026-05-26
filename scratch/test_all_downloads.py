import os
import sys
import django

# Setup Django path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from django.test import Client
from api.models import Users, PersonalDocument
from licenses.models import UserLicense
from vaccinations.models import Vaccination
from courses.models import Course
from api.models import SeaService
from django.core.files.uploadedfile import SimpleUploadedFile

def run_tests():
    c = Client()
    # 1. Get or create test user
    user = Users.objects.first()
    if not user:
        user = Users.objects.create(
            email="test_all_downloads@example.com",
            first_name="Test",
            last_name="All"
        )
        user_created = True
    else:
        user_created = False

    # Attach dummy files
    dummy_file = SimpleUploadedFile("dummy.pdf", b"pdf content", content_type="application/pdf")
    
    # Singleton attachments
    user.passport_attachment = dummy_file
    user.seaman_book_attachment = dummy_file
    user.other_seaman_book_attachment = dummy_file
    user.marlins_test_attachment = dummy_file
    user.ces_test_attachment = dummy_file
    user.save()

    # Related attachments
    license_obj = UserLicense.objects.create(user=user, document_name="COC", document_file=dummy_file)
    vaccination_obj = Vaccination.objects.create(user=user, name="Yellow Fever Immunization", document=dummy_file)
    course_obj = Course.objects.create(user=user, course_name="Basic Safety Training", document=dummy_file)
    sea_service_obj = SeaService.objects.create(user=user, vessel_name="Test Vessel", file=dummy_file)
    personal_doc_obj = PersonalDocument.objects.create(user=user, document_type="visa", file=dummy_file)

    endpoints = [
        (f"/api/users/users/{user.id}/download-passport/", "Passport"),
        (f"/api/users/users/{user.id}/download-seaman-book/", "Seaman Book"),
        (f"/api/users/users/{user.id}/download-other-seaman-book/", "Other Seaman Book"),
        (f"/api/users/users/{user.id}/download-marlins/", "Marlins"),
        (f"/api/users/users/{user.id}/download-ces/", "CES"),
        (f"/api/users/users/{user.id}/download-license/{license_obj.id}/", "License"),
        (f"/api/users/users/{user.id}/download-vaccination/{vaccination_obj.id}/", "Vaccination"),
        (f"/api/users/users/{user.id}/download-course/{course_obj.id}/", "Course"),
        (f"/api/users/users/{user.id}/download-sea-service/{sea_service_obj.id}/", "Sea Service"),
        (f"/api/users/users/{user.id}/download-personal-document/{personal_doc_obj.id}/", "Personal Document"),
    ]

    print("Running download endpoint access tests (ANONYMOUS requests):")
    all_success = True
    for url, label in endpoints:
        response = c.get(url, HTTP_HOST='localhost')
        if response.status_code == 200:
            print(f"✅ {label}: SUCCESS (200 OK)")
        else:
            print(f"❌ {label}: FAILED (Status: {response.status_code}, Body: {response.content[:100]})")
            all_success = False

    # Clean up related records
    license_obj.delete()
    vaccination_obj.delete()
    course_obj.delete()
    sea_service_obj.delete()
    personal_doc_obj.delete()

    if user_created:
        user.delete()

    if all_success:
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n🛑 SOME TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
