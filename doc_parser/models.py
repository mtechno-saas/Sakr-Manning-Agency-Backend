
# # doc_parser/models.py
# from django.db import models
# from api.models import Users # Optional: to link to a user

# class ParsedDocument(models.Model):
#     """
#     Stores an uploaded document, its processing status,
#     and the extracted data in structured YAML format.
#     """
#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('PROCESSING', 'Processing'),
#         ('COMPLETED', 'Completed'),
#         ('FAILED', 'Failed'),
#     ]

#     # The original uploaded file
#     source_file = models.FileField(upload_to='source_documents/')

#     # The extracted data, stored as text in YAML format
#     extracted_data_yaml = models.TextField(
#         blank=True,
#         help_text="The structured data extracted from the document, in YAML format."
#     )

#     # Tracking fields
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Optional: Link to the user profile that was created or updated from this doc
#     associated_user = models.ForeignKey(
#         Users,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='parsed_documents'
#     )

#     def __str__(self):
#         return f"Document {self.id} - {self.status}"

# doc_parser/models.py
from django.db import models
from api.models import Users  # Make sure this import is correct

class ParsedDocument(models.Model):
    """
    Stores an uploaded document, its processing status,
    and the extracted data in structured YAML format.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    # The original uploaded file
    source_file = models.FileField(upload_to='source_documents/')

    # The extracted data, stored as text in YAML format
    extracted_data_yaml = models.TextField(
        blank=True,
        help_text="The structured data extracted from the document, in YAML format."
    )

    # Tracking fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to the user profile that was created from this doc
    associated_user = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parsed_documents'
    )

    def __str__(self):
        return f"Document {self.id} - {self.status}"