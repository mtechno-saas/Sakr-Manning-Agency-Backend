# from django.conf import settings
# from django.db import models

# # Create your models here.
# """
# Django models for document management system.
# Handles DOCX and PDF file storage and metadata.
# """

# from django.db import models
# from django.core.validators import FileExtensionValidator
# import os



# class Applicant(models.Model):
#     personal_details = models.JSONField(default=dict, blank=True, null=True)
#     education = models.JSONField(default=dict, blank=True, null=True)
#     contact_details = models.JSONField(default=dict, blank=True, null=True)
#     travel_documents = models.JSONField(default=dict, blank=True, null=True)
#     professional_qualifications = models.JSONField(default=dict, blank=True, null=True)
#     next_of_kin_emergency_contact = models.JSONField(default=dict, blank=True, null=True)
#     health_certificates_vaccinations = models.JSONField(default=dict, blank=True, null=True)
#     covid_19_vaccination = models.JSONField(default=dict, blank=True, null=True)
#     marine_courses = models.JSONField(default=dict, blank=True, null=True)
#     sea_service_details = models.JSONField(default=dict, blank=True, null=True)
#     specialised_experience = models.JSONField(default=dict, blank=True, null=True)
#     references = models.JSONField(default=dict, blank=True, null=True)
#     declaration = models.JSONField(default=dict, blank=True, null=True)
#     office_use_only = models.JSONField(default=dict, blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Applicant {self.id}"


# def document_upload_path(instance, filename):
#     """
#     Generate upload path for documents.
#     Files will be uploaded to MEDIA_ROOT/documents/year/month/day/filename
#     """
#     from datetime import datetime
#     now = datetime.now()
#     return f'documents/{now.year}/{now.month:02d}/{now.day:02d}/{filename}'


# class Document(models.Model):
#     """
#     Model to store document files (DOCX and PDF) with metadata.
#     """
#     DOCUMENT_TYPES = [
#         ('pdf', 'PDF Document'),
#         ('docx', 'Word Document'),
#     ]
    
#     STATUS_CHOICES = [
#         ('pending', 'Pending Processing'),
#         ('processing', 'Processing'),
#         ('completed', 'Processing Completed'),
#         ('failed', 'Processing Failed'),
#     ]
    
#     title = models.CharField(
#         max_length=255,
#         help_text="Document title or name"
#     )
    
#     description = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Optional description of the document"
#     )
    
#     file = models.FileField(
#         upload_to=document_upload_path,
#         validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
#         help_text="Upload PDF or DOCX file"
#     )
    
#     document_type = models.CharField(
#         max_length=10,
#         choices=DOCUMENT_TYPES,
#         help_text="Type of document based on file extension"
#     )
    
#     file_size = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="File size in bytes"
#     )
    
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending',
#         help_text="Processing status of the document"
#     )
    
#     extracted_text = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Text content extracted from the document"
#     )
    
#     page_count = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Number of pages in the document"
#     )
    
#     word_count = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Number of words in the document"
#     )
    
#     processing_error = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Error message if processing failed"
#     )
    
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="Timestamp when document was uploaded"
#     )
    
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         help_text="Timestamp when document was last updated"
#     )
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Document"
#         verbose_name_plural = "Documents"
    
#     def __str__(self):
#         return f"{self.title} ({self.document_type.upper()})"
    
#     def save(self, *args, **kwargs):
#         """
#         Override save method to automatically set document type and file size.
#         """
#         if self.file:
#             # Set document type based on file extension
#             file_extension = os.path.splitext(self.file.name)[1].lower()
#             if file_extension == '.pdf':
#                 self.document_type = 'pdf'
#             elif file_extension == '.docx':
#                 self.document_type = 'docx'
            
#             # Set file size
#             if hasattr(self.file, 'size'):
#                 self.file_size = self.file.size
        
#         super().save(*args, **kwargs)
    
#     @property
#     def file_size_mb(self):
#         """
#         Return file size in megabytes.
#         """
#         if self.file_size:
#             return round(self.file_size / (1024 * 1024), 2)
#         return None
    
#     @property
#     def is_processed(self):
#         """
#         Check if document has been successfully processed.
#         """
#         return self.status == 'completed'
    
