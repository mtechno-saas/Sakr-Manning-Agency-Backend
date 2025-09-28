"""
Django REST Framework serializers for document management.
Handles serialization and validation of document data.
"""

from rest_framework import serializers
from .models import Document
import os


class DocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading documents.
    Validates file type and size before processing.
    """
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'document_type',
            'file_size', 'status', 'created_at'
        ]
        read_only_fields = [
            'id', 'document_type', 'file_size', 'status', 'created_at'
        ]
    
    def validate_file(self, value):
        """
        Validate uploaded file.
        """
        # Check file size (limit to 50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size cannot exceed 50MB. Current size: {value.size / (1024*1024):.2f}MB"
            )
        
        # Check file extension
        allowed_extensions = ['.pdf', '.docx']
        file_extension = os.path.splitext(value.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type '{file_extension}' is not supported. "
                f"Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def validate_title(self, value):
        """
        Validate document title.
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long."
            )
        return value.strip()


class DocumentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for document information including extracted content.
    """
    file_size_mb = serializers.ReadOnlyField()
    file_extension = serializers.SerializerMethodField()
    is_processed = serializers.ReadOnlyField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'document_type',
            'file_size', 'file_size_mb', 'file_extension', 'status',
            'extracted_text', 'page_count', 'word_count', 'processing_error',
            'is_processed', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'document_type', 'file_size', 'file_size_mb', 'file_extension',
            'status', 'extracted_text', 'page_count', 'word_count',
            'processing_error', 'is_processed', 'created_at', 'updated_at'
        ]
    
    def get_file_extension(self, obj):
        """
        Get file extension for the document.
        """
        return obj.get_file_extension()


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing documents.
    """
    file_size_mb = serializers.ReadOnlyField()
    file_extension = serializers.SerializerMethodField()
    is_processed = serializers.ReadOnlyField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'file_size_mb', 'file_extension',
            'status', 'is_processed', 'page_count', 'word_count', 'created_at'
        ]
    
    def get_file_extension(self, obj):
        """
        Get file extension for the document.
        """
        return obj.get_file_extension()


class DocumentProcessingSerializer(serializers.ModelSerializer):
    """
    Serializer for updating document processing status and results.
    Used internally by the processing system.
    """
    
    class Meta:
        model = Document
        fields = [
            'status', 'extracted_text', 'page_count', 'word_count', 'processing_error'
        ]
    
    def validate_status(self, value):
        """
        Validate status transitions.
        """
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value


class DocumentSearchSerializer(serializers.Serializer):
    """
    Serializer for document search parameters.
    """
    query = serializers.CharField(
        required=False,
        max_length=255,
        help_text="Search query for document title or content"
    )
    
    document_type = serializers.ChoiceField(
        choices=['pdf', 'docx'],
        required=False,
        help_text="Filter by document type"
    )
    
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'completed', 'failed'],
        required=False,
        help_text="Filter by processing status"
    )
    
    date_from = serializers.DateField(
        required=False,
        help_text="Filter documents created from this date (YYYY-MM-DD)"
    )
    
    date_to = serializers.DateField(
        required=False,
        help_text="Filter documents created until this date (YYYY-MM-DD)"
    )
    
    def validate(self, data):
        """
        Validate search parameters.
        """
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "date_from cannot be later than date_to"
            )
        
        return data
