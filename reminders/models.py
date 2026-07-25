"""Reminders model — a reminder tied to a specific user (crew member)."""
from django.conf import settings
from django.db import models


class Reminder(models.Model):
    """
    A reminder for a single user (typically a crew member).

    Shown in the Interviews section of the dashboard. The admin picks
    which user the reminder is for via a dropdown in the form, then
    writes the message, the date, and the time.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text='Crew member (or other user) the reminder is for',
    )
    text = models.TextField(
        help_text='Reminder message / details',
    )
    reminder_date = models.DateField(
        help_text='Date the reminder is for',
    )
    reminder_time = models.TimeField(
        help_text='Time the reminder is for',
    )
    is_completed = models.BooleanField(
        default=False,
        help_text='Mark as done when the user has acted on the reminder',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['reminder_date', 'reminder_time']
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'

    def __str__(self):
        who = getattr(self.user, 'email', None) or f'user#{self.user_id}'
        return f"Reminder for {who} on {self.reminder_date} at {self.reminder_time}"