#     def get_file_extension(self):
#         """
#         Get the file extension.
#         """
#         if self.file:
#             return os.path.splitext(self.file.name)[1].lower()
#         return None



# # Import logging models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from django.db.models import F
# import json


# class APIResponseLog(models.Model):
#     """
#     Model to log API responses with seafarer profile tracking.
#     """
    
#     # Request information
#     endpoint = models.CharField(
#         max_length=255,
#         help_text="API endpoint path"
#     )
    
#     method = models.CharField(
#         max_length=10,
#         help_text="HTTP method (GET, POST, etc.)"
#     )
    
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,   # ✅ instead of auth.User
#         on_delete=models.CASCADE
#     )
    
#     ip_address = models.GenericIPAddressField(
#         null=True,
#         blank=True,
#         help_text="Client IP address"
#     )
    
#     user_agent = models.TextField(
#         blank=True,
#         help_text="User agent string"
#     )
    
#     # Response information
#     status_code = models.IntegerField(
#         help_text="HTTP status code"
#     )
    
#     response_data = models.JSONField(
#         default=dict,
#         help_text="JSON response data"
#     )
    
#     response_size_bytes = models.PositiveIntegerField(
#         default=0,
#         help_text="Response size in bytes"
#     )
    
#     processing_time_ms = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Processing time in milliseconds"
#     )
    
#     # Document information
#     document_id = models.CharField(
#         max_length=100,
#         blank=True,
#         null=True,
#         help_text="Document ID from the response"
#     )
    
#     # Seafarer profile information
#     seafarer_name = models.CharField(
#         max_length=200,
#         blank=True,
#         help_text="Seafarer full name"
#     )
    
#     seafarer_email = models.EmailField(
#         blank=True,
#         help_text="Seafarer email address"
#     )
    
#     seafarer_nationality = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Seafarer nationality"
#     )
    
#     quality_score = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Data quality score from response"
#     )
    
#     # Timestamps
#     timestamp = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When the log entry was created"
#     )
    
#     class Meta:
#         ordering = ['-timestamp']
#         verbose_name = "API Response Log"
#         verbose_name_plural = "API Response Logs"
#         indexes = [
#             models.Index(fields=['endpoint', '-timestamp']),
#             models.Index(fields=['user', '-timestamp']),
#             models.Index(fields=['status_code', '-timestamp']),
#             models.Index(fields=['seafarer_email']),
#             models.Index(fields=['document_id']),
#         ]
    
#     def __str__(self):
#         return f"{self.method} {self.endpoint} - {self.status_code} ({self.timestamp})"
    
#     @property
#     def is_successful(self):
#         """Check if the response was successful (2xx status code)."""
#         return 200 <= self.status_code < 300
    
#     @property
#     def is_error(self):
#         """Check if the response was an error (4xx or 5xx status code)."""
#         return self.status_code >= 400


# class EndpointStats(models.Model):
#     """
#     Model to track endpoint usage statistics.
#     """
    
#     endpoint = models.CharField(
#         max_length=255,
#         unique=True,
#         help_text="API endpoint path"
#     )
    
#     total_requests = models.PositiveIntegerField(
#         default=0,
#         help_text="Total number of requests"
#     )
    
#     successful_requests = models.PositiveIntegerField(
#         default=0,
#         help_text="Number of successful requests (2xx)"
#     )
    
#     error_requests = models.PositiveIntegerField(
#         default=0,
#         help_text="Number of error requests (4xx, 5xx)"
#     )
    
#     avg_processing_time_ms = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Average processing time in milliseconds"
#     )
    
#     avg_response_size_bytes = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Average response size in bytes"
#     )
    
#     last_accessed = models.DateTimeField(
#         auto_now=True,
#         help_text="Last time this endpoint was accessed"
#     )
    
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When the stats record was created"
#     )
    
#     class Meta:
#         ordering = ['-total_requests']
#         verbose_name = "Endpoint Statistics"
#         verbose_name_plural = "Endpoint Statistics"
    
#     def __str__(self):
#         return f"{self.endpoint} ({self.total_requests} requests)"
    
