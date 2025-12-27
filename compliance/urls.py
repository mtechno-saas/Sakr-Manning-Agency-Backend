from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditViewSet, IncidentReportViewSet

router = DefaultRouter()
router.register(r'audits', AuditViewSet, basename='audit')
router.register(r'incidents', IncidentReportViewSet, basename='incident')

urlpatterns = [
    path('', include(router.urls)),
]
