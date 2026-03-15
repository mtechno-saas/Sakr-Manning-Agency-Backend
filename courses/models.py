from django.db import models
from django.conf import settings

class Course(models.Model):
    # Link to your custom User model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    
    course_name = models.CharField(max_length=255)
    course_number = models.CharField(max_length=100)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issued_by = models.CharField(max_length=255)
    issued_at = models.CharField(max_length=255)
    country_of_issue = models.CharField(max_length=100)
    
    # Drag-and-drop target (File field)
    document = models.FileField(upload_to='course_docs/', null=True, blank=True)

    def __str__(self):
        return f"{self.course_name} ({self.user.email})"