#     @property
#     def success_rate(self):
#         """Calculate success rate as a percentage."""
#         if self.total_requests == 0:
#             return 0.0
#         return (self.successful_requests / self.total_requests) * 100
    
#     def update_stats(self):
#         """Update statistics based on recent API logs."""
#         from django.db.models import Avg, Count, Q
        
#         # Get all logs for this endpoint
#         logs = APIResponseLog.objects.filter(endpoint=self.endpoint)
        
#         # Update basic counts
#         self.total_requests = logs.count()
#         self.successful_requests = logs.filter(
#             status_code__gte=200, 
#             status_code__lt=300
#         ).count()
#         self.error_requests = logs.filter(status_code__gte=400).count()
        
#         # Update averages
#         averages = logs.aggregate(
#             avg_processing_time=Avg('processing_time_ms'),
#             avg_response_size=Avg('response_size_bytes')
#         )
        
#         self.avg_processing_time_ms = averages['avg_processing_time']
#         self.avg_response_size_bytes = averages['avg_response_size']
        
#         self.save()


# class SeafarerProfileSummary(models.Model):
#     """
#     Model to track seafarer profiles extracted from documents.
#     """
    
#     seafarer_email = models.EmailField(
#         unique=True,
#         help_text="Seafarer email address (unique identifier)"
#     )
    
#     seafarer_name = models.CharField(
#         max_length=200,
#         help_text="Seafarer full name"
#     )
    
#     seafarer_nationality = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Seafarer nationality"
#     )
    
#     documents_processed = models.PositiveIntegerField(
#         default=0,
#         help_text="Number of documents processed for this seafarer"
#     )
    
#     avg_quality_score = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Average quality score across all documents"
#     )
    
#     first_seen = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When this seafarer was first processed"
#     )
    
#     last_seen = models.DateTimeField(
#         auto_now=True,
#         help_text="When this seafarer was last processed"
#     )
    
#     class Meta:
#         ordering = ['-last_seen']
#         verbose_name = "Seafarer Profile Summary"
#         verbose_name_plural = "Seafarer Profile Summaries"
#         indexes = [
#             models.Index(fields=['seafarer_email']),
#             models.Index(fields=['seafarer_nationality']),
#             models.Index(fields=['-last_seen']),
#         ]
    
#     def __str__(self):
#         return f"{self.seafarer_name} ({self.seafarer_email})"
    
#     @classmethod
#     def update_or_create_from_log(cls, api_log):
#         """Update or create seafarer summary from API log."""
#         if not api_log.seafarer_email:
#             return None
        
#         summary, created = cls.objects.get_or_create(
#             seafarer_email=api_log.seafarer_email,
#             defaults={
#                 'seafarer_name': api_log.seafarer_name or '',
#                 'seafarer_nationality': api_log.seafarer_nationality or '',
#             }
#         )
        
#         # Update document count and quality score
#         summary.documents_processed = APIResponseLog.objects.filter(
#             seafarer_email=summary.seafarer_email
#         ).exclude(document_id__isnull=True).exclude(document_id='').count()
        
#         from django.db.models import Avg
#         avg_score = APIResponseLog.objects.filter(
#             seafarer_email=summary.seafarer_email,
#             quality_score__isnull=False
#         ).aggregate(avg=Avg('quality_score'))['avg']
        
#         if avg_score is not None:
#             summary.avg_quality_score = avg_score
        
#         summary.save()
#         return summary






# from django.conf import settings
# from django.db import models

# # Create your models here.
# """
# Django models for document management system.
# Handles DOCX and PDF file storage and metadata.
# """

# from django.db import models
# from django.core.validators import FileExtensionValidator
# import os



# class Applicant(models.Model):
#     personal_details = models.JSONField(default=dict, blank=True, null=True)
#     education = models.JSONField(default=dict, blank=True, null=True)
#     contact_details = models.JSONField(default=dict, blank=True, null=True)
#     travel_documents = models.JSONField(default=dict, blank=True, null=True)
#     professional_qualifications = models.JSONField(default=dict, blank=True, null=True)
#     next_of_kin_emergency_contact = models.JSONField(default=dict, blank=True, null=True)
#     health_certificates_vaccinations = models.JSONField(default=dict, blank=True, null=True)
#     covid_19_vaccination = models.JSONField(default=dict, blank=True, null=True)
#     marine_courses = models.JSONField(default=dict, blank=True, null=True)
#     sea_service_details = models.JSONField(default=dict, blank=True, null=True)
#     specialised_experience = models.JSONField(default=dict, blank=True, null=True)
#     references = models.JSONField(default=dict, blank=True, null=True)
#     declaration = models.JSONField(default=dict, blank=True, null=True)
#     office_use_only = models.JSONField(default=dict, blank=True, null=True)

