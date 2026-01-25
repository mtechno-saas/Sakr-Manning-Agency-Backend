import os
import io
import django
import sys
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

# 1. Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users, Document
from api.views import DocumentViewSet

def make_document_apply():
    print("--- Starting Quick Apply (via POST /api/documents/) ---")
    
    # 2. Setup Factory and View
    factory = APIRequestFactory()
    view = DocumentViewSet.as_view({'post': 'create'})
    
    # 3. Create a Dummy Admin User to Authenticate the Request
    # The view requires IsAuthenticated. 
    # If this is a public endpoint, the code needs IsAllowAny, but it has IsAuthenticated.
    # We will assume we are testing "from the server" implies we can be an admin acting on behalf of user, 
    # OR testing the functionality assuming we have a token.
    
    admin_email = "admin_check@example.com"
    if not Users.objects.filter(email=admin_email).exists():
        admin_user = Users.objects.create_superuser(admin_email, "pass123")
    else:
        admin_user = Users.objects.get(email=admin_email)
        
    print(f"Authenticated as: {admin_email}")

    # 4. Prepare Data
    applicant_email = "quick_applicant@example.com"
    applicant_name = "Quick Applicant"
    
    # Check cleanup
    if Users.objects.filter(email=applicant_email).exists():
        print(f"Cleaning up previous applicant {applicant_email}...")
        Users.objects.get(email=applicant_email).delete()
        
    # Create a dummy PDF file
    file_content = b"%PDF-1.4 ... dummy content ..."
    file_obj = SimpleUploadedFile("cv.pdf", file_content, content_type="application/pdf")
    
    data = {
        "title": "My CV Application",
        "file": file_obj,
        "name": applicant_name,
        "email": applicant_email,
        "phone_number": "+20123456789",
        "position": "Master",
        # We don't send 'user' field, the view should handle creating it from email
    }
    
    # 5. Make Request
    request = factory.post('/api/documents/', data, format='multipart')
    force_authenticate(request, user=admin_user)
    
    print(f"Sending POST to /api/documents/ with email={applicant_email}...")
    
    try:
        response = view(request)
    except Exception as e:
        print(f"❌ Exception in view: {e}")
        import traceback
        traceback.print_exc()
        return

    # 6. Analyze Result
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")
    
    if response.status_code == 201:
        print("\n✅ Document Uploaded Successfully")
        
        # Verify side effects (User creation)
        if Users.objects.filter(email=applicant_email).exists():
            new_user = Users.objects.get(email=applicant_email)
            print(f"✅ Side Effect: New user created with ID {new_user.id} and Email {new_user.email}")
            print(f"   Role: {new_user.role}")
        else:
             # Check if it linked to admin_user or failed to create
            print("⚠️ User was NOT created from email. Check view logic.")
            if 'user' in response.data:
                print(f"   Document assigned to user_id: {response.data['user']}")

    else:
        print("❌ Upload Failed")

if __name__ == "__main__":
    make_document_apply()
