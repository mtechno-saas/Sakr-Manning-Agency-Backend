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
