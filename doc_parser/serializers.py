

# from rest_framework import serializers
# from .models import ParsedDocument
# from doc_parser.ai_parser_service import extract_document_features

# class ParsedDocumentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParsedDocument
#         fields = "__all__"
#         # fields = [
#         #     'id',
#         #     'source_file',
#         #     #'raw_text', # Add the new raw_text field here
#         #     'extracted_data_yaml',
#         #     'status',
#         #     'created_at',
#         #     'associated_user'
#         # ]
#         # read_only_fields = [
#         #     #'raw_text', # Mark raw_text as read-only as it's set by the backend
#         #     'extracted_data_yaml',
#         #     'status',
#         #     'created_at',
#         #     'associated_user'
#         # ]

"""
Enhanced serializers for the document parser with structured feature storage.
"""

from rest_framework import serializers
from .models import ParsedDocument, ExtractedFeature, DocumentTable, ProcessingLog


class ExtractedFeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for individual extracted features.
    """
    class Meta:
        model = ExtractedFeature
        fields = [
            'id', 'category', 'field_name', 'field_value', 
            'confidence_score', 'extraction_method', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DocumentTableSerializer(serializers.ModelSerializer):
    """
    Serializer for document tables.
    """
    class Meta:
        model = DocumentTable
        fields = [
            'id', 'table_index', 'table_data', 'table_headers',
            'row_count', 'column_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProcessingLogSerializer(serializers.ModelSerializer):
    """
    Serializer for processing logs.
    """
    class Meta:
        model = ProcessingLog
        fields = [
            'id', 'level', 'message', 'step', 'extra_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ParsedDocumentSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for parsed documents with structured features.
    """
    # Include related data
    features = ExtractedFeatureSerializer(many=True, read_only=True)
    tables = DocumentTableSerializer(many=True, read_only=True)
    processing_logs = ProcessingLogSerializer(many=True, read_only=True)
    
    # Computed fields
    quality_score = serializers.SerializerMethodField()
    feature_count = serializers.SerializerMethodField()
    table_count = serializers.SerializerMethodField()
    has_complete_personal_info = serializers.SerializerMethodField()
    
    # Personal info shortcuts
    personal_information = serializers.SerializerMethodField()
    qualifications = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    medical_information = serializers.SerializerMethodField()
    next_of_kin = serializers.SerializerMethodField()

    class Meta:
        model = ParsedDocument
        fields = [
            'id', 'source_file', 'raw_text', 'extracted_data_yaml',
            'extracted_features', 'processing_metadata', 'status',
            'created_at', 'updated_at', 'associated_user',
            # Related data
            'features', 'tables', 'processing_logs',
            # Computed fields
            'quality_score', 'feature_count', 'table_count',
            'has_complete_personal_info',
            # Structured data shortcuts
            'personal_information', 'qualifications', 'experience',
            'medical_information', 'next_of_kin'
        ]
        read_only_fields = [
            'id', 'raw_text', 'extracted_data_yaml', 'extracted_features',
            'processing_metadata', 'status', 'created_at', 'updated_at',
            'features', 'tables', 'processing_logs',
            'quality_score', 'feature_count', 'table_count',
            'has_complete_personal_info',
            'personal_information', 'qualifications', 'experience',
            'medical_information', 'next_of_kin'
        ]

    def get_quality_score(self, obj):
        """Get the extraction quality score."""
        return obj.get_extraction_quality_score()

    def get_feature_count(self, obj):
        """Get the number of extracted features."""
        return obj.features.count()

    def get_table_count(self, obj):
        """Get the number of extracted tables."""
        return obj.tables.count()

    def get_has_complete_personal_info(self, obj):
        """Check if personal information is complete."""
        return obj.has_complete_personal_info()

    def get_personal_information(self, obj):
        """Get personal information from extracted features."""
        return obj.get_personal_info()

    def get_qualifications(self, obj):
        """Get qualifications from extracted features."""
        return obj.get_qualifications()

    def get_experience(self, obj):
        """Get experience information from extracted features."""
        return obj.get_experience()

    def get_medical_information(self, obj):
        """Get medical information from extracted features."""
        return obj.get_medical_info()

    def get_next_of_kin(self, obj):
        """Get next of kin information from extracted features."""
        return obj.get_next_of_kin()


class ParsedDocumentSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for document lists without heavy nested data.
    """
    quality_score = serializers.SerializerMethodField()
    feature_count = serializers.SerializerMethodField()
    table_count = serializers.SerializerMethodField()
    has_complete_personal_info = serializers.SerializerMethodField()
    
    # Key personal info fields for quick overview
    full_name = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = ParsedDocument
        fields = [
            'id', 'source_file', 'status', 'created_at', 'updated_at',
            'quality_score', 'feature_count', 'table_count',
            'has_complete_personal_info', 'full_name', 'nationality', 'email'
        ]

    def get_quality_score(self, obj):
        """Get the extraction quality score."""
        return obj.get_extraction_quality_score()

    def get_feature_count(self, obj):
        """Get the number of extracted features."""
        return obj.features.count()

    def get_table_count(self, obj):
        """Get the number of extracted tables."""
        return obj.tables.count()

    def get_has_complete_personal_info(self, obj):
        """Check if personal information is complete."""
        return obj.has_complete_personal_info()

    def get_full_name(self, obj):
        """Get full name from personal information."""
        personal_info = obj.get_personal_info()
        return personal_info.get('full_name', '')

    def get_nationality(self, obj):
        """Get nationality from personal information."""
        personal_info = obj.get_personal_info()
        return personal_info.get('nationality', '')

    def get_email(self, obj):
        """Get email from personal information."""
        personal_info = obj.get_personal_info()
        return personal_info.get('email', '')


class FeatureSummarySerializer(serializers.Serializer):
    """
    Serializer for feature summary statistics.
    """
    category = serializers.CharField()
    feature_count = serializers.IntegerField()
    avg_confidence = serializers.FloatField()
    features = ExtractedFeatureSerializer(many=True)


class DocumentStatsSerializer(serializers.Serializer):
    """
    Serializer for document processing statistics.
    """
    total_documents = serializers.IntegerField()
    completed_documents = serializers.IntegerField()
    failed_documents = serializers.IntegerField()
    avg_quality_score = serializers.FloatField()
    total_features_extracted = serializers.IntegerField()
    total_tables_extracted = serializers.IntegerField()
    processing_success_rate = serializers.FloatField()
