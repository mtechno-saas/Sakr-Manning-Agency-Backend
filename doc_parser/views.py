

# from django.shortcuts import render
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from .models import ParsedDocument
# from .serializers import ParsedDocumentSerializer
# from .ai_parser_service import extract_document_features
# from api.models import Users
# from api.serializer import UsersSerializer
# import yaml
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# class DocumentUploadViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for uploading seafarer application forms for AI parsing.
#     """
#     queryset = ParsedDocument.objects.all()
#     serializer_class = ParsedDocumentSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     def create(self, request, *args, **kwargs):
#         # Standard file upload handling
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         # Save the initial model instance to get a file path
#         instance = serializer.save()
#         instance.status = 'PROCESSING'
#         instance.save()

#         try:
#             # --- AI Processing Step ---
#             # 1. Extract data from the uploaded document using the AI service
#             extracted_yaml = extract_document_features(instance.source_file.path)
#             if not extracted_yaml:
#                 instance.status = 'FAILED'
#                 instance.save()
#                 return Response(
#                     {"error": "Could not extract data from the document."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # 2. Parse the YAML and create a new user
#             try:
#                 # Handle both YAML and JSON responses
#                 if extracted_yaml.strip().startswith('{') or extracted_yaml.strip().startswith('['):
#                     # It's JSON format
#                     import json
#                     parsed_data = json.loads(extracted_yaml)
#                 else:
#                     # It's YAML format
#                     parsed_data = yaml.safe_load(extracted_yaml)
                
#                 # Handle case where data is wrapped in a "document" key
#                 if isinstance(parsed_data, dict) and "document" in parsed_data:
#                     parsed_data = parsed_data["document"]
                
#                 # If it's a list, take the first item (or most complete one)
#                 if isinstance(parsed_data, list) and len(parsed_data) > 0:
#                     parsed_data = parsed_data[0]
                
#                 user = self._create_user_from_yaml(parsed_data)
                
#                 # Link the created user to the parsed document
#                 instance.associated_user = user
                
#             except Exception as e:
#                 logger.error(f"Error creating user from extracted data: {str(e)}")
#                 logger.error(f"Extracted data was: {extracted_yaml}")
#                 instance.status = 'FAILED'
#                 instance.save()
#                 return Response(
#                     {"error": f"Could not create user from extracted data: {str(e)}"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # 3. Save the result and update the status
#             instance.extracted_data_yaml = extracted_yaml
#             instance.status = 'COMPLETED'
#             instance.save()

#             # Return the successful response with the extracted data and created user info
#             response_data = self.get_serializer(instance).data
#             response_data['created_user_id'] = user.id if user else None
#             response_data['created_user_email'] = user.email if user else None
            
#             headers = self.get_success_headers(serializer.data)
#             return Response(
#                 response_data,
#                 status=status.HTTP_201_CREATED,
#                 headers=headers
#             )

#         except Exception as e:
#             # Handle any errors during AI processing
#             instance.status = 'FAILED'
#             instance.save()
#             return Response(
#                 {"error": f"An error occurred during AI processing: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def _create_user_from_yaml(self, yaml_data):
#         """
#         Create a new Users instance from the parsed YAML data.
#         Maps the extracted document fields to the Users model fields.
#         """
#         if not yaml_data or not isinstance(yaml_data, dict):
#             raise ValueError("Invalid YAML data structure")

#         # Extract and map the fields
#         user_data = {}
        
#         # Basic personal information
#         full_name = yaml_data.get('full_name', '').strip()
#         if full_name:
#             name_parts = full_name.split()
#             user_data['first_name'] = name_parts[0] if name_parts else ''
#             user_data['last_name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
#         # Date fields with proper parsing
#         date_of_birth = self._parse_date(yaml_data.get('date_of_birth'))
#         if date_of_birth:
#             user_data['date_of_birth'] = date_of_birth
#             # Calculate age if date of birth is available
#             today = datetime.today().date()
#             age = today.year - date_of_birth.year
#             if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
#                 age -= 1
#             user_data['age'] = age

#         # Contact information
#         if yaml_data.get('email'):
#             user_data['email'] = yaml_data['email'].strip()
#             user_data['username'] = yaml_data['email'].strip()  # Use email as username
        
#         if yaml_data.get('phone_number'):
#             user_data['phone_number'] = yaml_data['phone_number'].strip()
        
#         if yaml_data.get('address'):
#             user_data['address'] = yaml_data['address'].strip()
        
