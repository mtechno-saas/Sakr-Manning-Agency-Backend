from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

VACCINE_CHOICES = [
    ("Quarantine Letter", "Quarantine Letter"),
    ("Rubella Immunity", "Rubella Immunity"),
    ("Tessera Sanitaria", "Tessera Sanitaria"),
    ("Tuberculosis Laboratory Screen", "Tuberculosis Laboratory Screen"),
    ("Typhoid Vaccination", "Typhoid Vaccination"),
    ("Varicella Immunization", "Varicella Immunization"),
    ("Yellow Fever Immunization", "Yellow Fever Immunization"),
    ("Chickenpox Immunity Screening", "Chickenpox Immunity Screening"),
    ("Color Vision Certificate", "Color Vision Certificate"),
    ("Covid-Sars Vaccination", "Covid-Sars Vaccination"),
    ("Covid Form", "Covid Form"),
    ("Foodhandler Exams", "Foodhandler Exams"),
    ("Health Questionnaire", "Health Questionnaire"),
    ("Hepatitis A Immunization", "Hepatitis A Immunization"),
    ("Hepatitis B Immunization", "Hepatitis B Immunization"),
    ("Italian Medical Pre-Embark Examination", "Italian Medical Pre-Embark Examination"),
    ("Measles Immunity", "Measles Immunity"),
    ("Medical Certificate For Seafarers", "Medical Certificate For Seafarers"),
    ("Mmr Booster 2", "Mmr Booster 2"),
    ("Mmr Vaccination / Immunization", "Mmr Vaccination / Immunization"),
    ("Mumps Immunity", "Mumps Immunity"),
    ("Pertussis Immunization", "Pertussis Immunization"),
]

class Vaccination(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vaccinations"
    )

    name = models.CharField(max_length=100, choices=VACCINE_CHOICES)
    number = models.CharField(max_length=200, blank=True, null=True)

    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    issued_by = models.CharField(max_length=255, blank=True, null=True)
    issued_at = models.CharField(max_length=255, blank=True, null=True)

    disease = models.CharField(max_length=255, blank=True, null=True)

    first_date = models.DateField(blank=True, null=True)
    last_date = models.DateField(blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)

    document = models.FileField(
        upload_to="vaccinations/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.issue_date and self.expiry_date:
            if self.expiry_date < self.issue_date:
                raise ValidationError("Expiry date cannot be before issue date.")

        if self.first_date and self.last_date:
            if self.last_date < self.first_date:
                raise ValidationError("Last date cannot be before first date.")

    def __str__(self):
        return f"{self.user} - {self.name}"
    