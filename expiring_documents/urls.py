"""URL config for the Expiring Documents app."""
from django.urls import path
from . import views

app_name = "expiring_documents"

urlpatterns = [
    # GET  /api/expiring-documents/
    # POST /api/expiring-documents/   (create a new personal document)
    path("", views.ExpiringDocumentsView.as_view(), name="expiring-documents"),

    # PATCH /api/expiring-documents/<item_id>/
    # item_id format:
    #   "user_<user_id>_<expiry_field>"   -> updates the Users field
    #   "pd_<doc_id>"                     -> updates a PersonalDocument row
    path("<str:item_id>/", views.ExpiringDocumentsView.as_view(), name="expiring-documents-detail"),
]