#         if yaml_data.get('nationality'):
#             user_data['nationality'] = yaml_data['nationality'].strip()
        
#         if yaml_data.get('place_of_birth'):
#             user_data['Place_Of_Birth'] = yaml_data['place_of_birth'].strip()

#         # Travel document fields
#         if yaml_data.get('passport_number'):
#             user_data['passport_no'] = yaml_data['passport_number'].strip()
        
#         passport_issue_date = self._parse_date(yaml_data.get('passport_issue_date'))
#         if passport_issue_date:
#             user_data['passport_issue_date'] = passport_issue_date
            
#         passport_expiry_date = self._parse_date(yaml_data.get('passport_expiry_date'))
#         if passport_expiry_date:
#             user_data['passport_expiry_date'] = passport_expiry_date

#         # Seaman book fields
#         if yaml_data.get('seaman_book_number'):
#             user_data['seaman_book_no'] = yaml_data['seaman_book_number'].strip()
            
#         seaman_book_issue_date = self._parse_date(yaml_data.get('seaman_book_issue_date'))
#         if seaman_book_issue_date:
#             user_data['seaman_book_issue_date'] = seaman_book_issue_date
            
#         seaman_book_expiry_date = self._parse_date(yaml_data.get('seaman_book_expiry_date'))
#         if seaman_book_expiry_date:
#             user_data['seaman_book_expiry_date'] = seaman_book_expiry_date

#         # Ensure required fields are present
#         if not user_data.get('email'):
#             # Generate a temporary email if not provided
#             user_data['email'] = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@tempmail.com"
#             user_data['username'] = user_data['email']
        
#         if not user_data.get('first_name'):
#             user_data['first_name'] = 'Unknown'
        
#         if not user_data.get('last_name'):
#             user_data['last_name'] = 'User'
        
#         if not user_data.get('phone_number'):
#             user_data['phone_number'] = 'Not provided'

#         # Set a default password (you may want to generate a random one and email it)
#         user_data['password'] = 'TempPassword123!'

#         try:
#             # Check if user with this email already exists
#             existing_user = Users.objects.filter(email=user_data['email']).first()
#             if existing_user:
#                 logger.warning(f"User with email {user_data['email']} already exists. Skipping creation.")
#                 return existing_user

#             # Create the user using Django's create_user method
#             user = Users.objects.create_user(
#                 username=user_data['username'],
#                 email=user_data['email'],
#                 password=user_data['password'],
#                 first_name=user_data['first_name'],
#                 last_name=user_data['last_name']
#             )
            
#             # Update additional fields
#             for field, value in user_data.items():
#                 if field not in ['username', 'email', 'password', 'first_name', 'last_name'] and hasattr(user, field):
#                     setattr(user, field, value)
            
#             user.save()
#             logger.info(f"Successfully created user: {user.email}")
#             return user
            
#         except Exception as e:
#             logger.error(f"Error creating user: {str(e)}")
#             raise e

#     def _parse_date(self, date_string):
#         """
#         Parse date string in various formats and return a date object.
#         """
#         if not date_string:
#             return None
            
#         # Try different date formats
#         date_formats = [
#             '%Y-%m-%d',    # 2023-12-31
#             '%d-%m-%Y',    # 31-12-2023
#             '%m/%d/%Y',    # 12/31/2023
#             '%d/%m/%Y',    # 31/12/2023
#             '%Y/%m/%d',    # 2023/12/31
#         ]
        
#         for fmt in date_formats:
#             try:
#                 return datetime.strptime(str(date_string).strip(), fmt).date()
#             except ValueError:
#                 continue
                
#         logger.warning(f"Could not parse date: {date_string}")
#         return None