#     # ADD THESE NEW FIELDS:
#     physical_measurements = models.JSONField(default=dict, blank=True, null=True)
#     language_skills = models.JSONField(default=dict, blank=True, null=True)
#     medical_history = models.JSONField(default=dict, blank=True, null=True)
#     assessments = models.JSONField(default=dict, blank=True, null=True)
#     competency_tests = models.JSONField(default=dict, blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Applicant {self.id}"


# def document_upload_path(instance, filename):
#     """
#     Generate upload path for documents.
#     Files will be uploaded to MEDIA_ROOT/documents/year/month/day/filename
#     """
#     from datetime import datetime
#     now = datetime.now()
#     return f'documents/{now.year}/{now.month:02d}/{now.day:02d}/{filename}'


# class Document(models.Model):
#     """
#     Model to store document files (DOCX and PDF) with metadata.
#     """
#     DOCUMENT_TYPES = [
#         ('pdf', 'PDF Document'),
#         ('docx', 'Word Document'),
#     ]
    
#     STATUS_CHOICES = [
#         ('pending', 'Pending Processing'),
#         ('processing', 'Processing'),
#         ('completed', 'Processing Completed'),
#         ('failed', 'Processing Failed'),
#     ]
    
#     title = models.CharField(
#         max_length=255,
#         help_text="Document title or name"
#     )
    
#     description = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Optional description of the document"
#     )
    
#     file = models.FileField(
#         upload_to=document_upload_path,
#         validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
#         help_text="Upload PDF or DOCX file"
#     )
    
#     document_type = models.CharField(
#         max_length=10,
#         choices=DOCUMENT_TYPES,
#         help_text="Type of document based on file extension"
#     )
    
#     file_size = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="File size in bytes"
#     )
    
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending',
#         help_text="Processing status of the document"
#     )
    
#     extracted_text = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Text content extracted from the document"
#     )
    
#     page_count = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Number of pages in the document"
#     )
    
#     word_count = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Number of words in the document"
#     )
    
#     processing_error = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Error message if processing failed"
#     )
    
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="Timestamp when document was uploaded"
#     )
    
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         help_text="Timestamp when document was last updated"
#     )
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Document"
#         verbose_name_plural = "Documents"
    
#     def __str__(self):
#         return f"{self.title} ({self.document_type.upper()})"
    
#     def save(self, *args, **kwargs):
#         """
#         Override save method to automatically set document type and file size.
#         """
#         if self.file:
#             # Set document type based on file extension
#             file_extension = os.path.splitext(self.file.name)[1].lower()
#             if file_extension == '.pdf':
#                 self.document_type = 'pdf'
#             elif file_extension == '.docx':
#                 self.document_type = 'docx'
            
#             # Set file size
#             if hasattr(self.file, 'size'):
#                 self.file_size = self.file.size
        
#         super().save(*args, **kwargs)
    
#     @property
#     def file_size_mb(self):
#         """
#         Return file size in megabytes.
#         """
#         if self.file_size:
#             return round(self.file_size / (1024 * 1024), 2)
#         return None
    
#     @property
#     def is_processed(self):
#         """
#         Check if document has been successfully processed.
#         """
#         return self.status == 'completed'
    
#     def get_file_extension(self):
#         """
#         Get the file extension.
#         """
#         if self.file:
#             return os.path.splitext(self.file.name)[1].lower()
#         return None



# # Import logging models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from django.db.models import F
# import json


# class APIResponseLog(models.Model):
#     """
#     Model to log API responses with seafarer profile tracking.
#     """
    
#     # Request information
#     endpoint = models.CharField(
#         max_length=255,
#         help_text="API endpoint path"
#     )
    
