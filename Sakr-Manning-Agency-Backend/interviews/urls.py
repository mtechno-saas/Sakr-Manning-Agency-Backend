from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InterviewViewSet, interview_status

router = DefaultRouter()
router.register(r'', InterviewViewSet, basename='interview')

urlpatterns = [
    path('status/', interview_status, name='interview-status'),
    path('', include(router.urls)),
]
