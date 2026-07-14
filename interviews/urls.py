from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InterviewViewSet, interview_status, ReminderViewSet

router = DefaultRouter()
router.register(r'', InterviewViewSet, basename='interview')
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = [
    path('status/', interview_status, name='interview-status'),
    path('', include(router.urls)),
]
