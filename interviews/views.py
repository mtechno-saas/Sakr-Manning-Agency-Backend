from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import Interview
from api.serializer import InterviewSerializer
from .models import Reminder
from .serializers import ReminderSerializer


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer

    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        """Get interview counts by status"""
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            interviews = Interview.objects.all()
        else:
            # api.models.Interview uses 'candidate' field
            interviews = Interview.objects.filter(candidate=request.user)

        return Response({
            'scheduled': interviews.filter(status='Scheduled').count(),
            'completed': interviews.filter(status='Completed').count(),
            'cancelled': interviews.filter(status='Cancelled').count(),
            'rescheduled': interviews.filter(status='Rescheduled').count(),
            'no_show': interviews.filter(status='No Show').count(),
            'total': interviews.count(),
        })


@api_view(['GET'])
def interview_status(request):
    """Get interview counts by status - standalone endpoint"""
    try:
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            interviews = Interview.objects.all()
        else:
            interviews = Interview.objects.filter(candidate=request.user)

        return Response({
            'scheduled': interviews.filter(status='Scheduled').count(),
            'completed': interviews.filter(status='Completed').count(),
            'cancelled': interviews.filter(status='Cancelled').count(),
            'rescheduled': interviews.filter(status='Rescheduled').count(),
            'no_show': interviews.filter(status='No Show').count(),
            'total': interviews.count(),
        })
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


class ReminderViewSet(viewsets.ModelViewSet):
    """
    CRUD for crew-member reminders.
    - Admin / HR Manager / Recruiter: see all reminders
    - Other users: see only their own (user=request.user)
    """
    queryset = Reminder.objects.all().select_related('user')
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Reminder.objects.all().select_related('user')
        if getattr(user, 'role', None) in ['Admin', 'HR Manager', 'Recruiter']:
            return qs
        return qs.filter(user=user)

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        """Return reminders scheduled for today or later, not yet completed."""
        from django.utils import timezone
        today = timezone.localdate()
        qs = self.get_queryset().filter(
            reminder_date__gte=today,
            is_completed=False,
        ).order_by('reminder_date', 'reminder_time')
        return Response(ReminderSerializer(qs, many=True).data)
