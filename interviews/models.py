from django.db import models
from api.models import Users

class Interview(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Pending Confirmation', 'Pending Confirmation'),
        ('Cancelled', 'Cancelled'),
    ]

    candidate = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='interviews_as_candidate')
    interviewer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='interviews_as_interviewer')
    date = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Confirmation')
    notes = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Interview with {self.candidate} on {self.date}"


class Reminder(models.Model):
    """
    A reminder tied to a crew member (user).
    Shown in the Interviews section of the dashboard for the assigned user.
    """
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text='Crew member the reminder is for',
    )
    text = models.TextField(help_text='Reminder details / message body')
    reminder_date = models.DateField()
    reminder_time = models.TimeField()
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['reminder_date', 'reminder_time']

    def __str__(self):
        return f"Reminder for {self.user} on {self.reminder_date} at {self.reminder_time}"
