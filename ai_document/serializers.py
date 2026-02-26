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










# """
# Django REST Framework serializers for document management.
# Handles serialization and validation of document data.
# """

# from rest_framework import serializers
# from .models import Document, Applicant
# from .data_mapper_service import DataMapperService
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
#                 f"File size cannot exceed 50MB. Current size: {value.size / (1024 * 1024):.2f}MB"
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
#         """Get file extension for the document."""
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
#         """Get file extension for the document."""
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


# # ===== API APP STRUCTURE SERIALIZERS =====

# class RankSerializer(serializers.Serializer):
#     """Serializer for rank information in API app format."""
#     id = serializers.IntegerField()
#     assigned_code = serializers.CharField()
#     rank_code = serializers.CharField()
#     rank_name = serializers.CharField()
#     rank = serializers.DictField()


# class CertificateSerializer(serializers.Serializer):
#     """Serializer for certificate information in API app format."""
#     id = serializers.IntegerField()
#     code = serializers.CharField()
#     name = serializers.CharField()


# class ReferenceSerializer(serializers.Serializer):
#     """Serializer for reference information in API app format."""
#     id = serializers.IntegerField()
#     company_name = serializers.CharField()
#     position = serializers.CharField()
#     name = serializers.CharField()
#     tel = serializers.CharField()
#     email = serializers.EmailField()


# class SeaServiceSerializer(serializers.Serializer):
#     """Serializer for sea service information in API app format."""
#     id = serializers.IntegerField()
#     company_name = serializers.CharField()
#     rank = serializers.CharField()
#     vessel_name_imo = serializers.CharField()
#     flag = serializers.CharField()
#     signed_on = serializers.DateField()
#     signed_off = serializers.DateField()
#     period = serializers.CharField()
#     vessel_type = serializers.CharField()
#     dwt = serializers.CharField()
#     grt = serializers.CharField()
#     engine_type = serializers.CharField()
#     bh = serializers.CharField()
#     kw = serializers.CharField()
#     reason_for_sign_off = serializers.CharField()


# class ApplicantToUsersSerializer(serializers.ModelSerializer):
#     """
#     Serializer that converts Applicant data to Users model format (API app structure).
#     This serializer returns data in the same format as the API app's Users serializer.
#     """
#     first_name = serializers.SerializerMethodField()
#     middle_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
#     age = serializers.SerializerMethodField()
#     nationality = serializers.SerializerMethodField()

#     passport_no = serializers.SerializerMethodField()
#     passport_issue_date = serializers.SerializerMethodField()
#     passport_expiry_date = serializers.SerializerMethodField()

#     coc_certificate_name = serializers.SerializerMethodField()
#     coc_certificate_number = serializers.SerializerMethodField()

#     ranks = RankSerializer(many=True, read_only=True)
#     certificates = CertificateSerializer(many=True, read_only=True)
#     references = ReferenceSerializer(many=True, read_only=True)
#     sea_services = SeaServiceSerializer(many=True, read_only=True)

#     class Meta:
#         model = Applicant
#         fields = [
#             'id', 'email', 'first_name', 'middle_name', 'profile_image', 'age',
#             'nationality', 'passport_no', 'passport_issue_date', 'passport_expiry_date',
#             'coc_certificate_name', 'coc_certificate_number', 'ranks', 'certificates',
#             'references', 'sea_services', 'created_at'
#         ]

#     def get_first_name(self, obj):
#         """Extract first name from personal details."""
#         personal_details = obj.personal_details or {}
#         full_name = personal_details.get('name', '') or personal_details.get('full_name', '')
#         if full_name:
#             return full_name.split()[0] if full_name.split() else ''
#         return ''

#     def get_middle_name(self, obj):
#         """Extract middle name from personal details."""
#         personal_details = obj.personal_details or {}
#         full_name = personal_details.get('name', '') or personal_details.get('full_name', '')
#         if full_name:
#             name_parts = full_name.split()
#             if len(name_parts) > 2:
#                 return ' '.join(name_parts[1:-1])
#         return ''

#     def get_profile_image(self, obj):
#         """Return placeholder for profile image."""
#         return None

#     def get_age(self, obj):
#         """Calculate age from date of birth."""
#         personal_details = obj.personal_details or {}
#         birth_date_str = personal_details.get('birth_date', '') or personal_details.get('date_of_birth', '')
#         if birth_date_str:
#             try:
#                 from datetime import datetime
#                 birth_date = DataMapperService.parse_date_string(birth_date_str)
#                 if birth_date:
#                     today = datetime.now().date()
#                     age = today.year - birth_date.year - (
#                         (today.month, today.day) < (birth_date.month, birth_date.day)
#                     )
#                     return age
#             except Exception:
#                 pass
#         return None

#     def get_nationality(self, obj):
#         """Extract nationality from personal details."""
#         personal_details = obj.personal_details or {}
#         return personal_details.get('nationality', '')

#     def get_passport_no(self, obj):
#         """Extract passport number from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         passport_details = travel_docs.get('passport_details', {})
#         return passport_details.get('number', '') or passport_details.get('document_no', '')

#     def get_passport_issue_date(self, obj):
#         """Extract passport issue date from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         passport_details = travel_docs.get('passport_details', {})
#         issue_date_str = passport_details.get('iss_date', '') or passport_details.get('issue_date', '')
#         if issue_date_str:
#             return DataMapperService.parse_date_string(issue_date_str)
#         return None

#     def get_passport_expiry_date(self, obj):
#         """Extract passport expiry date from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         passport_details = travel_docs.get('passport_details', {})
#         expiry_date_str = passport_details.get('exp_date', '') or passport_details.get('expiry_date', '')
#         if expiry_date_str:
#             return DataMapperService.parse_date_string(expiry_date_str)
#         return None

#     def get_coc_certificate_name(self, obj):
#         """Extract COC certificate name from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         certificates = prof_quals.get('certificates', [])
#         if isinstance(certificates, list) and certificates:
#             first_cert = certificates[0]
#             if isinstance(first_cert, dict):
#                 return first_cert.get('name', '')
#         return ''

#     def get_coc_certificate_number(self, obj):
#         """Extract COC certificate number from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         certificates = prof_quals.get('certificates', [])
#         if isinstance(certificates, list) and certificates:
#             first_cert = certificates[0]
#             if isinstance(first_cert, dict):
#                 return first_cert.get('number', '')
#         return ''

#     def to_representation(self, instance):
#         """Override to add dynamic data for relationships."""
#         data = super().to_representation(instance)

#         contact_details = instance.contact_details or {}
#         personal_details = instance.personal_details or {}
#         data['email'] = contact_details.get('email', '') or personal_details.get('email', '')

#         certificates_data = DataMapperService.extract_certificates_from_data({
#             'Professional_Qualifications': instance.professional_qualifications or {},
#             'Marine_Courses': instance.marine_courses or {},
#             'Sea_Service_Details': instance.sea_service_details or {},
#         })

#         data['certificates'] = [
#             {
#                 'id': idx + 1,
#                 'code': cert_name.upper().replace(' ', '_')[:100],
#                 'name': cert_name
#             }
#             for idx, cert_name in enumerate(certificates_data)
#         ]

#         references_data = DataMapperService.extract_references_from_data({
#             'References': instance.references or {}
#         })

#         data['references'] = [
#             {
#                 'id': idx + 1,
#                 'company_name': ref.get('company_name', ''),
#                 'position': ref.get('position', ''),
#                 'name': ref.get('name', ''),
#                 'tel': ref.get('tel', ''),
#                 'email': ref.get('email', '')
#             }
#             for idx, ref in enumerate(references_data)
#         ]

