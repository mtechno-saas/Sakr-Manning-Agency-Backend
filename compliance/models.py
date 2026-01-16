from django.db import models
from api.models import Users
from companies.models import Company
from ships.models import Ship

class Audit(models.Model):
    """
    Step 11B: Support MLC, PSC, and ISO audits.
    """
    AUDIT_TYPES = [
        ('MLC', 'MLC 2006'),
        ('ISO', 'ISO 9001'),
        ('PSC', 'Port State Control'),
        ('Internal', 'Internal Audit'),
        ('Client', 'Client Audit'),
    ]
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Passed', 'Passed'),
        ('Authorized with Conditions', 'Authorized with Conditions'),
        ('Failed', 'Failed'),
    ]

    audit_type = models.CharField(max_length=50, choices=AUDIT_TYPES)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    ship = models.ForeignKey(Ship, on_delete=models.SET_NULL, null=True, blank=True)
    
    audit_date = models.DateField()
    auditor_name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, help_text="e.g. DNV, Lloyd's, Flag State")
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Scheduled')
    findings_count = models.PositiveIntegerField(default=0)
    report_file = models.FileField(upload_to='compliance/audits/', null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.audit_type} Audit - {self.audit_date}"


class IncidentReport(models.Model):
    """
    Step 11D: Implement corrective and preventive actions.
    Step 10C: Handle complaints, grievances.
    """
    INCIDENT_TYPES = [
        ('Accident', 'Accident / Injury'),
        ('Near Miss', 'Near Miss'),
        ('Grievance', 'Crew Grievance / Complaint'),
        ('Disciplinary', 'Disciplinary Action'),
        ('Pollution', 'Pollution / Environmental'),
        ('Security', 'Security Breach'),
    ]
    SEVERITY_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    title = models.CharField(max_length=255)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='Low')
    
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    ship = models.ForeignKey(Ship, on_delete=models.SET_NULL, null=True, blank=True)
    
    date_occurred = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    
    description = models.TextField()
    immediate_action_taken = models.TextField(blank=True)
    
    root_cause_analysis = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    preventive_action = models.TextField(blank=True)
    
    is_closed = models.BooleanField(default=False)
    closed_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.incident_type}: {self.title} ({self.date_occurred.date()})"
