# """
# Django REST Framework serializers for document management.
# Handles serialization and validation of document data.
# """

# from rest_framework import serializers
# from .models import Document
# import os


# class DocumentUploadSerializer(serializers.ModelSerializer):
#     """
#     Serializer for uploading documents.
#     Validates file type and size before processing.
#     """
    
#     class Meta:
#         model = Document
#         fields = [
#             'id', 'title', 'description', 'file', 'document_type',
#             'file_size', 'status', 'created_at'
#         ]
#         read_only_fields = [
#             'id', 'document_type', 'file_size', 'status', 'created_at'
#         ]
    
#     def validate_file(self, value):
#         """
#         Validate uploaded file.
#         """
#         # Check file size (limit to 50MB)
#         max_size = 50 * 1024 * 1024  # 50MB in bytes
#         if value.size > max_size:
#             raise serializers.ValidationError(
#                 f"File size cannot exceed 50MB. Current size: {value.size / (1024*1024):.2f}MB"
#             )
        
#         # Check file extension
#         allowed_extensions = ['.pdf', '.docx']
#         file_extension = os.path.splitext(value.name)[1].lower()
#         if file_extension not in allowed_extensions:
#             raise serializers.ValidationError(
#                 f"File type '{file_extension}' is not supported. "
#                 f"Allowed types: {', '.join(allowed_extensions)}"
#             )
        
#         return value
    
#     def validate_title(self, value):
#         """
#         Validate document title.
#         """
#         if len(value.strip()) < 3:
#             raise serializers.ValidationError(
#                 "Title must be at least 3 characters long."
#             )
#         return value.strip()


# class DocumentDetailSerializer(serializers.ModelSerializer):
#     """
#     Detailed serializer for document information including extracted content.
#     """
#     file_size_mb = serializers.ReadOnlyField()
#     file_extension = serializers.SerializerMethodField()
#     is_processed = serializers.ReadOnlyField()
    
#     class Meta:
#         model = Document
#         fields = [
#             'id', 'title', 'description', 'file', 'document_type',
#             'file_size', 'file_size_mb', 'file_extension', 'status',
#             'extracted_text', 'page_count', 'word_count', 'processing_error',
#             'is_processed', 'created_at', 'updated_at'
#         ]
#         read_only_fields = [
#             'id', 'document_type', 'file_size', 'file_size_mb', 'file_extension',
#             'status', 'extracted_text', 'page_count', 'word_count',
#             'processing_error', 'is_processed', 'created_at', 'updated_at'
#         ]
    
#     def get_file_extension(self, obj):
#         """
#         Get file extension for the document.
#         """
#         return obj.get_file_extension()


# class DocumentListSerializer(serializers.ModelSerializer):
#     """
#     Lightweight serializer for listing documents.
#     """
#     file_size_mb = serializers.ReadOnlyField()
#     file_extension = serializers.SerializerMethodField()
#     is_processed = serializers.ReadOnlyField()
    
#     class Meta:
#         model = Document
#         fields = [
#             'id', 'title', 'document_type', 'file_size_mb', 'file_extension',
#             'status', 'is_processed', 'page_count', 'word_count', 'created_at'
#         ]
    
#     def get_file_extension(self, obj):
#         """
#         Get file extension for the document.
#         """
#         return obj.get_file_extension()


# class DocumentProcessingSerializer(serializers.ModelSerializer):
#     """
#     Serializer for updating document processing status and results.
#     Used internally by the processing system.
#     """
    
#     class Meta:
#         model = Document
#         fields = [
#             'status', 'extracted_text', 'page_count', 'word_count', 'processing_error'
#         ]
    
#     def validate_status(self, value):
#         """
#         Validate status transitions.
#         """
#         valid_statuses = ['pending', 'processing', 'completed', 'failed']
#         if value not in valid_statuses:
#             raise serializers.ValidationError(
#                 f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
#             )
#         return value


# class DocumentSearchSerializer(serializers.Serializer):
#     """
#     Serializer for document search parameters.
#     """
#     query = serializers.CharField(
#         required=False,
#         max_length=255,
#         help_text="Search query for document title or content"
#     )
    
#     document_type = serializers.ChoiceField(
#         choices=['pdf', 'docx'],
#         required=False,
#         help_text="Filter by document type"
#     )
    
#     status = serializers.ChoiceField(
#         choices=['pending', 'processing', 'completed', 'failed'],
#         required=False,
#         help_text="Filter by processing status"
#     )
    
#     date_from = serializers.DateField(
#         required=False,
#         help_text="Filter documents created from this date (YYYY-MM-DD)"
#     )
    
