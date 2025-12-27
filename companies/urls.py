from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, JobOrderViewSet, JobOrderPositionViewSet

router = DefaultRouter()
router.register(r'job-orders', JobOrderViewSet, basename='job-order')
router.register(r'job-positions', JobOrderPositionViewSet, basename='job-position')
router.register(r'', CompanyViewSet, basename='company')

# Define custom action URLs first, then append router URLs
# The order matters: more specific patterns must come before generic ones
urlpatterns = [
    # Custom stats endpoint - must be before router patterns
    re_path(r'^stats/$', CompanyViewSet.as_view({'get': 'stats'}), name='company-stats'),
]

# Add router URLs after our custom ones
urlpatterns += router.urls