"""
Enhanced Views for Document Upload with database storage of extracted features.
"""

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import ParsedDocument, ExtractedFeature, DocumentTable, ProcessingLog
from .serializers import ParsedDocumentSerializer
from .ai_parser_service import (
    extract_structured_content_from_docx,
    extract_data_from_document_enhanced,
    extract_data_from_document
)
import logging
import os
import yaml
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class EnhancedDocumentUploadViewSet(viewsets.ModelViewSet):
    """
    Enhanced API endpoint for uploading seafarer application forms for AI parsing.
    Now supports improved DOCX processing with structured data extraction and database storage.
    """
    queryset = ParsedDocument.objects.all()
    serializer_class = ParsedDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Standard file upload handling
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the initial model instance to get a file path
        instance = serializer.save()
        instance.status = 'PROCESSING'
        
        # Log the start of processing
        self._log_processing(instance, 'INFO', 'processing_start', 'Started document processing')
        
        try:
            file_path = instance.source_file.path
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Enhanced processing for DOCX files
            if file_extension == '.docx':
                success = self._process_docx_file(instance, file_path)
            else:
                # Handle other file types (if any) with fallback processing
                success = self._process_other_file(instance, file_path)
            
            if not success:
                instance.status = 'FAILED'
                instance.save()
                self._log_processing(instance, 'ERROR', 'processing_failed', 'Document processing failed')
                return Response(
                    {"error": "Could not process the document. Please ensure it's a valid DOCX file."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Return successful response
            headers = self.get_success_headers(serializer.data)
            return Response(
                self.get_serializer(instance).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        except Exception as e:
            logger.error(f"Error during document processing: {str(e)}")
            instance.status = 'FAILED'
            instance.save()
            self._log_processing(instance, 'ERROR', 'processing_exception', f"Processing exception: {str(e)}")
            return Response(
                {"error": f"An error occurred during document processing: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _process_docx_file(self, instance, file_path: str) -> bool:
        """
        Process DOCX files using the enhanced extraction method and save features to database.
        
        Args:
            instance: ParsedDocument instance
            file_path: Path to the uploaded file
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Step 1: Extract structured content for analysis
            self._log_processing(instance, 'INFO', 'extraction_start', 'Starting structured content extraction')
            
            structured_data = extract_structured_content_from_docx(file_path)
            if not structured_data:
                logger.error("Failed to extract structured content from DOCX")
                self._log_processing(instance, 'ERROR', 'extraction_failed', 'Failed to extract structured content')
                return False
            
            # Step 2: Store raw text and processing metadata
            instance.raw_text = structured_data.get('text', '')
            
            # Store processing metadata
            processing_metadata = {
                'text_length': len(instance.raw_text),
                'tables_found': len(structured_data.get('tables', [])),
                'images_found': len(structured_data.get('images', [])),
                'properties_found': len(structured_data.get('properties', {})),
                'processing_method': 'enhanced_docx_extraction',
                'processed_at': datetime.now().isoformat()
            }
            instance.processing_metadata = processing_metadata
            
            # Step 3: Save tables to database
            self._save_document_tables(instance, structured_data.get('tables', []))
            
            # Step 4: Enhanced AI processing using structured data
            self._log_processing(instance, 'INFO', 'ai_processing_start', 'Starting AI data extraction')
            
            extracted_yaml = extract_data_from_document_enhanced(file_path)
            
            if not extracted_yaml or extracted_yaml.startswith("Error:"):
                logger.error(f"AI extraction failed: {extracted_yaml}")
                self._log_processing(instance, 'ERROR', 'ai_processing_failed', f'AI extraction failed: {extracted_yaml}')
                return False
            
            # Step 5: Parse and save extracted features
            instance.extracted_data_yaml = extracted_yaml
            
            # Parse YAML and save structured features
            success = self._save_extracted_features(instance, extracted_yaml)
            if not success:
                logger.warning("Failed to parse and save extracted features, but continuing with YAML storage")
                self._log_processing(instance, 'WARNING', 'feature_parsing_failed', 'Failed to parse extracted features')
            
            # Step 6: Calculate and log quality metrics
            quality_score = instance.get_extraction_quality_score()
            self._log_processing(
                instance, 
                'INFO', 
                'processing_complete', 
                f'Processing completed with quality score: {quality_score:.1f}%',
                {'quality_score': quality_score, 'metadata': processing_metadata}
            )
            
            # Step 7: Save final results
            instance.status = 'COMPLETED'
            instance.save()
            
            logger.info(f"Successfully processed DOCX file: {file_path} (Quality: {quality_score:.1f}%)")
            return True
            
        except Exception as e:
            logger.error(f"Error processing DOCX file {file_path}: {str(e)}")
            self._log_processing(instance, 'ERROR', 'processing_exception', f"Processing exception: {str(e)}")
            return False

    def _save_document_tables(self, instance, tables_data):
        """
        Save extracted tables to the database.
        
        Args:
            instance: ParsedDocument instance
            tables_data: List of tables from structured extraction
        """
        try:
            for i, table in enumerate(tables_data):
                if table and len(table) > 0:
                    # Determine headers (first row if it looks like headers)
                    headers = []
                    table_data = table
                    
                    if len(table) > 1:
                        first_row = table[0]
                        # Simple heuristic: if first row contains common header words, treat as headers
                        header_indicators = ['name', 'date', 'number', 'type', 'certificate', 'issue', 'expiry']
                        if any(indicator in ' '.join(first_row).lower() for indicator in header_indicators):
                            headers = first_row
                            table_data = table[1:]  # Rest of the table
                    
                    DocumentTable.objects.create(
                        document=instance,
                        table_index=i,
                        table_data=table_data,
                        table_headers=headers,
                        row_count=len(table_data),
                        column_count=len(table_data[0]) if table_data else 0
                    )
            
            self._log_processing(instance, 'INFO', 'tables_saved', f'Saved {len(tables_data)} tables to database')
            
        except Exception as e:
            logger.error(f"Error saving tables: {str(e)}")
            self._log_processing(instance, 'ERROR', 'table_save_failed', f'Failed to save tables: {str(e)}')

    def _save_extracted_features(self, instance, extracted_yaml: str) -> bool:
        """
        Parse YAML and save individual features to the database.
        
        Args:
            instance: ParsedDocument instance
            extracted_yaml: YAML string with extracted data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Parse YAML
            parsed_data = yaml.safe_load(extracted_yaml)
            if not isinstance(parsed_data, dict):
                return False
            
            # Store the full structured data
            instance.extracted_features = parsed_data
            
            # Save individual features for better querying
            feature_count = 0
            
            # Define category mappings
            category_mapping = {
                'personal_information': 'personal',
                'next_of_kin': 'contact',
                'medical_information': 'medical',
                'qualifications': 'qualification',
                'experience': 'experience',
                'preferred_roles': 'other',
                'availability_date': 'other'
            }
            
            for section_name, section_data in parsed_data.items():
                category = category_mapping.get(section_name, 'other')
                
                if isinstance(section_data, dict):
                    # Handle nested dictionaries
                    for field_name, field_value in section_data.items():
                        if field_value and str(field_value).strip():
                            # Calculate confidence score based on value quality
                            confidence = self._calculate_confidence_score(field_value)
                            
                            ExtractedFeature.objects.update_or_create(
                                document=instance,
                                field_name=f"{section_name}.{field_name}",
                                defaults={
                                    'category': category,
                                    'field_value': str(field_value),
                                    'confidence_score': confidence,
                                    'extraction_method': 'ai_extraction'
                                }
                            )
                            feature_count += 1
                            
                elif isinstance(section_data, list):
                    # Handle lists (like preferred_roles)
                    ExtractedFeature.objects.update_or_create(
                        document=instance,
                        field_name=section_name,
                        defaults={
                            'category': category,
                            'field_value': json.dumps(section_data),
                            'confidence_score': 0.8,  # Lists are usually well-extracted
                            'extraction_method': 'ai_extraction'
                        }
                    )
                    feature_count += 1
                    
                else:
                    # Handle simple values
                    if section_data and str(section_data).strip():
                        confidence = self._calculate_confidence_score(section_data)
                        
                        ExtractedFeature.objects.update_or_create(
                            document=instance,
                            field_name=section_name,
                            defaults={
                                'category': category,
                                'field_value': str(section_data),
                                'confidence_score': confidence,
                                'extraction_method': 'ai_extraction'
                            }
                        )
                        feature_count += 1
            
            self._log_processing(instance, 'INFO', 'features_saved', f'Saved {feature_count} features to database')
            return True
            
        except Exception as e:
            logger.error(f"Error saving extracted features: {str(e)}")
            self._log_processing(instance, 'ERROR', 'feature_save_failed', f'Failed to save features: {str(e)}')
            return False

    def _calculate_confidence_score(self, value) -> float:
        """
        Calculate a confidence score for an extracted value.
        
        Args:
            value: The extracted value
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        if not value or str(value).strip() == "":
            return 0.0
        
        value_str = str(value).strip()
        
        # Very low confidence for "Not Available" or similar
        if value_str.lower() in ['not available', 'n/a', 'na', 'none', 'null']:
            return 0.1
        
        # Higher confidence for structured data (dates, emails, etc.)
        import re
        
        # Email pattern
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value_str):
            return 0.95
        
        # Date pattern (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
            return 0.9
        
        # Phone number pattern
        if re.match(r'^[\+]?[\d\s\-\(\)]{10,}$', value_str):
            return 0.85
        
        # Longer text generally more reliable
        if len(value_str) > 20:
            return 0.8
        elif len(value_str) > 10:
            return 0.7
        elif len(value_str) > 3:
            return 0.6
        else:
            return 0.5

    def _log_processing(self, instance, level: str, step: str, message: str, extra_data: dict = None):
        """
        Log processing steps to the database.
        
        Args:
            instance: ParsedDocument instance
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            step: Processing step name
            message: Log message
            extra_data: Additional structured data
        """
        try:
            ProcessingLog.objects.create(
                document=instance,
                level=level,
                step=step,
                message=message,
                extra_data=extra_data or {}
            )
        except Exception as e:
            # Don't let logging errors break the main process
            logger.error(f"Failed to create processing log: {str(e)}")

    def _process_other_file(self, instance, file_path: str) -> bool:
        """
        Process non-DOCX files using fallback methods.
        
        Args:
            instance: ParsedDocument instance
            file_path: Path to the uploaded file
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # For now, we only support DOCX files
            # This method can be extended to support other formats like PDF, TXT, etc.
            logger.warning(f"Unsupported file type: {file_path}")
            self._log_processing(instance, 'WARNING', 'unsupported_format', f'Unsupported file type: {file_path}')
            return False
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            self._log_processing(instance, 'ERROR', 'processing_exception', f"Processing exception: {str(e)}")
            return False

    @action(detail=True, methods=['get'])
    def features(self, request, pk=None):
        """
        Get extracted features for a specific document.
        """
        document = self.get_object()
        features = ExtractedFeature.objects.filter(document=document).order_by('category', 'field_name')
        
        # Group features by category
        grouped_features = {}
        for feature in features:
            if feature.category not in grouped_features:
                grouped_features[feature.category] = []
            
            grouped_features[feature.category].append({
                'field_name': feature.field_name,
                'field_value': feature.field_value,
                'confidence_score': feature.confidence_score,
                'extraction_method': feature.extraction_method
            })
        
        return Response({
            'document_id': document.id,
            'features_by_category': grouped_features,
            'total_features': features.count(),
            'quality_score': document.get_extraction_quality_score()
        })

    @action(detail=True, methods=['get'])
    def tables(self, request, pk=None):
        """
        Get extracted tables for a specific document.
        """
        document = self.get_object()
        tables = DocumentTable.objects.filter(document=document).order_by('table_index')
        
        tables_data = []
        for table in tables:
            tables_data.append({
                'table_index': table.table_index,
                'headers': table.table_headers,
                'data': table.table_data,
                'row_count': table.row_count,
                'column_count': table.column_count
            })
        
        return Response({
            'document_id': document.id,
            'tables': tables_data,
            'total_tables': len(tables_data)
        })

    @action(detail=True, methods=['get'])
    def processing_logs(self, request, pk=None):
        """
        Get processing logs for a specific document.
        """
        document = self.get_object()
        logs = ProcessingLog.objects.filter(document=document).order_by('-created_at')
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'level': log.level,
                'step': log.step,
                'message': log.message,
                'extra_data': log.extra_data,
                'created_at': log.created_at
            })
        
        return Response({
            'document_id': document.id,
            'logs': logs_data,
            'total_logs': len(logs_data)
        })

    def list(self, request, *args, **kwargs):
        """
        Override list method to provide additional information about processing capabilities.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add metadata about supported formats and processing capabilities
        if isinstance(response.data, dict) and 'results' in response.data:
            response.data['supported_formats'] = ['docx']
            response.data['processing_features'] = [
                'Structured content extraction',
                'Table data extraction and storage',
                'Individual feature extraction and storage',
                'Document properties extraction',
                'Enhanced AI processing',
                'Quality scoring',
                'Processing logs and monitoring'
            ]
        
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve method to provide additional processing details.
        """
        response = super().retrieve(request, *args, **kwargs)
        
        # Add processing metadata and feature summary
        instance = self.get_object()
        if instance.status == 'COMPLETED':
            feature_count = ExtractedFeature.objects.filter(document=instance).count()
            table_count = DocumentTable.objects.filter(document=instance).count()
            
            response.data['processing_info'] = {
                'text_length': len(instance.raw_text) if instance.raw_text else 0,
                'processing_method': instance.processing_metadata.get('processing_method', 'unknown'),
                'has_structured_data': bool(instance.extracted_features),
                'feature_count': feature_count,
                'table_count': table_count,
                'quality_score': instance.get_extraction_quality_score(),
                'processing_metadata': instance.processing_metadata
            }
        
        return response


# Backward compatibility - keep the original class name as an alias
class DocumentUploadViewSet(EnhancedDocumentUploadViewSet):
    """
    Backward compatibility alias for the enhanced document upload viewset.
    """
    pass