#     date_to = serializers.DateField(
#         required=False,
#         help_text="Filter documents created until this date (YYYY-MM-DD)"
#     )
    
#     def validate(self, data):
#         """
#         Validate search parameters.
#         """
#         date_from = data.get('date_from')
#         date_to = data.get('date_to')
        
#         if date_from and date_to and date_from > date_to:
#             raise serializers.ValidationError(
#                 "date_from cannot be later than date_to"
#             )
        
#         return data










"""
Django REST Framework serializers for document management.
Handles serialization and validation of document data.
"""

from rest_framework import serializers
from .models import Document, Applicant
from .data_mapper_service import DataMapperService
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
                f"File size cannot exceed 50MB. Current size: {value.size / (1024 * 1024):.2f}MB"
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
        """Get file extension for the document."""
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
        """Get file extension for the document."""
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


# ===== API APP STRUCTURE SERIALIZERS =====

class RankSerializer(serializers.Serializer):
    """Serializer for rank information in API app format."""
    id = serializers.IntegerField()
    assigned_code = serializers.CharField()
    rank_code = serializers.CharField()
    rank_name = serializers.CharField()
    rank = serializers.DictField()


class CertificateSerializer(serializers.Serializer):
    """Serializer for certificate information in API app format."""
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class ReferenceSerializer(serializers.Serializer):
    """Serializer for reference information in API app format."""
    id = serializers.IntegerField()
    company_name = serializers.CharField()
    position = serializers.CharField()
    name = serializers.CharField()
    tel = serializers.CharField()
    email = serializers.EmailField()


class SeaServiceSerializer(serializers.Serializer):
    """Serializer for sea service information in API app format."""
    id = serializers.IntegerField()
    company_name = serializers.CharField()
    rank = serializers.CharField()
    vessel_name_imo = serializers.CharField()
    flag = serializers.CharField()
    signed_on = serializers.DateField()
    signed_off = serializers.DateField()
    period = serializers.CharField()
    vessel_type = serializers.CharField()
    dwt_grt = serializers.CharField()
    engine_type_bh_kw = serializers.CharField()
    reason_for_sign_off = serializers.CharField()


