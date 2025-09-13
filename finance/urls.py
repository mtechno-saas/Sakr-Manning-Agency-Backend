from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinanceRecordViewSet

router = DefaultRouter()
router.register(r'finance-records', FinanceRecordViewSet, basename="finance-record")

urlpatterns = [
    path('', include(router.urls)),
]
