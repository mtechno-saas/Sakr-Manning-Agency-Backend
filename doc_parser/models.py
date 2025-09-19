

# # doc_parser/models.py
# from django.db import models
# from api.models import Users  # Make sure this import is correct

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
    
#     # Link to the user profile that was created from this doc
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
# doc_parser/models.py
from django.db import models
from api.models import Users  # Optional: to link to a user
import json


class ParsedDocument(models.Model):
    """
    Stores an uploaded document, its processing status,
    and the extracted data in structured YAML format.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    # The original uploaded file
    source_file = models.FileField(upload_to='source_documents/')

    # The raw text extracted from the document
    raw_text = models.TextField(
        blank=True,
        help_text="The raw text extracted from the document."
    )

    # The extracted data, stored as text in YAML format
    extracted_data_yaml = models.TextField(
        blank=True,
        help_text="The structured data extracted from the document, in YAML format."
    )

    # NEW: Structured extracted features stored as JSON text (database agnostic)
    extracted_features_json = models.TextField(
        blank=True,
        default='{}',
        help_text="The extracted seafarer features stored as JSON string."
    )

    # NEW: Processing metadata stored as JSON text (database agnostic)
    processing_metadata_json = models.TextField(
        blank=True,
        default='{}',
        help_text="Metadata about the processing including extraction quality, tables found, etc."
    )

    # Tracking fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: Link to the user profile that was created or updated from this doc
    associated_user = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parsed_documents'
    )

    def __str__(self):
        return f"Document {self.id} - {self.status}"

    # Property methods to handle JSON serialization/deserialization
    @property
    def extracted_features(self):
        """Get extracted features as Python dict."""
        try:
            return json.loads(self.extracted_features_json) if self.extracted_features_json else {}
        except json.JSONDecodeError:
            return {}

    @extracted_features.setter
    def extracted_features(self, value):
        """Set extracted features from Python dict."""
        self.extracted_features_json = json.dumps(value) if value else '{}'

    @property
    def processing_metadata(self):
        """Get processing metadata as Python dict."""
        try:
            return json.loads(self.processing_metadata_json) if self.processing_metadata_json else {}
        except json.JSONDecodeError:
            return {}

    @processing_metadata.setter
    def processing_metadata(self, value):
        """Set processing metadata from Python dict."""
        self.processing_metadata_json = json.dumps(value) if value else '{}'

    def get_personal_info(self):
        """Get personal information from extracted features."""
        return self.extracted_features.get('personal_information', {})

    def get_qualifications(self):
        """Get qualifications from extracted features."""
        return self.extracted_features.get('qualifications', {})

    def get_experience(self):
        """Get experience information from extracted features."""
        return self.extracted_features.get('experience', {})

    def get_medical_info(self):
        """Get medical information from extracted features."""
        return self.extracted_features.get('medical_information', {})

    def get_next_of_kin(self):
        """Get next of kin information from extracted features."""
        return self.extracted_features.get('next_of_kin', {})

    def has_complete_personal_info(self):
        """Check if personal information is reasonably complete."""
        personal_info = self.get_personal_info()
        required_fields = ['full_name', 'nationality', 'date_of_birth']
        return all(
            personal_info.get(field) and personal_info.get(field) != "Not Available"
            for field in required_fields
        )

    def get_extraction_quality_score(self):
        """Calculate a quality score based on how many fields were extracted."""
        if not self.extracted_features:
            return 0
        
        total_fields = 0
        filled_fields = 0
        
        # Count fields in each section
        sections = ['personal_information', 'qualifications', 'experience', 'medical_information', 'next_of_kin']
        
        for section in sections:
            section_data = self.extracted_features.get(section, {})
            if isinstance(section_data, dict):
                for value in section_data.values():
                    total_fields += 1
                    if value and str(value).strip() and str(value) != "Not Available":
                        filled_fields += 1
        
        return (filled_fields / total_fields * 100) if total_fields > 0 else 0


class ExtractedFeature(models.Model):
    """
    Individual extracted features for more granular storage and querying.
    This allows for better searching and filtering of seafarer data.
    """
    FEATURE_CATEGORIES = [
        ('personal', 'Personal Information'),
        ('qualification', 'Qualification'),
        ('experience', 'Experience'),
        ('medical', 'Medical Information'),
        ('contact', 'Contact Information'),
        ('document', 'Document Information'),
        ('other', 'Other'),
    ]

    # Link to the parsed document
    document = models.ForeignKey(
        ParsedDocument,
        on_delete=models.CASCADE,
        related_name='features'
    )

    # Feature details
    category = models.CharField(max_length=20, choices=FEATURE_CATEGORIES)
    field_name = models.CharField(max_length=100, help_text="Name of the extracted field")
    field_value = models.TextField(help_text="Value of the extracted field")
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence score of the extraction (0.0 to 1.0)"
    )

    # Metadata
    extraction_method = models.CharField(
        max_length=50,
        default='ai_extraction',
        help_text="Method used to extract this feature"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'field_name')
        indexes = [
            models.Index(fields=['category', 'field_name']),
            models.Index(fields=['document', 'category']),
        ]

    def __str__(self):
        return f"{self.document.id} - {self.field_name}: {self.field_value[:50]}"


class DocumentTable(models.Model):
    """
    Store tables extracted from documents for better structured data access.
    """
    # Link to the parsed document
    document = models.ForeignKey(
        ParsedDocument,
        on_delete=models.CASCADE,
        related_name='tables'
    )

    # Table details
    table_index = models.IntegerField(help_text="Index of the table in the document")
    table_data_json = models.TextField(help_text="Table data as JSON string")
    table_headers_json = models.TextField(
        default='[]',
        blank=True,
        help_text="Table headers as JSON string"
    )
    
    # Metadata
    row_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'table_index')

    def __str__(self):
        return f"Table {self.table_index} from Document {self.document.id} ({self.row_count}x{self.column_count})"

    @property
    def table_data(self):
        """Get table data as Python list."""
        try:
            return json.loads(self.table_data_json) if self.table_data_json else []
        except json.JSONDecodeError:
            return []

    @table_data.setter
    def table_data(self, value):
        """Set table data from Python list."""
        self.table_data_json = json.dumps(value) if value else '[]'

    @property
    def table_headers(self):
        """Get table headers as Python list."""
        try:
            return json.loads(self.table_headers_json) if self.table_headers_json else []
        except json.JSONDecodeError:
            return []

    @table_headers.setter
    def table_headers(self, value):
        """Set table headers from Python list."""
        self.table_headers_json = json.dumps(value) if value else '[]'


class ProcessingLog(models.Model):
    """
    Log processing steps and results for debugging and monitoring.
    """
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
    ]

    # Link to the parsed document
    document = models.ForeignKey(
        ParsedDocument,
        on_delete=models.CASCADE,
        related_name='processing_logs'
    )

    # Log details
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    step = models.CharField(
        max_length=100,
        help_text="Processing step (e.g., 'extraction', 'ai_processing', 'validation')"
    )
    
    # Additional data stored as JSON string
    extra_data_json = models.TextField(
        default='{}',
        blank=True,
        help_text="Additional structured data related to this log entry as JSON string"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.level} - {self.step}: {self.message[:100]}"

    @property
    def extra_data(self):
        """Get extra data as Python dict."""
        try:
            return json.loads(self.extra_data_json) if self.extra_data_json else {}
        except json.JSONDecodeError:
            return {}

    @extra_data.setter
    def extra_data(self, value):
        """Set extra data from Python dict."""
        self.extra_data_json = json.dumps(value) if value else '{}'


