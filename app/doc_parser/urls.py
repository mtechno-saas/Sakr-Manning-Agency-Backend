# doc_parser/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentUploadViewSet

router = DefaultRouter()
router.register(r'upload', DocumentUploadViewSet, basename='document-upload')

urlpatterns = [
    path('', include(router.urls)),
]
