"""
URL configuration for documents app.
"""

from django.urls import path
from .views import DocumentUploadView

urlpatterns = [
    path("upload/", DocumentUploadView.as_view(), name="document-upload"),
]