#         sea_services_data = DataMapperService.extract_sea_services_from_data({
#             'Sea_Service_Details': instance.sea_service_details or {}
#         })

#         data['sea_services'] = [
#             {
#                 'id': idx + 1,
#                 'company_name': service.get('company_name', ''),
#                 'rank': service.get('rank', ''),
#                 'vessel_name_imo': service.get('vessel_name_imo', ''),
#                 'flag': service.get('flag', ''),
#                 'signed_on': service.get('signed_on'),
#                 'signed_off': service.get('signed_off'),
#                 'period': service.get('period', ''),
#                 'vessel_type': service.get('vessel_type', ''),
#                 'dwt': service.get('dwt', ''),
#                 'grt': service.get('grt', ''),
#                 'engine_type': service.get('engine_type', ''),
#                 'bh': service.get('bh', ''),
#                 'kw': service.get('kw', ''),
#                 'reason_for_sign_off': service.get('reason_for_sign_off', '')
#             }
#             for idx, service in enumerate(sea_services_data)
#         ]

#         data['ranks'] = []
#         return data


# class DocumentWithUsersFormatSerializer(serializers.ModelSerializer):
#     """
#     Document serializer that includes processed applicant data in Users format.
#     Combines document metadata with extracted applicant data formatted
#     like the API app's Users model.
#     """
#     file_size_mb = serializers.ReadOnlyField()
#     file_extension = serializers.SerializerMethodField()
#     is_processed = serializers.ReadOnlyField()
#     applicant_data = serializers.SerializerMethodField()

#     class Meta:
#         model = Document
#         fields = [
#             'id', 'title', 'description', 'file', 'document_type',
#             'file_size', 'file_size_mb', 'file_extension', 'status',
#             'page_count', 'word_count', 'is_processed',
#             'created_at', 'updated_at', 'applicant_data'
#         ]

#     def get_file_extension(self, obj):
#         """Get file extension for the document."""
#         return obj.get_file_extension()

#     def get_applicant_data(self, obj):
#         """Get related applicant data formatted like Users model."""
#         try:
#             from .models import Applicant
#             applicant = Applicant.objects.first()  # Replace with actual relation
#             if applicant:
#                 serializer = ApplicantToUsersSerializer(applicant)
#                 return serializer.data
#         except Exception:
#             pass
#         return None









# from rest_framework import serializers

# from api.serializer import CertificateSerializer, RankSerializer, ReferenceSerializer, SeaServiceSerializer
# from .models import Document, Applicant
# from .data_mapper_service import DataMapperService
# import os








# class ApplicantToUsersSerializer(serializers.ModelSerializer):
#     """
#     Serializer that converts Applicant data to Users model format (API app structure).
#     This serializer returns data in the same format as the API app's Users serializer.
#     """
#     first_name = serializers.SerializerMethodField()
#     middle_name = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
#     age = serializers.SerializerMethodField()
#     nationality = serializers.SerializerMethodField()
#     blood_type = serializers.SerializerMethodField()
#     smoker = serializers.SerializerMethodField()
#     date_of_birth = serializers.SerializerMethodField()
#     marital_status = serializers.SerializerMethodField()
#     place_of_birth = serializers.SerializerMethodField()
#     height_cm = serializers.SerializerMethodField()
#     weight_kg = serializers.SerializerMethodField()

#     # Contact Details
#     email = serializers.SerializerMethodField()
#     phone_number = serializers.SerializerMethodField()
#     address = serializers.SerializerMethodField()

#     # Travel Documents
#     passport_no = serializers.SerializerMethodField()
#     passport_issue_date = serializers.SerializerMethodField()
#     passport_expiry_date = serializers.SerializerMethodField()
#     passport_issued_by = serializers.SerializerMethodField()
#     passport_place_of_issue = serializers.SerializerMethodField()
#     seaman_book_no = serializers.SerializerMethodField()
#     seaman_book_issue_date = serializers.SerializerMethodField()
#     seaman_book_expiry_date = serializers.SerializerMethodField()
#     us_visa_status = serializers.SerializerMethodField()
#     schengen_visa_status = serializers.SerializerMethodField()

#     # Professional Qualifications
#     coc_certificate_name = serializers.SerializerMethodField()
#     coc_certificate_number = serializers.SerializerMethodField()
#     coc_issue_date = serializers.SerializerMethodField()
#     coc_expiry_date = serializers.SerializerMethodField()
#     goc_certificate_number = serializers.SerializerMethodField()
#     goc_issue_date = serializers.SerializerMethodField()
#     goc_expiry_date = serializers.SerializerMethodField()

#     # Next of Kin
#     next_of_kin_full_name = serializers.SerializerMethodField()
#     next_of_kin_relationship = serializers.SerializerMethodField()
#     next_of_kin_phone = serializers.SerializerMethodField()
#     next_of_kin_email = serializers.SerializerMethodField()

#     # Health Certificates
#     health_number = serializers.SerializerMethodField()
#     health_issue_date = serializers.SerializerMethodField()
#     health_expiry_date = serializers.SerializerMethodField()
#     yellow_fever_number = serializers.SerializerMethodField()
#     international_medical_number = serializers.SerializerMethodField()

#     # COVID-19 Vaccination
#     covid_vaccine_name = serializers.SerializerMethodField()
#     covid_first_dose = serializers.SerializerMethodField()
#     covid_second_dose = serializers.SerializerMethodField()

#     # Physical Measurements (NEW)
#     overall_size = serializers.SerializerMethodField()
#     shirt_size = serializers.SerializerMethodField()
#     trouser_size = serializers.SerializerMethodField()
#     shoes_size = serializers.SerializerMethodField()

#     # Language Skills (NEW)
#     english_language_level = serializers.SerializerMethodField()
#     other_language = serializers.SerializerMethodField()
#     other_language_level = serializers.SerializerMethodField()

#     # Medical History (NEW)
#     disease_history = serializers.SerializerMethodField()
#     accident_history = serializers.SerializerMethodField()
#     psychiatric_treatment_history = serializers.SerializerMethodField()
#     addiction_history = serializers.SerializerMethodField()

#     # Assessments (NEW)
#     initial_assessment_comments = serializers.SerializerMethodField()
#     responsible_person_name = serializers.SerializerMethodField()
#     assessment_date = serializers.SerializerMethodField()

#     # Competency Tests (NEW)
#     marlins_test_issued_date = serializers.SerializerMethodField()
#     marlins_test_result = serializers.SerializerMethodField()
#     marlins_test_issued_by = serializers.SerializerMethodField()
#     marlins_test_issued_at = serializers.SerializerMethodField()

#     # Education
#     college_or_school = serializers.SerializerMethodField()

#     # Declaration
#     declaration_consent = serializers.SerializerMethodField()
#     declaration_date = serializers.SerializerMethodField()
#     declaration_place = serializers.SerializerMethodField()

#     # Relationships
#     ranks = RankSerializer(many=True, read_only=True)
#     certificates = CertificateSerializer(many=True, read_only=True)
#     references = ReferenceSerializer(many=True, read_only=True)
#     sea_services = SeaServiceSerializer(many=True, read_only=True)

