from django.db import models
from api.models import Users

class Interview(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Pending Confirmation', 'Pending Confirmation'),
        ('Cancelled', 'Cancelled'),
    ]

    INTERVIEW_TYPE_CHOICES = [
        ('Phone', 'Phone'),
        ('Video', 'Video'),
        ('In-Person', 'In-Person'),
    ]

    RESULT_CHOICES = [
        ('Pending', 'Pending'),
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('Hold', 'Hold'),
    ]

    candidate = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='interviews_as_candidate')
    interviewer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='interviews_as_interviewer')
    principal = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interviews',
        help_text='Company doing the hiring',
    )
    position = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES, blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Confirmation')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Interview with {self.candidate} on {self.date}"


# NOTE: The Reminder model was moved to its own `reminders` app on 2026-07-25.
# The data still lives in the `interviews_reminder` table — left intact in
# case any production records need to be migrated manually. The
# `reminders.Reminder` model uses a fresh `reminders_reminder` table.