#     method = models.CharField(
#         max_length=10,
#         help_text="HTTP method (GET, POST, etc.)"
#     )
    
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,   # ✅ instead of auth.User
#         on_delete=models.CASCADE
#     )
    
#     ip_address = models.GenericIPAddressField(
#         null=True,
#         blank=True,
#         help_text="Client IP address"
#     )
    
#     user_agent = models.TextField(
#         blank=True,
#         help_text="User agent string"
#     )
    
#     # Response information
#     status_code = models.IntegerField(
#         help_text="HTTP status code"
#     )
    
#     response_data = models.JSONField(
#         default=dict,
#         help_text="JSON response data"
#     )
    
#     response_size_bytes = models.PositiveIntegerField(
#         default=0,
#         help_text="Response size in bytes"
#     )
    
#     processing_time_ms = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Processing time in milliseconds"
#     )
    
#     # Document information
#     document_id = models.CharField(
#         max_length=100,
#         blank=True,
#         null=True,
#         help_text="Document ID from the response"
#     )
    
#     # Seafarer profile information
#     seafarer_name = models.CharField(
#         max_length=200,
#         blank=True,
#         help_text="Seafarer full name"
#     )
    
#     seafarer_email = models.EmailField(
#         blank=True,
#         help_text="Seafarer email address"
#     )
    
#     seafarer_nationality = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Seafarer nationality"
#     )
    
#     quality_score = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Data quality score from response"
#     )
    
#     # Timestamps
#     timestamp = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When the log entry was created"
#     )
    
#     class Meta:
#         ordering = ['-timestamp']
#         verbose_name = "API Response Log"
#         verbose_name_plural = "API Response Logs"
#         indexes = [
#             models.Index(fields=['endpoint', '-timestamp']),
#             models.Index(fields=['user', '-timestamp']),
#             models.Index(fields=['status_code', '-timestamp']),
#             models.Index(fields=['seafarer_email']),
#             models.Index(fields=['document_id']),
#         ]
    
#     def __str__(self):
#         return f"{self.method} {self.endpoint} - {self.status_code} ({self.timestamp})"
    
#     @property
#     def is_successful(self):
#         """Check if the response was successful (2xx status code)."""
#         return 200 <= self.status_code < 300
    
#     @property
#     def is_error(self):
#         """Check if the response was an error (4xx or 5xx status code)."""
#         return self.status_code >= 400


# class EndpointStats(models.Model):
#     """
#     Model to track endpoint usage statistics.
#     """
    
#     endpoint = models.CharField(
#         max_length=255,
#         unique=True,
#         help_text="API endpoint path"
#     )
    
#     total_requests = models.PositiveIntegerField(
#         default=0,
#         help_text="Total number of requests"
#     )
    
#     successful_requests = models.PositiveIntegerField(
#         default=0,
#         help_text="Number of successful requests (2xx)"
#     )
    
#     error_requests = models.PositiveIntegerField(
#         default=0,
#         help_text="Number of error requests (4xx, 5xx)"
#     )
    
#     avg_processing_time_ms = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Average processing time in milliseconds"
#     )
    
#     avg_response_size_bytes = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Average response size in bytes"
#     )
    
#     last_accessed = models.DateTimeField(
#         auto_now=True,
#         help_text="Last time this endpoint was accessed"
#     )
    
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When the stats record was created"
#     )
    
#     class Meta:
#         ordering = ['-total_requests']
#         verbose_name = "Endpoint Statistics"
#         verbose_name_plural = "Endpoint Statistics"
    
#     def __str__(self):
#         return f"{self.endpoint} ({self.total_requests} requests)"
    
#     @property
#     def success_rate(self):
#         """Calculate success rate as a percentage."""
#         if self.total_requests == 0:
#             return 0.0
#         return (self.successful_requests / self.total_requests) * 100
    
#     def update_stats(self):
#         """Update statistics based on recent API logs."""
#         from django.db.models import Avg, Count, Q
        
#         # Get all logs for this endpoint
#         logs = APIResponseLog.objects.filter(endpoint=self.endpoint)
        