#     class Meta:
#         model = Applicant
#         fields = [
#             'id', 'email', 'first_name', 'middle_name', 'profile_image', 'age',
#             'blood_type', 'smoker', 'date_of_birth', 'marital_status', 'nationality',
#             'place_of_birth', 'height_cm', 'weight_kg', 'phone_number', 'address',
#             'passport_no', 'passport_issue_date', 'passport_expiry_date',
#             'passport_issued_by', 'passport_place_of_issue', 'seaman_book_no',
#             'seaman_book_issue_date', 'seaman_book_expiry_date', 'us_visa_status',
#             'schengen_visa_status', 'coc_certificate_name', 'coc_certificate_number',
#             'coc_issue_date', 'coc_expiry_date', 'goc_certificate_number',
#             'goc_issue_date', 'goc_expiry_date', 'next_of_kin_full_name',
#             'next_of_kin_relationship', 'next_of_kin_phone', 'next_of_kin_email',
#             'health_number', 'health_issue_date', 'health_expiry_date',
#             'yellow_fever_number', 'international_medical_number',
#             'covid_vaccine_name', 'covid_first_dose', 'covid_second_dose',
#             'overall_size', 'shirt_size', 'trouser_size', 'shoes_size',
#             'english_language_level', 'other_language', 'other_language_level',
#             'disease_history', 'accident_history', 'psychiatric_treatment_history',
#             'addiction_history', 'initial_assessment_comments', 'responsible_person_name',
#             'assessment_date', 'marlins_test_issued_date', 'marlins_test_result',
#             'marlins_test_issued_by', 'marlins_test_issued_at', 'college_or_school',
#             'declaration_consent', 'declaration_date', 'declaration_place',
#             'ranks', 'certificates', 'references', 'sea_services', 'created_at'
#         ]

#     # Personal Details Methods
#     def get_first_name(self, obj):
#         """Extract first name from personal details."""
#         personal_details = obj.personal_details or {}
#         return personal_details.get('first_name', '') or personal_details.get('name', '').split()[0] if personal_details.get('name', '') else ''

#     def get_middle_name(self, obj):
#         """Extract middle name from personal details."""
#         personal_details = obj.personal_details or {}
#         middle_name = personal_details.get('middle_name', '')
#         if not middle_name:
#             full_name = personal_details.get('name', '')
#             if full_name:
#                 name_parts = full_name.split()
#                 if len(name_parts) > 2:
#                     middle_name = ' '.join(name_parts[1:-1])
#         return middle_name

#     def get_profile_image(self, obj):
#         """Return placeholder for profile image."""
#         return None

#     def get_age(self, obj):
#         """Calculate age from date of birth."""
#         personal_details = obj.personal_details or {}
#         birth_date_str = personal_details.get('age', '') or personal_details.get('date_of_birth', '')
#         if isinstance(birth_date_str, int):
#             return birth_date_str
#         if birth_date_str:
#             try:
#                 from datetime import datetime
#                 birth_date = DataMapperService.parse_date_string(birth_date_str)
#                 if birth_date:
#                     today = datetime.now().date()
#                     age = today.year - birth_date.year - (
#                         (today.month, today.day) < (birth_date.month, birth_date.day)
#                     )
#                     return age
#             except Exception:
#                 pass
#         return None

#     def get_nationality(self, obj):
#         """Extract nationality from personal details."""
#         personal_details = obj.personal_details or {}
#         return personal_details.get('nationality', '')

#     def get_blood_type(self, obj):
#         """Extract blood type from personal details."""
#         personal_details = obj.personal_details or {}
#         return personal_details.get('blood_type', '')

#     def get_smoker(self, obj):
#         """Extract smoker status from personal details."""
#         personal_details = obj.personal_details or {}
#         smoker_value = personal_details.get('smoker', False)
#         return smoker_value if isinstance(smoker_value, bool) else False

#     def get_date_of_birth(self, obj):
#         """Extract date of birth from personal details."""
#         personal_details = obj.personal_details or {}
#         birth_date_str = personal_details.get('date_of_birth', '')
#         if birth_date_str:
#             return DataMapperService.parse_date_string(birth_date_str)
#         return None

#     def get_marital_status(self, obj):
#         """Extract marital status from personal details."""
#         personal_details = obj.personal_details or {}
#         return personal_details.get('marital_status', '')

#     def get_place_of_birth(self, obj):
#         """Extract place of birth from personal details."""
#         personal_details = obj.personal_details or {}
#         return personal_details.get('place_of_birth', '')

#     def get_height_cm(self, obj):
#         """Extract height from personal details."""
#         personal_details = obj.personal_details or {}
#         height = personal_details.get('height_cm', 0)
#         return height if isinstance(height, (int, float)) else 0

#     def get_weight_kg(self, obj):
#         """Extract weight from personal details."""
#         personal_details = obj.personal_details or {}
#         weight = personal_details.get('weight_kg', 0)
#         return weight if isinstance(weight, (int, float)) else 0

#     # Contact Details Methods
#     def get_email(self, obj):
#         """Extract email from contact details."""
#         contact_details = obj.contact_details or {}
#         personal_details = obj.personal_details or {}
#         return contact_details.get('email', '') or personal_details.get('email', '')

#     def get_phone_number(self, obj):
#         """Extract phone number from contact details."""
#         contact_details = obj.contact_details or {}
#         return contact_details.get('phone_number', '') or contact_details.get('phone', '')

#     def get_address(self, obj):
#         """Extract address from contact details."""
#         contact_details = obj.contact_details or {}
#         return contact_details.get('address', '')

#     # Travel Documents Methods
#     def get_passport_no(self, obj):
#         """Extract passport number from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         return travel_docs.get('passport_no', '') or travel_docs.get('passport_number', '')

#     def get_passport_issue_date(self, obj):
#         """Extract passport issue date from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         issue_date_str = travel_docs.get('passport_issue_date', '')
#         if issue_date_str:
#             return DataMapperService.parse_date_string(issue_date_str)
#         return None

#     def get_passport_expiry_date(self, obj):
#         """Extract passport expiry date from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         expiry_date_str = travel_docs.get('passport_expiry_date', '')
#         if expiry_date_str:
#             return DataMapperService.parse_date_string(expiry_date_str)
#         return None

#     def get_passport_issued_by(self, obj):
#         """Extract passport issued by from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         return travel_docs.get('passport_issued_by', '')

#     def get_passport_place_of_issue(self, obj):
#         """Extract passport place of issue from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         return travel_docs.get('passport_place_of_issue', '')

#     def get_seaman_book_no(self, obj):
#         """Extract seaman book number from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         return travel_docs.get('seaman_book_no', '')

#     def get_seaman_book_issue_date(self, obj):
#         """Extract seaman book issue date from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         issue_date_str = travel_docs.get('seaman_book_issue_date', '')
#         if issue_date_str:
#             return DataMapperService.parse_date_string(issue_date_str)
#         return None

#     def get_seaman_book_expiry_date(self, obj):
#         """Extract seaman book expiry date from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         expiry_date_str = travel_docs.get('seaman_book_expiry_date', '')
#         if expiry_date_str:
#             return DataMapperService.parse_date_string(expiry_date_str)
#         return None

#     def get_us_visa_status(self, obj):
#         """Extract US visa status from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         return travel_docs.get('us_visa_status', '')

#     def get_schengen_visa_status(self, obj):
#         """Extract Schengen visa status from travel documents."""
#         travel_docs = obj.travel_documents or {}
#         return travel_docs.get('schengen_visa_status', '')

#     # Professional Qualifications Methods
#     def get_coc_certificate_name(self, obj):
#         """Extract COC certificate name from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         return prof_quals.get('coc_certificate_name', '')

#     def get_coc_certificate_number(self, obj):
#         """Extract COC certificate number from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         return prof_quals.get('coc_certificate_number', '')

#     def get_coc_issue_date(self, obj):
#         """Extract COC issue date from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         issue_date_str = prof_quals.get('coc_issue_date', '')
#         if issue_date_str:
#             return DataMapperService.parse_date_string(issue_date_str)
#         return None

