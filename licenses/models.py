from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings

def user_license_upload_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/user_<id>/licenses/<filename>
    return f'user_{instance.user.id}/licenses/{filename}'

# Predefined document names
DOCUMENT_NAME_CHOICES = [
    ("Master (Reg. II/2 Par. 1-2)", "Master (Reg. II/2 Par. 1-2)"),
    ("Master (Reg. II/2 Par. 1-2) Endorsement", "Master (Reg. II/2 Par. 1-2) Endorsement"),
    ("Master <3,000 GRT (Reg. II/2 Par. 3-4)", "Master <3,000 GRT (Reg. II/2 Par. 3-4)"),
    ("Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement", "Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement"),
    ("Master <500 GRT (Reg. II/3 Par. 5-6)", "Master <500 GRT (Reg. II/3 Par. 5-6)"),
    ("Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement", "Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement"),
    ("Yachtmaster Coastal", "Yachtmaster Coastal"),
    ("Chief Officer (Reg. II/2 Par. 1-2)", "Chief Officer (Reg. II/2 Par. 1-2)"),
    ("Chief Officer (Reg. II/2 Par. 1-2) Endorsement", "Chief Officer (Reg. II/2 Par. 1-2) Endorsement"),
    ("Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4)", "Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4)"),
    ("Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement", "Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement"),
    ("Navigational Watch Officer (Reg. II/1)", "Navigational Watch Officer (Reg. II/1)"),
    ("Navigational Watch Officer (Reg. II/1) Endorsement", "Navigational Watch Officer (Reg. II/1) Endorsement"),
    ("Navigational Watch Officer <500 GRT (II/3 Par. 3-4)", "Navigational Watch Officer <500 GRT (II/3 Par. 3-4)"),
    ("Chief Engineer (Reg. III/2)", "Chief Engineer (Reg. III/2)"),
    ("Chief Engineer (Reg. III/2) Endorsement", "Chief Engineer (Reg. III/2) Endorsement"),
    ("Chief Engineer – Steam (Reg. III/2)", "Chief Engineer – Steam (Reg. III/2)"),
    ("Chief Engineer – Steam (Reg. III/2) Endorsement", "Chief Engineer – Steam (Reg. III/2) Endorsement"),
    ("Chief Engineer <3,000 KW (Reg. III/3)", "Chief Engineer <3,000 KW (Reg. III/3)"),
    ("2nd Engineer (Reg. III/2)", "2nd Engineer (Reg. III/2)"),
    ("2nd Engineer (Reg. III/2) Endorsement", "2nd Engineer (Reg. III/2) Endorsement"),
    ("2nd Engineer – Steam (Reg. III/3)", "2nd Engineer – Steam (Reg. III/3)"),
    ("2nd Engineer – Steam (Reg. III/3) Endorsement", "2nd Engineer – Steam (Reg. III/3) Endorsement"),
    ("2nd Engineer <3,000 KW (Reg. III/3)", "2nd Engineer <3,000 KW (Reg. III/3)"),
    ("Engineering Watch Officer (Reg. III/1)", "Engineering Watch Officer (Reg. III/1)"),
    ("Engineering Watch Officer (Reg. III/1) Endorsement", "Engineering Watch Officer (Reg. III/1) Endorsement"),
    ("Electro Technical Officer (Reg. III/6)", "Electro Technical Officer (Reg. III/6)"),
    ("Electro Technical Officer (Reg. III/6) Endorsement", "Electro Technical Officer (Reg. III/6) Endorsement"),
    ("Electro Technical Rating (Reg. III/7)", "Electro Technical Rating (Reg. III/7)"),
    ("Able Seaman Deck (Reg. II/5)", "Able Seaman Deck (Reg. II/5)"),
    ("Able Seaman Deck (Reg. II/5) Endorsement", "Able Seaman Deck (Reg. II/5) Endorsement"),
    ("Able Seaman Engine (Reg. III/5)", "Able Seaman Engine (Reg. III/5)"),
    ("Able Seaman Engine (Reg. III/5) Endorsement", "Able Seaman Engine (Reg. III/5) Endorsement"),
    ("Qualified Steward/Messman Endorsement", "Qualified Steward/Messman Endorsement"),
    ("GMDSS Radio Operator (Reg. IV/2)", "GMDSS Radio Operator (Reg. IV/2)"),
    ("GMDSS Radio Operator (Reg. IV/2) Endorsement", "GMDSS Radio Operator (Reg. IV/2) Endorsement"),
    ("GMDSS Endorsement (Reg. IV/2) Flag CRA", "GMDSS Endorsement (Reg. IV/2) Flag CRA"),
    ("GMDSS Restricted Operator (ROC) (Reg. IV/2)", "GMDSS Restricted Operator (ROC) (Reg. IV/2)"),
    ("GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement", "GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement"),
    ("GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA", "GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA"),
    ("Qualified Ship’s Cook (MLC 2006)", "Qualified Ship’s Cook (MLC 2006)"),
    ("Qualified Ship’s Cook (MLC 2006) Endorsement", "Qualified Ship’s Cook (MLC 2006) Endorsement"),
    ("Navigational Watch Rating (Reg. II/4)", "Navigational Watch Rating (Reg. II/4)"),
    ("Navigational Watch Rating (Reg. II/4) Endorsement", "Navigational Watch Rating (Reg. II/4) Endorsement"),
    ("COC – Certificate of Competency", "COC – Certificate of Competency"),
    ("COC – Certificate of Competency Endorsement", "COC – Certificate of Competency Endorsement"),
    ("GOC – General Operator Certificate", "GOC – General Operator Certificate"),
    ("GOC – General Operator Certificate Endorsement", "GOC – General Operator Certificate Endorsement"),
]

class UserLicense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='licenses'
    )
    document_name = models.CharField(
        max_length=255,
        choices=DOCUMENT_NAME_CHOICES
    )
    document_number = models.CharField(max_length=100)
    country_of_issue = models.CharField(max_length=100)
    issue_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    
    # PDF Upload Field
    document_file = models.FileField(
        upload_to=user_license_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        null=True, 
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expiration_date']

    def __str__(self):
        return f"{self.document_name} ({self.document_number}) - {self.user.email}"
