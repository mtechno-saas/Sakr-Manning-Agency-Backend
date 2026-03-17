from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

VACCINE_CHOICES = [
    ("QUARANTINE LETTER", "QUARANTINE LETTER"),
    ("RUBELLA IMMUNITY", "RUBELLA IMMUNITY"),
    ("TESSERA SANITARIA", "TESSERA SANITARIA"),
    ("TUBERCULOSIS_LAB_SCREEN", "Tuberculosis Laboratory Screen"),
    ("TYPHOID_VACCINATION", "Typhoid Vaccination"),
    ("VARICELLA_IMMUNIZATION", "Varicella Immunization"),
    ("YELLOW_FEVER_IMMUNIZATION", "Yellow Fever Immunization"),
    ("CHICKENPOX_IMMUNITY_SCREENING", "Chickenpox Immunity Screening"),
    ("COLOR_VISION_CERTIFICATE", "Color Vision Certificate"),
    ("COVID_SARS_VACCINATION", "COVID-SARS Vaccination"),
    ("COVID_FORM", "COVID Form"),
    ("FOODHANDLER_EXAMS", "Foodhandler Exams"),
    ("HEALTH_QUESTIONNAIRE", "Health Questionnaire"),
    ("HEPATITIS_A_IMMUNIZATION", "Hepatitis A Immunization"),
    ("HEPATITIS_B_IMMUNIZATION", "Hepatitis B Immunization"),
    ("ITALIAN_MEDICAL_PRE_EMBARK", "Italian Medical Pre-Embark Examination"),
    ("MEASLES_IMMUNITY", "Measles Immunity"),
    ("MEDICAL_CERT_SEAFARERS", "Medical Certificate for Seafarers"),
    ("MMR_BOOSTER_2", "MMR Booster 2"),
    ("MMR_VACC_IMMUNIZATION", "MMR Vaccination / Immunization"),
    ("MUMPS_IMMUNITY", "Mumps Immunity"),
    ("PERTUSSIS_IMMUNIZATION", "Pertussis Immunization"),
]

class Vaccination(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vaccinations"
    )

    name = models.CharField(max_length=50, choices=VACCINE_CHOICES)
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
        validators=[FileExtensionValidator(["pdf"])]
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
    