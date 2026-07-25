"""URL config for the Expiring Documents app."""
from django.urls import path
from . import views

app_name = "expiring_documents"

urlpatterns = [
    # GET /api/expiring-documents/
    # GET /api/expiring-documents/?days=60
    # GET /api/expiring-documents/?category=critical
    path("", views.expiring_documents, name="expiring-documents"),
]
