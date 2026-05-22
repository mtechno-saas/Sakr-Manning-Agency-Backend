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
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