#         # Update basic counts
#         self.total_requests = logs.count()
#         self.successful_requests = logs.filter(
#             status_code__gte=200, 
#             status_code__lt=300
#         ).count()
#         self.error_requests = logs.filter(status_code__gte=400).count()
        
#         # Update averages
#         averages = logs.aggregate(
#             avg_processing_time=Avg('processing_time_ms'),
#             avg_response_size=Avg('response_size_bytes')
#         )
        
#         self.avg_processing_time_ms = averages['avg_processing_time']
#         self.avg_response_size_bytes = averages['avg_response_size']
        
#         self.save()


# class SeafarerProfileSummary(models.Model):
#     """
#     Model to track seafarer profiles extracted from documents.
#     """
    
#     seafarer_email = models.EmailField(
#         unique=True,
#         help_text="Seafarer email address (unique identifier)"
#     )
    
#     seafarer_name = models.CharField(
#         max_length=200,
#         help_text="Seafarer full name"
#     )
    
#     seafarer_nationality = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Seafarer nationality"
#     )
    
#     documents_processed = models.PositiveIntegerField(
#         default=0,
#         help_text="Number of documents processed for this seafarer"
#     )
    
#     avg_quality_score = models.FloatField(
#         null=True,
#         blank=True,
#         help_text="Average quality score across all documents"
#     )
    
#     first_seen = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When this seafarer was first processed"
#     )
    
#     last_seen = models.DateTimeField(
#         auto_now=True,
#         help_text="When this seafarer was last processed"
#     )
    
#     class Meta:
#         ordering = ['-last_seen']
#         verbose_name = "Seafarer Profile Summary"
#         verbose_name_plural = "Seafarer Profile Summaries"
#         indexes = [
#             models.Index(fields=['seafarer_email']),
#             models.Index(fields=['seafarer_nationality']),
#             models.Index(fields=['-last_seen']),
#         ]
    
#     def __str__(self):
#         return f"{self.seafarer_name} ({self.seafarer_email})"
    
#     @classmethod
#     def update_or_create_from_log(cls, api_log):
#         """Update or create seafarer summary from API log."""
#         if not api_log.seafarer_email:
#             return None
        
#         summary, created = cls.objects.get_or_create(
#             seafarer_email=api_log.seafarer_email,
#             defaults={
#                 'seafarer_name': api_log.seafarer_name or '',
#                 'seafarer_nationality': api_log.seafarer_nationality or '',
#             }
#         )
        
#         # Update document count and quality score
#         summary.documents_processed = APIResponseLog.objects.filter(
#             seafarer_email=summary.seafarer_email
#         ).exclude(document_id__isnull=True).exclude(document_id='').count()
        
#         from django.db.models import Avg
#         avg_score = APIResponseLog.objects.filter(
#             seafarer_email=summary.seafarer_email,
#             quality_score__isnull=False
#         ).aggregate(avg=Avg('quality_score'))['avg']
        
#         if avg_score is not None:
#             summary.avg_quality_score = avg_score
        
#         summary.save()
#         return summary








from django.conf import settings
from django.db import models

# Create your models here.
"""
Django models for document management system.
Handles DOCX and PDF file storage and metadata.
"""

from django.db import models
from django.core.validators import FileExtensionValidator
import os