#     def get_coc_expiry_date(self, obj):
#         """Extract COC expiry date from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         expiry_date_str = prof_quals.get('coc_expiry_date', '')
#         if expiry_date_str:
#             return DataMapperService.parse_date_string(expiry_date_str)
#         return None

#     def get_goc_certificate_number(self, obj):
#         """Extract GOC certificate number from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         return prof_quals.get('goc_certificate_number', '')

#     def get_goc_issue_date(self, obj):
#         """Extract GOC issue date from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         issue_date_str = prof_quals.get('goc_issue_date', '')
#         if issue_date_str:
#             return DataMapperService.parse_date_string(issue_date_str)
#         return None

#     def get_goc_expiry_date(self, obj):
#         """Extract GOC expiry date from professional qualifications."""
#         prof_quals = obj.professional_qualifications or {}
#         expiry_date_str = prof_quals.get('goc_expiry_date', '')
#         if expiry_date_str:
#             return DataMapperService.parse_date_string(expiry_date_str)
#         return None

#     # Next of Kin Methods
#     def get_next_of_kin_full_name(self, obj):
#         """Extract next of kin full name."""
#         next_of_kin = obj.next_of_kin_emergency_contact or {}
#         return next_of_kin.get('next_of_kin_full_name', '') or next_of_kin.get('name', '')

#     def get_next_of_kin_relationship(self, obj):
#         """Extract next of kin relationship."""
#         next_of_kin = obj.next_of_kin_emergency_contact or {}
#         return next_of_kin.get('next_of_kin_relationship', '') or next_of_kin.get('relationship', '')

#     def get_next_of_kin_phone(self, obj):
#         """Extract next of kin phone."""
#         next_of_kin = obj.next_of_kin_emergency_contact or {}
#         return next_of_kin.get('next_of_kin_phone', '') or next_of_kin.get('phone', '')

#     def get_next_of_kin_email(self, obj):
#         """Extract next of kin email."""
#         next_of_kin = obj.next_of_kin_emergency_contact or {}
#         return next_of_kin.get('next_of_kin_email', '') or next_of_kin.get('email', '')

#     # Health Certificates Methods
#     def get_health_number(self, obj):
#         """Extract health certificate number."""
#         health_certs = obj.health_certificates_vaccinations or {}
#         return health_certs.get('health_number', '')

#     def get_health_issue_date(self, obj):
#         """Extract health certificate issue date."""
#         health_certs = obj.health_certificates_vaccinations or {}
#         issue_date_str = health_certs.get('health_issue_date', '')
#         if issue_date_str:
#             return DataMapperService.parse_date_string(issue_date_str)
#         return None

#     def get_health_expiry_date(self, obj):
#         """Extract health certificate expiry date."""
#         health_certs = obj.health_certificates_vaccinations or {}
#         expiry_date_str = health_certs.get('health_expiry_date', '')
#         if expiry_date_str:
#             return DataMapperService.parse_date_string(expiry_date_str)
#         return None

#     def get_yellow_fever_number(self, obj):
#         """Extract yellow fever certificate number."""
#         health_certs = obj.health_certificates_vaccinations or {}
#         return health_certs.get('yellow_fever_number', '')

#     def get_international_medical_number(self, obj):
#         """Extract international medical certificate number."""
#         health_certs = obj.health_certificates_vaccinations or {}
#         return health_certs.get('international_medical_number', '')

#     # COVID-19 Vaccination Methods
#     def get_covid_vaccine_name(self, obj):
#         """Extract COVID vaccine name."""
#         covid_vacc = obj.covid_19_vaccination or {}
#         return covid_vacc.get('covid_vaccine_name', '') or covid_vacc.get('vaccine_name', '')

#     def get_covid_first_dose(self, obj):
#         """Extract COVID first dose date."""
#         covid_vacc = obj.covid_19_vaccination or {}
#         first_dose_str = covid_vacc.get('covid_first_dose', '') or covid_vacc.get('first_dose', '')
#         if first_dose_str:
#             return DataMapperService.parse_date_string(first_dose_str)
#         return None

#     def get_covid_second_dose(self, obj):
#         """Extract COVID second dose date."""
#         covid_vacc = obj.covid_19_vaccination or {}
#         second_dose_str = covid_vacc.get('covid_second_dose', '') or covid_vacc.get('second_dose', '')
#         if second_dose_str:
#             return DataMapperService.parse_date_string(second_dose_str)
#         return None

#     # Physical Measurements Methods (NEW)
#     def get_overall_size(self, obj):
#         """Extract overall size from physical measurements."""
#         physical_measurements = obj.physical_measurements or {}
#         return physical_measurements.get('overall_size', '')

#     def get_shirt_size(self, obj):
#         """Extract shirt size from physical measurements."""
#         physical_measurements = obj.physical_measurements or {}
#         return physical_measurements.get('shirt_size', '')

#     def get_trouser_size(self, obj):
#         """Extract trouser size from physical measurements."""
#         physical_measurements = obj.physical_measurements or {}
#         return physical_measurements.get('trouser_size', '')

#     def get_shoes_size(self, obj):
#         """Extract shoes size from physical measurements."""
#         physical_measurements = obj.physical_measurements or {}
#         return physical_measurements.get('shoes_size', '')

#     # Language Skills Methods (NEW)
#     def get_english_language_level(self, obj):
#         """Extract English language level from language skills."""
#         language_skills = obj.language_skills or {}
#         return language_skills.get('english_language_level', '')

#     def get_other_language(self, obj):
#         """Extract other language from language skills."""
#         language_skills = obj.language_skills or {}
#         return language_skills.get('other_language', '')

#     def get_other_language_level(self, obj):
#         """Extract other language level from language skills."""
#         language_skills = obj.language_skills or {}
#         return language_skills.get('other_language_level', '')

#     # Medical History Methods (NEW)
#     def get_disease_history(self, obj):
#         """Extract disease history from medical history."""
#         medical_history = obj.medical_history or {}
#         return medical_history.get('disease_history', '')

#     def get_accident_history(self, obj):
#         """Extract accident history from medical history."""
#         medical_history = obj.medical_history or {}
#         return medical_history.get('accident_history', '')

#     def get_psychiatric_treatment_history(self, obj):
#         """Extract psychiatric treatment history from medical history."""
#         medical_history = obj.medical_history or {}
#         return medical_history.get('psychiatric_treatment_history', '')

#     def get_addiction_history(self, obj):
#         """Extract addiction history from medical history."""
#         medical_history = obj.medical_history or {}
#         return medical_history.get('addiction_history', '')

#     # Assessments Methods (NEW)
#     def get_initial_assessment_comments(self, obj):
#         """Extract initial assessment comments from assessments."""
#         assessments = obj.assessments or {}
#         return assessments.get('initial_assessment_comments', '')

#     def get_responsible_person_name(self, obj):
#         """Extract responsible person name from assessments."""
#         assessments = obj.assessments or {}
#         return assessments.get('responsible_person_name', '')

#     def get_assessment_date(self, obj):
#         """Extract assessment date from assessments."""
#         assessments = obj.assessments or {}
#         assessment_date_str = assessments.get('assessment_date', '')
#         if assessment_date_str:
#             return DataMapperService.parse_date_string(assessment_date_str)
#         return None

#     # Competency Tests Methods (NEW)
#     def get_marlins_test_issued_date(self, obj):
#         """Extract Marlins test issued date from competency tests."""
#         competency_tests = obj.competency_tests or {}
#         issued_date_str = competency_tests.get('marlins_test_issued_date', '')
#         if issued_date_str:
#             return DataMapperService.parse_date_string(issued_date_str)
#         return None

