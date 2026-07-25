from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InterviewViewSet, interview_status

router = DefaultRouter()
router.register(r'', InterviewViewSet, basename='interview')

# NOTE: Reminders route moved to its own `reminders` app on 2026-07-25.
# Old: /api/interviews/reminders/  →  New: /api/reminders/

urlpatterns = [
    path('status/', interview_status, name='interview-status'),
    path('', include(router.urls)),
]
