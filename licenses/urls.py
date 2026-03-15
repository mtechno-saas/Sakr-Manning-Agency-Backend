from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserLicenseViewSet

router = DefaultRouter()
router.register(r'my-licenses', UserLicenseViewSet, basename='user-license')

urlpatterns = [
    path('', include(router.urls)),
]