from django.urls import path, re_path
from .routers import TrailingSlashOptionalRouter
from .views import CompanyViewSet, JobOrderViewSet, JobOrderPositionViewSet

# Use the trailing-slash-optional router so that POST / PUT / PATCH / DELETE
# requests without a trailing slash don't hit Django's APPEND_SLASH
# RuntimeError. See companies/routers.py for details.
router = TrailingSlashOptionalRouter()
router.register(r'job-orders', JobOrderViewSet, basename='job-order')
router.register(r'job-positions', JobOrderPositionViewSet, basename='job-position')
router.register(r'', CompanyViewSet, basename='company')

# Define custom action URLs first, then append router URLs
# The order matters: more specific patterns must come before generic ones
urlpatterns = [
    # Custom stats endpoint - must be before router patterns
    re_path(r'^stats/$', CompanyViewSet.as_view({'get': 'stats'}), name='company-stats'),
]

# Add router URLs after our custom ones. Because we use the optional-slash
# router, every router URL is also available without a trailing slash.
urlpatterns += router.urls