#     def get_marlins_test_result(self, obj):
#         """Extract Marlins test result from competency tests."""
#         competency_tests = obj.competency_tests or {}
#         return competency_tests.get('marlins_test_result', '')

#     def get_marlins_test_issued_by(self, obj):
#         """Extract Marlins test issued by from competency tests."""
#         competency_tests = obj.competency_tests or {}
#         return competency_tests.get('marlins_test_issued_by', '')

#     def get_marlins_test_issued_at(self, obj):
#         """Extract Marlins test issued at from competency tests."""
#         competency_tests = obj.competency_tests or {}
#         return competency_tests.get('marlins_test_issued_at', '')

#     # Education Methods
#     def get_college_or_school(self, obj):
#         """Extract college or school from education."""
#         education = obj.education or {}
#         return education.get('college_or_school', '') or education.get('institution', '')

#     # Declaration Methods
#     def get_declaration_consent(self, obj):
#         """Extract declaration consent from declaration."""
#         declaration = obj.declaration or {}
#         consent = declaration.get('declaration_consent', False)
#         return consent if isinstance(consent, bool) else False

#     def get_declaration_date(self, obj):
#         """Extract declaration date from declaration."""
#         declaration = obj.declaration or {}
#         declaration_date_str = declaration.get('declaration_date', '')
#         if declaration_date_str:
#             return DataMapperService.parse_date_string(declaration_date_str)
#         return None

#     def get_declaration_place(self, obj):
#         """Extract declaration place from declaration."""
#         declaration = obj.declaration or {}
#         return declaration.get('declaration_place', '')

#     def to_representation(self, instance):
#         """Override to add dynamic data for relationships."""
#         data = super().to_representation(instance)

#         # Extract certificates from multiple sources
#         certificates_data = DataMapperService.extract_certificates_from_data({
#             'Professional_Qualifications': instance.professional_qualifications or {},
#             'Marine_Courses': instance.marine_courses or {},
#             'Sea_Service_Details': instance.sea_service_details or {},
#             'Competency_Tests': instance.competency_tests or {},
#         })

#         data['certificates'] = [
#             {
#                 'id': idx + 1,
#                 'code': cert_name.upper().replace(' ', '_')[:100],
#                 'name': cert_name
#             }
#             for idx, cert_name in enumerate(certificates_data)
#         ]

#         # Extract references
#         references_data = DataMapperService.extract_references_from_data({
#             'References': instance.references or {}
#         })

#         data['references'] = [
#             {
#                 'id': idx + 1,
#                 'company_name': ref.get('company_name', ''),
#                 'position': ref.get('position', ''),
#                 'name': ref.get('name', ''),
#                 'tel': ref.get('tel', ''),
#                 'email': ref.get('email', '')
#             }
#             for idx, ref in enumerate(references_data)
#         ]

#         # Extract sea services
#         sea_services_data = DataMapperService.extract_sea_services_from_data({
#             'Sea_Service_Details': instance.sea_service_details or {}
#         })

#         data['sea_services'] = [
#             {
#                 'id': idx + 1,
#                 'company_name': service.get('company_name', ''),
#                 'rank': service.get('rank', ''),
#                 'vessel_name_imo': service.get('vessel_name_imo', ''),
#                 'flag': service.get('flag', ''),
#                 'signed_on': service.get('signed_on'),
#                 'signed_off': service.get('signed_off'),
#                 'period': service.get('period', ''),
#                 'vessel_type': service.get('vessel_type', ''),
#                 'dwt': service.get('dwt', ''),
#                 'grt': service.get('grt', ''),
#                 'engine_type': service.get('engine_type', ''),
#                 'bh': service.get('bh', ''),
#                 'kw': service.get('kw', ''),
#                 'reason_for_sign_off': service.get('reason_for_sign_off', '')
#             }
#             for idx, service in enumerate(sea_services_data)
#         ]

#         # Ranks remain empty for now
#         data['ranks'] = []
        
#         return data














"""
COMPLETE FIXED serializers.py
Replace your entire serializers.py with this file.

All errors fixed:
- Proper indentation (all methods inside class)
- No duplicates
- Handles both dict and list formats
- All 88 fields covered
"""

from rest_framework import serializers
from api.serializer import CertificateSerializer, RankSerializer, ReferenceSerializer, SeaServiceSerializer
from .models import Document, Applicant
from .data_mapper_service import DataMapperService
import os


# ============================================================================
# REQUEST VALIDATION SERIALIZERS
# ============================================================================