class ApplicantToUsersSerializer(serializers.ModelSerializer):
    """
    Serializer that converts Applicant data to Users model format (API app structure).
    This serializer returns data in the same format as the API app's Users serializer.
    """
    first_name = serializers.SerializerMethodField()
    middle_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()

    passport_no = serializers.SerializerMethodField()
    passport_issue_date = serializers.SerializerMethodField()
    passport_expiry_date = serializers.SerializerMethodField()

    coc_certificate_name = serializers.SerializerMethodField()
    coc_certificate_number = serializers.SerializerMethodField()

    ranks = RankSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    sea_services = SeaServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Applicant
        fields = [
            'id', 'email', 'first_name', 'middle_name', 'profile_image', 'age',
            'nationality', 'passport_no', 'passport_issue_date', 'passport_expiry_date',
            'coc_certificate_name', 'coc_certificate_number', 'ranks', 'certificates',
            'references', 'sea_services', 'created_at'
        ]

    def get_first_name(self, obj):
        """Extract first name from personal details."""
        personal_details = obj.personal_details or {}
        full_name = personal_details.get('name', '') or personal_details.get('full_name', '')
        if full_name:
            return full_name.split()[0] if full_name.split() else ''
        return ''

    def get_middle_name(self, obj):
        """Extract middle name from personal details."""
        personal_details = obj.personal_details or {}
        full_name = personal_details.get('name', '') or personal_details.get('full_name', '')
        if full_name:
            name_parts = full_name.split()
            if len(name_parts) > 2:
                return ' '.join(name_parts[1:-1])
        return ''

    def get_profile_image(self, obj):
        """Return placeholder for profile image."""
        return None

    def get_age(self, obj):
        """Calculate age from date of birth."""
        personal_details = obj.personal_details or {}
        birth_date_str = personal_details.get('birth_date', '') or personal_details.get('date_of_birth', '')
        if birth_date_str:
            try:
                from datetime import datetime
                birth_date = DataMapperService.parse_date_string(birth_date_str)
                if birth_date:
                    today = datetime.now().date()
                    age = today.year - birth_date.year - (
                        (today.month, today.day) < (birth_date.month, birth_date.day)
                    )
                    return age
            except Exception:
                pass
        return None

    def get_nationality(self, obj):
        """Extract nationality from personal details."""
        personal_details = obj.personal_details or {}
        return personal_details.get('nationality', '')

    def get_passport_no(self, obj):
        """Extract passport number from travel documents."""
        travel_docs = obj.travel_documents or {}
        passport_details = travel_docs.get('passport_details', {})
        return passport_details.get('number', '') or passport_details.get('document_no', '')

    def get_passport_issue_date(self, obj):
        """Extract passport issue date from travel documents."""
        travel_docs = obj.travel_documents or {}
        passport_details = travel_docs.get('passport_details', {})
        issue_date_str = passport_details.get('iss_date', '') or passport_details.get('issue_date', '')
        if issue_date_str:
            return DataMapperService.parse_date_string(issue_date_str)
        return None

    def get_passport_expiry_date(self, obj):
        """Extract passport expiry date from travel documents."""
        travel_docs = obj.travel_documents or {}
        passport_details = travel_docs.get('passport_details', {})
        expiry_date_str = passport_details.get('exp_date', '') or passport_details.get('expiry_date', '')
        if expiry_date_str:
            return DataMapperService.parse_date_string(expiry_date_str)
        return None

    def get_coc_certificate_name(self, obj):
        """Extract COC certificate name from professional qualifications."""
        prof_quals = obj.professional_qualifications or {}
        certificates = prof_quals.get('certificates', [])
        if isinstance(certificates, list) and certificates:
            first_cert = certificates[0]
            if isinstance(first_cert, dict):
                return first_cert.get('name', '')
        return ''

    def get_coc_certificate_number(self, obj):
        """Extract COC certificate number from professional qualifications."""
        prof_quals = obj.professional_qualifications or {}
        certificates = prof_quals.get('certificates', [])
        if isinstance(certificates, list) and certificates:
            first_cert = certificates[0]
            if isinstance(first_cert, dict):
                return first_cert.get('number', '')
        return ''

    def to_representation(self, instance):
        """Override to add dynamic data for relationships."""
        data = super().to_representation(instance)

        contact_details = instance.contact_details or {}
        personal_details = instance.personal_details or {}
        data['email'] = contact_details.get('email', '') or personal_details.get('email', '')

        certificates_data = DataMapperService.extract_certificates_from_data({
            'Professional_Qualifications': instance.professional_qualifications or {},
            'Marine_Courses': instance.marine_courses or {},
            'Sea_Service_Details': instance.sea_service_details or {},
        })

        data['certificates'] = [
            {
                'id': idx + 1,
                'code': cert_name.upper().replace(' ', '_')[:100],
                'name': cert_name
            }
            for idx, cert_name in enumerate(certificates_data)
        ]

        references_data = DataMapperService.extract_references_from_data({
            'References': instance.references or {}
        })

        data['references'] = [
            {
                'id': idx + 1,
                'company_name': ref.get('company_name', ''),
                'position': ref.get('position', ''),
                'name': ref.get('name', ''),
                'tel': ref.get('tel', ''),
                'email': ref.get('email', '')
            }
            for idx, ref in enumerate(references_data)
        ]

        sea_services_data = DataMapperService.extract_sea_services_from_data({
            'Sea_Service_Details': instance.sea_service_details or {}
        })

        data['sea_services'] = [
            {
                'id': idx + 1,
                'company_name': service.get('company_name', ''),
                'rank': service.get('rank', ''),
                'vessel_name_imo': service.get('vessel_name_imo', ''),
                'flag': service.get('flag', ''),
                'signed_on': service.get('signed_on'),
                'signed_off': service.get('signed_off'),
                'period': service.get('period', ''),
                'vessel_type': service.get('vessel_type', ''),
                'dwt_grt': service.get('dwt_grt', ''),
                'engine_type_bh_kw': service.get('engine_type_bh_kw', ''),
                'reason_for_sign_off': service.get('reason_for_sign_off', '')
            }
            for idx, service in enumerate(sea_services_data)
        ]

        data['ranks'] = []
        return data


class DocumentWithUsersFormatSerializer(serializers.ModelSerializer):
    """
    Document serializer that includes processed applicant data in Users format.
    Combines document metadata with extracted applicant data formatted
    like the API app's Users model.
    """
    file_size_mb = serializers.ReadOnlyField()
    file_extension = serializers.SerializerMethodField()
    is_processed = serializers.ReadOnlyField()
    applicant_data = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'document_type',
            'file_size', 'file_size_mb', 'file_extension', 'status',
            'page_count', 'word_count', 'is_processed',
            'created_at', 'updated_at', 'applicant_data'
        ]

    def get_file_extension(self, obj):
        """Get file extension for the document."""
        return obj.get_file_extension()

    def get_applicant_data(self, obj):
        """Get related applicant data formatted like Users model."""
        try:
            from .models import Applicant
            applicant = Applicant.objects.first()  # Replace with actual relation
            if applicant:
                serializer = ApplicantToUsersSerializer(applicant)
                return serializer.data
        except Exception:
            pass
        return None