class Applicant(models.Model):
    personal_details = models.JSONField(default=dict, blank=True, null=True)
    education = models.JSONField(default=dict, blank=True, null=True)
    contact_details = models.JSONField(default=dict, blank=True, null=True)
    travel_documents = models.JSONField(default=dict, blank=True, null=True)
    professional_qualifications = models.JSONField(default=dict, blank=True, null=True)
    next_of_kin_emergency_contact = models.JSONField(default=dict, blank=True, null=True)
    health_certificates_vaccinations = models.JSONField(default=dict, blank=True, null=True)
    covid_19_vaccination = models.JSONField(default=dict, blank=True, null=True)
    marine_courses = models.JSONField(default=dict, blank=True, null=True)
    sea_service_details = models.JSONField(default=dict, blank=True, null=True)
    specialised_experience = models.JSONField(default=dict, blank=True, null=True)
    references = models.JSONField(default=dict, blank=True, null=True)
    declaration = models.JSONField(default=dict, blank=True, null=True)
    office_use_only = models.JSONField(default=dict, blank=True, null=True)

    # EXISTING NEW FIELDS:
    physical_measurements = models.JSONField(default=dict, blank=True, null=True)
    language_skills = models.JSONField(default=dict, blank=True, null=True)
    medical_history = models.JSONField(default=dict, blank=True, null=True)
    assessments = models.JSONField(default=dict, blank=True, null=True)
    competency_tests = models.JSONField(default=dict, blank=True, null=True)
    
    # ADD THIS NEW FIELD:
    applied_position_info = models.JSONField(default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Applicant {self.id}"


def document_upload_path(instance, filename):
    """
    Generate upload path for documents.
    Files will be uploaded to MEDIA_ROOT/documents/year/month/day/filename
    """
    from datetime import datetime
    now = datetime.now()
    return f'documents/{now.year}/{now.month:02d}/{now.day:02d}/{filename}'


class Document(models.Model):
    """
    Model to store document files (DOCX and PDF) with metadata.
    """
    DOCUMENT_TYPES = [
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Processing'),
        ('processing', 'Processing'),
        ('completed', 'Processing Completed'),
        ('failed', 'Processing Failed'),
    ]
    
    title = models.CharField(
        max_length=255,
        help_text="Document title or name"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the document"
    )
    
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        help_text="Upload PDF or DOCX file"
    )
    
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPES,
        help_text="Type of document based on file extension"
    )
    
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Processing status of the document"
    )
    
    extracted_text = models.TextField(
        blank=True,
        null=True,
        help_text="Text content extracted from the document"
    )
    
    page_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of pages in the document"
    )
    
    word_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of words in the document"
    )
    
    processing_error = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if processing failed"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when document was uploaded"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when document was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document"
        verbose_name_plural = "Documents"
    
    def __str__(self):
        return f"{self.title} ({self.document_type.upper()})"
    
    def save(self, *args, **kwargs):
        """
        Override save method to automatically set document type and file size.
        """
        if self.file:
            # Set document type based on file extension
            file_extension = os.path.splitext(self.file.name)[1].lower()
            if file_extension == '.pdf':
                self.document_type = 'pdf'
            elif file_extension == '.docx':
                self.document_type = 'docx'
            
            # Set file size
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """
        Return file size in megabytes.
        """
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    @property
    def is_processed(self):
        """
        Check if document has been successfully processed.
        """
        return self.status == 'completed'
    
    def get_file_extension(self):
        """
        Get the file extension.
        """
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None



# Import logging models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import F
import json


class APIResponseLog(models.Model):
    """
    Model to log API responses with seafarer profile tracking.
    """
    
    # Request information
    endpoint = models.CharField(
        max_length=255,
        help_text="API endpoint path"
    )
    
    method = models.CharField(
        max_length=10,
        help_text="HTTP method (GET, POST, etc.)"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # ✅ instead of auth.User
        on_delete=models.CASCADE
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )
    
    # Response information
    status_code = models.IntegerField(
        help_text="HTTP status code"
    )
    
    response_data = models.JSONField(
        default=dict,
        help_text="JSON response data"
    )
    
    response_size_bytes = models.PositiveIntegerField(
        default=0,
        help_text="Response size in bytes"
    )
    
    processing_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Processing time in milliseconds"
    )
    
    # Document information
    document_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Document ID from the response"
    )
    
    # Seafarer profile information
    seafarer_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Seafarer full name"
    )
    
    seafarer_email = models.EmailField(
        blank=True,
        help_text="Seafarer email address"
    )
    
    seafarer_nationality = models.CharField(
        max_length=100,
        blank=True,
        help_text="Seafarer nationality"
    )
    
    quality_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Data quality score from response"
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the log entry was created"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "API Response Log"
        verbose_name_plural = "API Response Logs"
        indexes = [
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
            models.Index(fields=['seafarer_email']),
            models.Index(fields=['document_id']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.timestamp})"
    
    @property
    def is_successful(self):
        """Check if the response was successful (2xx status code)."""
        return 200 <= self.status_code < 300
    
    @property
    def is_error(self):
        """Check if the response was an error (4xx or 5xx status code)."""
        return self.status_code >= 400


