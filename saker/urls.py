"""
URL configuration for saker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/contracts-gen/", include("contracts.urls")),
    path("api/users/", include("api.urls")),  # users API
    path("api/tickets-papers/", include("tickets_papers.urls")),  # ✅ tickets & papers API
    path("api/companies/", include("companies.urls")),
    path("api/ships/", include("ships.urls")),
    path("api/expiring-documents/", include("expiring_documents.urls")),  # expiring documents aggregator
    path("api/reminders/", include("reminders.urls")),  # per-user reminders (Interviews section)
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/core/", include("core.urls")),
    path('api/finance/', include('finance.urls')),
    path("ai-agents/", include("ai_agents.urls")),
    path("ai/", include("ai_document.urls")),
    path("api/interviews/", include("interviews.urls")),
    path("api/logistics/", include("logistics.urls")),
    path("api/compliance/", include("compliance.urls")),
    path("api/", include("api.urls")),
    path('api/', include('licenses.urls')),
    path("api/", include("vaccinations.urls")),
    path("api/", include("courses.urls")),
    path("api/reports/", include("reports.urls")),  # Reports page
    path(
        "api/historical-data-for-companies/",
        include("historical_data_companies.urls"),
    ),  # Historical Data for Companies page
]

# ----------------------------------------------------------------------------
# Compat shim: /api/job-orders/  -->  /api/companies/job-orders/
# ----------------------------------------------------------------------------
# The dashboard's job-order create form POSTs to ``/api/job-orders/`` (a
# 404 today), but the canonical URL the router actually serves is
# ``/api/companies/job-orders/`` (see ``companies/urls.py:9``). Rather
# than block on the frontend dev, we mirror the JobOrderViewSet at
# BOTH paths. The shim is basenamed ``job-order-compat`` so the
# reverse-lookup ``reverse('job-order-compat-list')`` is unambiguous.
#
# REMOVE THIS BLOCK once the frontend switches to the canonical URL.
# ----------------------------------------------------------------------------
from companies.routers import TrailingSlashOptionalRouter
from companies.views import JobOrderViewSet

_job_order_compat_router = TrailingSlashOptionalRouter()
_job_order_compat_router.register(
    r'api/job-orders',
    JobOrderViewSet,
    basename='job-order-compat',
)
urlpatterns += _job_order_compat_router.urls

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
