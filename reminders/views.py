"""Views for the Reminders app — full CRUD with role-based scoping."""
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Reminder
from .serializers import ReminderSerializer


class ReminderViewSet(viewsets.ModelViewSet):
    """
    CRUD for per-user reminders.

    Role-based scoping
    -----------------
    - **Admin / HR Manager / Recruiter**: see and manage every reminder
    - **Any other authenticated user**: sees and manages only their own
      (`user == request.user`). To create a reminder for someone else,
      the user must be Admin/HR/Recruiter.

    Custom actions
    --------------
    - `GET /api/reminders/upcoming/` — reminders for today or later, not yet completed,
      ordered by date+time
    - `GET /api/reminders/overdue/` — past-due, not yet completed
    - `POST /api/reminders/{id}/mark_done/` — flip `is_completed` to True
    """

    queryset = Reminder.objects.select_related('user').all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Admin/HR/Recruiter see all; everyone else sees only their own."""
        user = self.request.user
        qs = Reminder.objects.select_related('user').all()
        privileged = getattr(user, 'role', None) in ('Admin', 'HR Manager', 'Recruiter')
        if not privileged:
            qs = qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        """
        Save with the user set to the request user.
        Privileged users can pick any user; non-privileged are forced to
        create for themselves (defensive — the URL/serializer is the
        primary gate).
        """
        user = self.request.user
        privileged = getattr(user, 'role', None) in ('Admin', 'HR Manager', 'Recruiter')
        if privileged and 'user' in serializer.validated_data:
            # Admin picks a crew member
            serializer.save()
        else:
            # Force ownership = self
            serializer.save(user=user)

    # ----------------------------------------------------------------
    # Custom actions
    # ----------------------------------------------------------------

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        """
        Return reminders scheduled for today or later, not yet completed.
        Ordered by date ASC, time ASC.
        """
        today = timezone.localdate()
        qs = self.get_queryset().filter(
            reminder_date__gte=today,
            is_completed=False,
        ).order_by('reminder_date', 'reminder_time')
        return Response(ReminderSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """
        Return past-due, not-yet-completed reminders.
        Ordered by date DESC (most overdue first), time DESC.
        """
        today = timezone.localdate()
        qs = self.get_queryset().filter(
            reminder_date__lt=today,
            is_completed=False,
        ).order_by('-reminder_date', '-reminder_time')
        return Response(ReminderSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='mark_done')
    def mark_done(self, request, pk=None):
        """
        Quick action: flip `is_completed` to True for this reminder.
        Returns the updated reminder.
        """
        reminder = self.get_object()
        reminder.is_completed = True
        reminder.save(update_fields=['is_completed', 'updated_at'])
        return Response(ReminderSerializer(reminder).data)

    @action(detail=True, methods=['post'], url_path='mark_pending')
    def mark_pending(self, request, pk=None):
        """
        Quick action: flip `is_completed` back to False.
        Useful when a user dismissed a reminder by mistake.
        """
        reminder = self.get_object()
        reminder.is_completed = False
        reminder.save(update_fields=['is_completed', 'updated_at'])
        return Response(ReminderSerializer(reminder).data)