class EndpointStats(models.Model):
    """
    Model to track endpoint usage statistics.
    """
    
    endpoint = models.CharField(
        max_length=255,
        unique=True,
        help_text="API endpoint path"
    )
    
    total_requests = models.PositiveIntegerField(
        default=0,
        help_text="Total number of requests"
    )
    
    successful_requests = models.PositiveIntegerField(
        default=0,
        help_text="Number of successful requests (2xx)"
    )
    
    error_requests = models.PositiveIntegerField(
        default=0,
        help_text="Number of error requests (4xx, 5xx)"
    )
    
    avg_processing_time_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Average processing time in milliseconds"
    )
    
    avg_response_size_bytes = models.FloatField(
        null=True,
        blank=True,
        help_text="Average response size in bytes"
    )
    
    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text="Last time this endpoint was accessed"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the stats record was created"
    )
    
    class Meta:
        ordering = ['-total_requests']
        verbose_name = "Endpoint Statistics"
        verbose_name_plural = "Endpoint Statistics"
    
    def __str__(self):
        return f"{self.endpoint} ({self.total_requests} requests)"
    
    @property
    def success_rate(self):
        """Calculate success rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def update_stats(self):
        """Update statistics based on recent API logs."""
        from django.db.models import Avg, Count, Q
        
        # Get all logs for this endpoint
        logs = APIResponseLog.objects.filter(endpoint=self.endpoint)
        
        # Update basic counts
        self.total_requests = logs.count()
        self.successful_requests = logs.filter(
            status_code__gte=200, 
            status_code__lt=300
        ).count()
        self.error_requests = logs.filter(status_code__gte=400).count()
        
        # Update averages
        averages = logs.aggregate(
            avg_processing_time=Avg('processing_time_ms'),
            avg_response_size=Avg('response_size_bytes')
        )
        
        self.avg_processing_time_ms = averages['avg_processing_time']
        self.avg_response_size_bytes = averages['avg_response_size']
        
        self.save()


class SeafarerProfileSummary(models.Model):
    """
    Model to track seafarer profiles extracted from documents.
    """
    
    seafarer_email = models.EmailField(
        unique=True,
        help_text="Seafarer email address (unique identifier)"
    )
    
    seafarer_name = models.CharField(
        max_length=200,
        help_text="Seafarer full name"
    )
    
    seafarer_nationality = models.CharField(
        max_length=100,
        blank=True,
        help_text="Seafarer nationality"
    )
    
    documents_processed = models.PositiveIntegerField(
        default=0,
        help_text="Number of documents processed for this seafarer"
    )
    
    avg_quality_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Average quality score across all documents"
    )
    
    first_seen = models.DateTimeField(
        auto_now_add=True,
        help_text="When this seafarer was first processed"
    )
    
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text="When this seafarer was last processed"
    )
    
    class Meta:
        ordering = ['-last_seen']
        verbose_name = "Seafarer Profile Summary"
        verbose_name_plural = "Seafarer Profile Summaries"
        indexes = [
            models.Index(fields=['seafarer_email']),
            models.Index(fields=['seafarer_nationality']),
            models.Index(fields=['-last_seen']),
        ]
    
    def __str__(self):
        return f"{self.seafarer_name} ({self.seafarer_email})"
    
    @classmethod
    def update_or_create_from_log(cls, api_log):
        """Update or create seafarer summary from API log."""
        if not api_log.seafarer_email:
            return None
        
        summary, created = cls.objects.get_or_create(
            seafarer_email=api_log.seafarer_email,
            defaults={
                'seafarer_name': api_log.seafarer_name or '',
                'seafarer_nationality': api_log.seafarer_nationality or '',
            }
        )
        
        # Update document count and quality score
        summary.documents_processed = APIResponseLog.objects.filter(
            seafarer_email=summary.seafarer_email
        ).exclude(document_id__isnull=True).exclude(document_id='').count()
        
        from django.db.models import Avg
        avg_score = APIResponseLog.objects.filter(
            seafarer_email=summary.seafarer_email,
            quality_score__isnull=False
        ).aggregate(avg=Avg('quality_score'))['avg']
        
        if avg_score is not None:
            summary.avg_quality_score = avg_score
        
        summary.save()
        return summary