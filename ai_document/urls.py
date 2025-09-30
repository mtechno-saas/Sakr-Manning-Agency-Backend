# """
# URL configuration for documents app.
# """

# from django.urls import path
# from .views import DocumentUploadView

# urlpatterns = [
#     path("upload/", DocumentUploadView.as_view(), name="document-upload"),
# ]



"""
URL configuration for documents app.
"""

# from django.urls import path
# from .views import DocumentUploadView, IntegratedDocumentUploadView

# urlpatterns = [
#     path("upload/", DocumentUploadView.as_view(), name="document-upload"),
#     path("integrated-upload/", IntegratedDocumentUploadView.as_view(), name="integrated-document-upload"),
#     path("sync-status/<int:applicant_id>/", IntegratedDocumentUploadView.as_view(), name="sync-status"),
# ]












from django.urls import path
from .views import DirectUsersUploadView

urlpatterns = [
    path("upload/", DirectUsersUploadView.as_view(), name="direct-users-upload"),
]














"""
1. upload/ - Original Document Upload


  path("upload/", DocumentUploadView.as_view(), name="document-upload")
Purpose: Basic document upload and processing
View: DocumentUploadView
What it does:
Accepts document uploads (PDF, images, etc.)
Processes documents using AI to extract data
Saves extracted data only to the Applicant model in ai_document app
Returns processed JSON data
Use case: When you only need to store data in the ai_document app




2. integrated-upload/ - Integrated Document Upload

  path("integrated-upload/", IntegratedDocumentUploadView.as_view(), name="integrated-document-upload")
Purpose: Enhanced document upload with cross-app data saving
View: IntegratedDocumentUploadView
What it does:
Accepts document uploads (same as above)
Processes documents using AI to extract data
Saves data to both Applicant model (ai_document app) AND Users model (api app)
Uses DataMapperService to map data between different model structures
Handles database transactions to ensure data consistency
Returns success/error status for both saves
Use case: When you need the extracted data available in both applications







3. sync-status/<int:applicant_id>/ - Check Sync Status
python
Copy
path("sync-status/<int:applicant_id>/", IntegratedDocumentUploadView.as_view(), name="sync-status")
Purpose: Check if an applicant's data was successfully synced to the Users model
View: IntegratedDocumentUploadView (handles GET requests differently)
URL Parameter: applicant_id - the ID of the applicant to check
What it does:
Takes an applicant ID from the URL
Checks if corresponding user exists in the api app's Users model
Returns sync status (synced/not synced) and any relevant details
Use case: Verify data synchronization between the two apps
Example Usage:
Upload to both apps:

POST /ai_document/integrated-upload/
Content-Type: multipart/form-data
[document file]
Check sync status:

GET /ai_document/sync-status/123/
Response: {"synced": true, "user_id": 456, "sync_date": "2024-01-01T10:00:00Z"}

The integrated approach ensures your document data is available in both the ai_document app (for document processing workflows) and the api app (for general user management).
"""