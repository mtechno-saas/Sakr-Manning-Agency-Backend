# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlagViewSet, VesselTypeViewSet, CompanyTypeViewSet

# Create a router to automatically generate the URLs for our ViewSets
router = DefaultRouter()

# Register the ViewSets with the router
router.register(r'flags', FlagViewSet, basename='flag')
router.register(r'vessel-types', VesselTypeViewSet, basename='vessel-type')
router.register(r'company-types', CompanyTypeViewSet, basename='company-type')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
