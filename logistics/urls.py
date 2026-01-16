from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightBookingViewSet, VisaApplicationViewSet, JoiningInstructionViewSet

router = DefaultRouter()
router.register(r'flights', FlightBookingViewSet, basename='flight')
router.register(r'visas', VisaApplicationViewSet, basename='visa')
router.register(r'joining-instructions', JoiningInstructionViewSet, basename='joining-instruction')

urlpatterns = [
    path('', include(router.urls)),
]