class DocumentUploadSerializer(serializers.Serializer):
    """Validate file uploads."""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate file type and size."""
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size cannot exceed 50MB. Current: {value.size / (1024*1024):.2f}MB"
            )
        
        allowed_extensions = ['.pdf', '.docx']
        file_extension = os.path.splitext(value.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type '{file_extension}' not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class ConvertApplicantRequestSerializer(serializers.Serializer):
    """Validate single applicant conversion request."""
    applicant_id = serializers.IntegerField(required=True)
    
    def validate_applicant_id(self, value):
        """Validate applicant exists."""
        if not Applicant.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Applicant with ID {value} does not exist")
        return value


class BatchConvertRequestSerializer(serializers.Serializer):
    """Validate batch conversion request."""
    applicant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    convert_all = serializers.BooleanField(required=False, default=False)
    
    def validate(self, data):
        """Validate that either applicant_ids or convert_all is provided."""
        if not data.get('convert_all') and not data.get('applicant_ids'):
            raise serializers.ValidationError(
                "Either 'applicant_ids' or 'convert_all' must be provided"
            )
        return data


class ApplicantListSerializer(serializers.Serializer):
    """Lightweight serializer for listing applicants."""
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    
    def get_name(self, obj):
        """Extract name from personal details."""
        personal_details = obj.personal_details or {}
        return personal_details.get('name', 'Unknown')
    
    def get_email(self, obj):
        """Extract email from contact details."""
        contact_details = obj.contact_details or {}
        return contact_details.get('email', '')
    
    def get_nationality(self, obj):
        """Extract nationality from personal details."""
        personal_details = obj.personal_details or {}
        return personal_details.get('nationality', '')


# ============================================================================
# MAIN APPLICANT SERIALIZER
# ============================================================================

class ApplicantToUsersSerializer(serializers.ModelSerializer):
    """
    Complete serializer for Applicant to Users conversion.
    Handles all 88 fields with support for both dict and list formats.
    """
    
    # Define all SerializerMethodFields
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    middle_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    blood_type = serializers.SerializerMethodField()
    smoker = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    marital_status = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()
    place_of_birth = serializers.SerializerMethodField()
    height_cm = serializers.SerializerMethodField()
    weight_kg = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    
    passport_no = serializers.SerializerMethodField()
    passport_issue_date = serializers.SerializerMethodField()
    passport_expiry_date = serializers.SerializerMethodField()
    passport_issued_by = serializers.SerializerMethodField()
    passport_place_of_issue = serializers.SerializerMethodField()
    seaman_book_no = serializers.SerializerMethodField()
    seaman_book_issue_date = serializers.SerializerMethodField()
    seaman_book_expiry_date = serializers.SerializerMethodField()
    us_visa_status = serializers.SerializerMethodField()
    schengen_visa_status = serializers.SerializerMethodField()
    
    coc_certificate_name = serializers.SerializerMethodField()
    coc_certificate_number = serializers.SerializerMethodField()
    coc_issue_date = serializers.SerializerMethodField()
    coc_expiry_date = serializers.SerializerMethodField()
    goc_certificate_number = serializers.SerializerMethodField()
    goc_issue_date = serializers.SerializerMethodField()
    goc_expiry_date = serializers.SerializerMethodField()
    
    next_of_kin_full_name = serializers.SerializerMethodField()
    next_of_kin_relationship = serializers.SerializerMethodField()
    next_of_kin_phone = serializers.SerializerMethodField()
    next_of_kin_email = serializers.SerializerMethodField()
    
    health_number = serializers.SerializerMethodField()
    health_issue_date = serializers.SerializerMethodField()
    health_expiry_date = serializers.SerializerMethodField()
    yellow_fever_number = serializers.SerializerMethodField()
    international_medical_number = serializers.SerializerMethodField()
    
    covid_vaccine_name = serializers.SerializerMethodField()
    covid_first_dose = serializers.SerializerMethodField()
    covid_second_dose = serializers.SerializerMethodField()
    
    overall_size = serializers.SerializerMethodField()
    shirt_size = serializers.SerializerMethodField()
    trouser_size = serializers.SerializerMethodField()
    shoes_size = serializers.SerializerMethodField()
    
    english_language_level = serializers.SerializerMethodField()
    other_language = serializers.SerializerMethodField()
    other_language_level = serializers.SerializerMethodField()
    
    disease_history = serializers.SerializerMethodField()
    accident_history = serializers.SerializerMethodField()
    psychiatric_treatment_history = serializers.SerializerMethodField()
    addiction_history = serializers.SerializerMethodField()
    
    initial_assessment_comments = serializers.SerializerMethodField()
    responsible_person_name = serializers.SerializerMethodField()
    assessment_date = serializers.SerializerMethodField()
    
    marlins_test_issued_date = serializers.SerializerMethodField()
    marlins_test_result = serializers.SerializerMethodField()
    marlins_test_issued_by = serializers.SerializerMethodField()
    marlins_test_issued_at = serializers.SerializerMethodField()
    
    college_or_school = serializers.SerializerMethodField()
    declaration_consent = serializers.SerializerMethodField()
    declaration_date = serializers.SerializerMethodField()
    declaration_place = serializers.SerializerMethodField()
    
    ranks = RankSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    sea_services = SeaServiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Applicant
        fields = [
            'id', 'email', 'first_name', 'middle_name', 'profile_image', 'age',
            'blood_type', 'smoker', 'date_of_birth', 'marital_status', 'nationality',
            'place_of_birth', 'height_cm', 'weight_kg', 'phone_number', 'address',
            'passport_no', 'passport_issue_date', 'passport_expiry_date',
            'passport_issued_by', 'passport_place_of_issue', 'seaman_book_no',
            'seaman_book_issue_date', 'seaman_book_expiry_date', 'us_visa_status',
            'schengen_visa_status', 'coc_certificate_name', 'coc_certificate_number',
            'coc_issue_date', 'coc_expiry_date', 'goc_certificate_number',
            'goc_issue_date', 'goc_expiry_date', 'next_of_kin_full_name',
            'next_of_kin_relationship', 'next_of_kin_phone', 'next_of_kin_email',
            'health_number', 'health_issue_date', 'health_expiry_date',
            'yellow_fever_number', 'international_medical_number',
            'covid_vaccine_name', 'covid_first_dose', 'covid_second_dose',
            'overall_size', 'shirt_size', 'trouser_size', 'shoes_size',
            'english_language_level', 'other_language', 'other_language_level',
            'disease_history', 'accident_history', 'psychiatric_treatment_history',
            'addiction_history', 'initial_assessment_comments', 'responsible_person_name',
            'assessment_date', 'marlins_test_issued_date', 'marlins_test_result',
            'marlins_test_issued_by', 'marlins_test_issued_at', 'college_or_school',
            'declaration_consent', 'declaration_date', 'declaration_place',
            'ranks', 'certificates', 'references', 'sea_services', 'created_at'
        ]
    
    # ========================================================================
    # HELPER METHOD
    # ========================================================================
    
    def _safe_get(self, data, *keys):
        """Safely get value from dict or list, trying multiple keys."""
        if not data:
            return ''
        
        # Handle list format
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                for key in keys:
                    value = data[0].get(key, '')
                    if value:
                        return value
        
        # Handle dict format
        elif isinstance(data, dict):
            for key in keys:
                value = data.get(key, '')
                if value:
                    return value
        
        return ''
    
    # ========================================================================
    # CONTACT & EMAIL METHODS
    # ========================================================================
    
    def get_email(self, obj):
        """Extract email - CRITICAL."""
        contact_details = getattr(obj, 'contact_details', None)
        if contact_details:
            email = self._safe_get(contact_details, 'Email', 'email')
            if email:
                return email.lower()
        
        personal_details = getattr(obj, 'personal_details', None)
        if personal_details:
            email = self._safe_get(personal_details, 'Email', 'email')
            if email:
                return email.lower()
        
        return ''
    
    def get_phone_number(self, obj):
        """Extract phone number."""
        contact_details = getattr(obj, 'contact_details', None)
        return self._safe_get(contact_details, 'Mobile_Tel', 'phone', 'mobile')
    
    def get_address(self, obj):
        """Extract address."""
        contact_details = getattr(obj, 'contact_details', None)
        return self._safe_get(contact_details, 'Home_Address_City', 'address', 'Address')
    
    # ========================================================================
    # PERSONAL DETAILS METHODS
    # ========================================================================
    
    def get_first_name(self, obj):
        """Extract first name."""
        personal_details = getattr(obj, 'personal_details', None)
        full_name = self._safe_get(personal_details, 'Full_Name', 'name')
        if full_name:
            parts = full_name.split()
            return parts[0] if parts else ''
        return ''
    
    def get_middle_name(self, obj):
        """Extract middle name."""
        personal_details = getattr(obj, 'personal_details', None)
        full_name = self._safe_get(personal_details, 'Full_Name', 'name')
        if full_name:
            parts = full_name.split()
            return ' '.join(parts[1:-1]) if len(parts) > 2 else ''
        return ''
    
    def get_profile_image(self, obj):
        """Extract profile image."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'profile_image')
    
    def get_age(self, obj):
        """Extract age."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Age', 'age')
    
    def get_nationality(self, obj):
        """Extract nationality."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Nationality', 'nationality')
    
    def get_blood_type(self, obj):
        """Extract blood type."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Blood_Type', 'blood_type')
    
    def get_smoker(self, obj):
        """Extract smoker status."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Smoker', 'smoker')
    
    def get_date_of_birth(self, obj):
        """Extract date of birth."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Date_Of_Birth', 'birth_date', 'date_of_birth')
    
    def get_marital_status(self, obj):
        """Extract marital status."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Marital_Status', 'marital_status')
    
    def get_place_of_birth(self, obj):
        """Extract place of birth."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Place_Of_Birth', 'place_of_birth')
    
    def get_height_cm(self, obj):
        """Extract height."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Height_Cm', 'height_cm')
    
    def get_weight_kg(self, obj):
        """Extract weight."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Weight_Kg', 'weight_kg')
    
    # ========================================================================
    # PHYSICAL MEASUREMENTS
    # ========================================================================
    
    def get_overall_size(self, obj):
        """Extract overall size."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Overall_Size', 'overall_size')
    
    def get_shirt_size(self, obj):
        """Extract shirt size."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Shirt_Size', 'shirt_size')
    
    def get_trouser_size(self, obj):
        """Extract trouser size."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Trouser_Size', 'trouser_size')
    
    def get_shoes_size(self, obj):
        """Extract shoes size."""
        personal_details = getattr(obj, 'personal_details', None)
        return self._safe_get(personal_details, 'Shoes_Size', 'shoes_size')
    
    # ========================================================================
    # TRAVEL DOCUMENTS
    # ========================================================================
    
    def _find_document(self, travel_documents, doc_type):
        """Find specific document from travel documents array."""
        if isinstance(travel_documents, list):
            for doc in travel_documents:
                if isinstance(doc, dict) and doc_type in doc.get('Type', ''):
                    return doc
        return None
    
    def get_passport_no(self, obj):
        """Extract passport number."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        passport = self._find_document(travel_documents, 'Passport')
        if passport:
            return passport.get('Document_No', '')
        
        return self._safe_get(travel_documents, 'passport_number', 'passport_no', 'Document_No')
    
    def get_passport_issue_date(self, obj):
        """Extract passport issue date."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        passport = self._find_document(travel_documents, 'Passport')
        if passport:
            return passport.get('ISS_Date', '')
        
        return self._safe_get(travel_documents, 'passport_issue_date', 'ISS_Date')
    
    def get_passport_expiry_date(self, obj):
        """Extract passport expiry date."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        passport = self._find_document(travel_documents, 'Passport')
        if passport:
            return passport.get('Exp_Date', '')
        
        return self._safe_get(travel_documents, 'passport_expiry_date', 'Exp_Date')
    
    def get_passport_issued_by(self, obj):
        """Extract passport issued by."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        passport = self._find_document(travel_documents, 'Passport')
        if passport:
            return passport.get('ISS_By_Authority', '')
        
        return self._safe_get(travel_documents, 'passport_issued_by', 'ISS_By_Authority')
    
    def get_passport_place_of_issue(self, obj):
        """Extract passport place of issue."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        passport = self._find_document(travel_documents, 'Passport')
        if passport:
            return passport.get('Place_of_Issue', '')
        
        return self._safe_get(travel_documents, 'passport_place_of_issue', 'Place_of_Issue')
    
    def get_seaman_book_no(self, obj):
        """Extract seaman book number."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        seaman_book = self._find_document(travel_documents, 'Seaman Book')
        if seaman_book:
            return seaman_book.get('Document_No', '')
        
        return self._safe_get(travel_documents, 'seaman_book_no', 'Document_No')
    
    def get_seaman_book_issue_date(self, obj):
        """Extract seaman book issue date."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        seaman_book = self._find_document(travel_documents, 'Seaman Book')
        if seaman_book:
            return seaman_book.get('ISS_Date', '')
        
        return self._safe_get(travel_documents, 'seaman_book_issue_date', 'ISS_Date')
    
    def get_seaman_book_expiry_date(self, obj):
        """Extract seaman book expiry date."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        seaman_book = self._find_document(travel_documents, 'Seaman Book')
        if seaman_book:
            return seaman_book.get('Exp_Date', '')
        
        return self._safe_get(travel_documents, 'seaman_book_expiry_date', 'Exp_Date')
    
    def get_us_visa_status(self, obj):
        """Extract US visa status."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        us_visa = self._find_document(travel_documents, 'US')
        if us_visa:
            return us_visa.get('Status', '')
        
        return self._safe_get(travel_documents, 'us_visa_status')
    
    def get_schengen_visa_status(self, obj):
        """Extract Schengen visa status."""
        travel_documents = getattr(obj, 'travel_documents', None)
        if not travel_documents:
            return ''
        
        schengen_visa = self._find_document(travel_documents, 'Schengen')
        if schengen_visa:
            return schengen_visa.get('Status', '')
        
        return self._safe_get(travel_documents, 'schengen_visa_status')
    
    # ========================================================================
    # PROFESSIONAL QUALIFICATIONS
    # ========================================================================
    
    def _find_certificate(self, qualifications, cert_type):
        """Find specific certificate from qualifications array."""
        if isinstance(qualifications, list):
            for cert in qualifications:
                if isinstance(cert, dict) and cert_type in cert.get('Certificate_Name', ''):
                    return cert
        return None
    
    def get_coc_certificate_name(self, obj):
        """Extract COC certificate name."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        coc = self._find_certificate(qualifications, 'COC')
        if coc:
            return coc.get('Certificate_Name', '')
        
        return self._safe_get(qualifications, 'coc_certificate_name', 'Certificate_Name')
    
    def get_coc_certificate_number(self, obj):
        """Extract COC certificate number."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        coc = self._find_certificate(qualifications, 'COC')
        if coc:
            return coc.get('Number', '')
        
        return self._safe_get(qualifications, 'coc_certificate_number', 'Number')
    
    def get_coc_issue_date(self, obj):
        """Extract COC issue date."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        coc = self._find_certificate(qualifications, 'COC')
        if coc:
            return coc.get('Issue_Date', '')
        
        return self._safe_get(qualifications, 'coc_issue_date', 'Issue_Date')
    
    def get_coc_expiry_date(self, obj):
        """Extract COC expiry date."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        coc = self._find_certificate(qualifications, 'COC')
        if coc:
            return coc.get('Expiry_Date', '')
        
        return self._safe_get(qualifications, 'coc_expiry_date', 'Expiry_Date')
    
    def get_goc_certificate_number(self, obj):
        """Extract GOC certificate number."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        goc = self._find_certificate(qualifications, 'GOC')
        if goc:
            return goc.get('Number', '')
        
        return self._safe_get(qualifications, 'goc_certificate_number', 'Number')
    
    def get_goc_issue_date(self, obj):
        """Extract GOC issue date."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        goc = self._find_certificate(qualifications, 'GOC')
        if goc:
            return goc.get('Issue_Date', '')
        
        return self._safe_get(qualifications, 'goc_issue_date', 'Issue_Date')
    
    def get_goc_expiry_date(self, obj):
        """Extract GOC expiry date."""
        qualifications = getattr(obj, 'professional_qualifications', None)
        if not qualifications:
            return ''
        
        goc = self._find_certificate(qualifications, 'GOC')
        if goc:
            return goc.get('Expiry_Date', '')
        
        return self._safe_get(qualifications, 'goc_expiry_date', 'Expiry_Date')
    
    # ========================================================================
    # HEALTH CERTIFICATES
    # ========================================================================
    
    def _find_health_cert(self, health_certs, cert_type):
        """Find specific health certificate."""
        if isinstance(health_certs, list):
            for cert in health_certs:
                if isinstance(cert, dict) and cert_type in cert.get('Flag_State', ''):
                    return cert
        return None
    
    def get_health_number(self, obj):
        """Extract health certificate number."""
        health_certs = getattr(obj, 'health_certificates_vaccinations', None)
        if not health_certs:
            return ''
        
        medical = self._find_health_cert(health_certs, 'Medical')
        if medical:
            return medical.get('Number', '')
        
        return self._safe_get(health_certs, 'health_number', 'medical_certificate', 'Number')
    
    def get_health_issue_date(self, obj):
        """Extract health certificate issue date."""
        health_certs = getattr(obj, 'health_certificates_vaccinations', None)
        if not health_certs:
            return ''
        
        medical = self._find_health_cert(health_certs, 'Medical')
        if medical:
            return medical.get('Issue_Date', '')
        
        return self._safe_get(health_certs, 'health_issue_date', 'Issue_Date')
    
    def get_health_expiry_date(self, obj):
        """Extract health certificate expiry date."""
        health_certs = getattr(obj, 'health_certificates_vaccinations', None)
        if not health_certs:
            return ''
        
        medical = self._find_health_cert(health_certs, 'Medical')
        if medical:
            return medical.get('Expiry_Date', '')
        
        return self._safe_get(health_certs, 'health_expiry_date', 'Expiry_Date')
    
    def get_yellow_fever_number(self, obj):
        """Extract yellow fever certificate number."""
        health_certs = getattr(obj, 'health_certificates_vaccinations', None)
        if not health_certs:
            return ''
        
        yellow_fever = self._find_health_cert(health_certs, 'Yellow Fever')
        if yellow_fever:
            return yellow_fever.get('Number', '')
        
        return self._safe_get(health_certs, 'yellow_fever_number', 'Number')
    
    def get_international_medical_number(self, obj):
        """Extract international medical certificate number."""
        health_certs = getattr(obj, 'health_certificates_vaccinations', None)
        if not health_certs:
            return ''
        
        intl_medical = self._find_health_cert(health_certs, 'International Medical')
        if intl_medical:
            return intl_medical.get('Number', '')
        
        return self._safe_get(health_certs, 'international_medical_number', 'Number')
    
    # ========================================================================
    # COVID-19 VACCINATION
    # ========================================================================
    
    def get_covid_vaccine_name(self, obj):
        """Extract COVID vaccine name."""
        covid_vax = getattr(obj, 'covid_19_vaccination', None)
        return self._safe_get(covid_vax, 'Vaccination_Name', 'vaccine_name', 'vaccine_type')
    
    def get_covid_first_dose(self, obj):
        """Extract COVID first dose date."""
        covid_vax = getattr(obj, 'covid_19_vaccination', None)
        return self._safe_get(covid_vax, 'First_Dose', 'first_dose', 'date')
    
    def get_covid_second_dose(self, obj):
        """Extract COVID second dose date."""
        covid_vax = getattr(obj, 'covid_19_vaccination', None)
        return self._safe_get(covid_vax, 'Second_Dose', 'second_dose')
    
    # ========================================================================
    # NEXT OF KIN
    # ========================================================================
    
    def get_next_of_kin_full_name(self, obj):
        """Extract next of kin name."""
        next_of_kin = getattr(obj, 'next_of_kin_emergency_contact', None)
        return self._safe_get(next_of_kin, 'Full_Name', 'name')
    
    def get_next_of_kin_relationship(self, obj):
        """Extract next of kin relationship."""
        next_of_kin = getattr(obj, 'next_of_kin_emergency_contact', None)
        return self._safe_get(next_of_kin, 'Relationship', 'relationship')
    
    def get_next_of_kin_phone(self, obj):
        """Extract next of kin phone."""
        next_of_kin = getattr(obj, 'next_of_kin_emergency_contact', None)
        return self._safe_get(next_of_kin, 'Mobile', 'Tel_No', 'phone')
    
    def get_next_of_kin_email(self, obj):
        """Extract next of kin email."""
        next_of_kin = getattr(obj, 'next_of_kin_emergency_contact', None)
        email = self._safe_get(next_of_kin, 'Email', 'email')
        return email.lower() if email else ''
    
    # ========================================================================
    # EDUCATION & LANGUAGE
    # ========================================================================
    
    def get_college_or_school(self, obj):
        """Extract college or school."""
        education = getattr(obj, 'education', None)
        return self._safe_get(education, 'College_School', 'college', 'school')
    
    def get_english_language_level(self, obj):
        """Extract English language level."""
        education = getattr(obj, 'education', None)
        return self._safe_get(education, 'English_Language', 'english_level')
    
    def get_other_language(self, obj):
        """Extract other language."""
        education = getattr(obj, 'education', None)
        if not education:
            return ''
        
        if isinstance(education, list) and education:
            other_langs = education[0].get('Other_Languages', [])
            if isinstance(other_langs, list) and other_langs:
                return other_langs[0]
        elif isinstance(education, dict):
            other_langs = education.get('Other_Languages', [])
            if isinstance(other_langs, list) and other_langs:
                return other_langs[0]
        
        return ''
    
    def get_other_language_level(self, obj):
        """Extract other language level."""
        return ''  # Not in current schema
    
    # ========================================================================
    # MEDICAL HISTORY
    # ========================================================================
    
    def _get_health_question(self, declaration, question_key):
        """Extract health question from declaration."""
        if not declaration:
            return ''
        
        health_q = {}
        if isinstance(declaration, list) and declaration:
            health_q = declaration[0].get('Health_Questions', {})
        elif isinstance(declaration, dict):
            health_q = declaration.get('Health_Questions', {})
        
        if isinstance(health_q, dict):
            return health_q.get(question_key, '')
        
        return ''
    
    def get_disease_history(self, obj):
        """Extract disease history."""
        declaration = getattr(obj, 'declaration', None)
        return self._get_health_question(declaration, 'Disease_likely_to_render_unfit')
    
    def get_accident_history(self, obj):
        """Extract accident history."""
        declaration = getattr(obj, 'declaration', None)
        return self._get_health_question(declaration, 'Accident_rendering_disabled')
    
    def get_psychiatric_treatment_history(self, obj):
        """Extract psychiatric treatment history."""
        declaration = getattr(obj, 'declaration', None)
        return self._get_health_question(declaration, 'Psychiatric_treatment')
    
    def get_addiction_history(self, obj):
        """Extract addiction history."""
        declaration = getattr(obj, 'declaration', None)
        return self._get_health_question(declaration, 'Addicted_to_alcohol_or_drugs')
    
    # ========================================================================
    # ASSESSMENTS
    # ========================================================================
    
    def _get_marine_test_field(self, education, field_key):
        """Extract marine test field from education."""
        if not education:
            return ''
        
        marine_test = {}
        if isinstance(education, list) and education:
            marine_test = education[0].get('Marine_Test', {})
        elif isinstance(education, dict):
            marine_test = education.get('Marine_Test', {})
        
        if isinstance(marine_test, dict):
            return marine_test.get(field_key, '')
        
        return ''
    
    def get_marlins_test_result(self, obj):
        """Extract Marlins test result."""
        education = getattr(obj, 'education', None)
        return self._get_marine_test_field(education, 'Result_Percent')
    
    def get_marlins_test_issued_date(self, obj):
        """Extract Marlins test issued date."""
        education = getattr(obj, 'education', None)
        return self._get_marine_test_field(education, 'Issued_Date')
    
    def get_marlins_test_issued_by(self, obj):
        """Extract Marlins test issued by."""
        education = getattr(obj, 'education', None)
        return self._get_marine_test_field(education, 'Issued_By_Authority')
    
    def get_marlins_test_issued_at(self, obj):
        """Extract Marlins test issued at."""
        education = getattr(obj, 'education', None)
        return self._get_marine_test_field(education, 'Issued_At')
    
    # ========================================================================
    # DECLARATION
    # ========================================================================
    
    def get_declaration_consent(self, obj):
        """Extract declaration consent."""
        declaration = getattr(obj, 'declaration', None)
        return self._safe_get(declaration, 'Consent_Statement', 'consent')
    
    def get_declaration_date(self, obj):
        """Extract declaration date."""
        declaration = getattr(obj, 'declaration', None)
        return self._safe_get(declaration, 'Date', 'date')
    
    def get_declaration_place(self, obj):
        """Extract declaration place."""
        return ''  # Not in current schema
    
    # ========================================================================
    # OFFICE USE
    # ========================================================================
    
    def get_initial_assessment_comments(self, obj):
        """Extract initial assessment comments."""
        office_use = getattr(obj, 'office_use_only', None)
        return self._safe_get(office_use, 'Comments', 'comments')
    
    def get_responsible_person_name(self, obj):
        """Extract responsible person name."""
        office_use = getattr(obj, 'office_use_only', None)
        return self._safe_get(office_use, 'Responsible_person', 'responsible_person')
    
    def get_assessment_date(self, obj):
        """Extract assessment date."""
        office_use = getattr(obj, 'office_use_only', None)
        return self._safe_get(office_use, 'Date', 'date')
