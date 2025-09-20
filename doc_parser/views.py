

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

# """
# Fixed views that properly save extracted features and tables to the database.
# """

# from django.shortcuts import render
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.decorators import action
# from .models import ParsedDocument, ExtractedFeature, DocumentTable, ProcessingLog
# from .serializers import ParsedDocumentSerializer, ParsedDocumentSummarySerializer
# import logging
# import os
# import yaml
# import json
# import traceback
# from datetime import datetime
# from typing import Dict, Any, List, Tuple

# logger = logging.getLogger(__name__)


# class DocumentUploadViewSet(viewsets.ModelViewSet):
#     """
#     Fixed document upload viewset that properly saves all extracted data to database.
#     """
#     queryset = ParsedDocument.objects.all()
#     serializer_class = ParsedDocumentSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     def create(self, request, *args, **kwargs):
#         """
#         Handle document upload with comprehensive database saving.
#         """
#         try:
#             # Basic validation
#             if 'source_file' not in request.data:
#                 return Response(
#                     {'error': 'No file provided. Please upload a file with key "source_file"'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             uploaded_file = request.data['source_file']
            
#             # File type validation
#             if not uploaded_file.name.lower().endswith('.docx'):
#                 return Response(
#                     {'error': f'Unsupported file type: {uploaded_file.name}. Only .docx files are supported.'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Create document instance
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             instance = serializer.save()
            
#             # Log initial state
#             self._log_processing(instance, 'INFO', 'upload_start', f'File uploaded: {uploaded_file.name}')
            
#             # Set processing status
#             instance.status = 'PROCESSING'
#             instance.save()
            
#             # Process document with comprehensive feature saving
#             try:
#                 result = self._process_document_comprehensive(instance)
                
#                 if result['success']:
#                     instance.status = 'COMPLETED'
#                     instance.save()
                    
#                     # Return comprehensive response
#                     response_data = self.get_serializer(instance).data
#                     response_data['processing_result'] = result
                    
#                     return Response(response_data, status=status.HTTP_201_CREATED)
#                 else:
#                     instance.status = 'FAILED'
#                     instance.save()
                    
#                     return Response({
#                         'error': 'Processing failed',
#                         'details': result
#                     }, status=status.HTTP_400_BAD_REQUEST)
                    
#             except Exception as processing_error:
#                 instance.status = 'FAILED'
#                 instance.save()
                
#                 error_details = {
#                     'error': str(processing_error),
#                     'traceback': traceback.format_exc(),
#                     'file_path': instance.source_file.path if instance.source_file else 'No file path',
#                     'file_exists': os.path.exists(instance.source_file.path) if instance.source_file else False
#                 }
                
#                 self._log_processing(instance, 'ERROR', 'processing_error', 
#                                    f'Processing failed: {str(processing_error)}', error_details)
                
#                 return Response({
#                     'error': 'Document processing failed',
#                     'details': error_details
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
#         except Exception as e:
#             return Response({
#                 'error': f'Upload failed: {str(e)}',
#                 'traceback': traceback.format_exc()
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def _process_document_comprehensive(self, instance):
#         """
#         Process document with comprehensive feature extraction and database saving.
#         """
#         result = {
#             'success': False,
#             'steps': [],
#             'errors': [],
#             'file_info': {},
#             'extraction_stats': {}
#         }
        
#         try:
#             file_path = instance.source_file.path
            
#             # Step 1: File validation
#             result['steps'].append('file_validation')
#             result['file_info'] = {
#                 'path': file_path,
#                 'exists': os.path.exists(file_path),
#                 'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
#                 'extension': os.path.splitext(file_path)[1].lower()
#             }
            
#             if not os.path.exists(file_path):
#                 result['errors'].append('File does not exist')
#                 return result
            
#             if result['file_info']['size'] == 0:
#                 result['errors'].append('File is empty')
#                 return result
            
#             # Step 2: DOCX content extraction
#             result['steps'].append('docx_extraction')
            
#             try:
#                 from .ai_parser_service import SeafarerFieldExtractor
#                 extractor = SeafarerFieldExtractor()
                
#                 structured_data = extractor.extract_structured_content_from_docx(file_path)
                
#                 if structured_data:
#                     result['extraction_info'] = {
#                         'text_length': len(structured_data.get('text', '')),
#                         'tables_found': len(structured_data.get('tables', [])),
#                         'images_found': len(structured_data.get('images', [])),
#                         'properties_found': len(structured_data.get('properties', {})),
#                         'method': structured_data.get('extraction_method', 'unknown')
#                     }
                    
#                     # Store raw text
#                     instance.raw_text = structured_data.get('text', '')
                    
#                     # Save tables to database
#                     self._save_document_tables(instance, structured_data.get('tables', []))
                    
#                 else:
#                     result['errors'].append('Failed to extract DOCX content')
#                     return result
                    
#             except Exception as e:
#                 result['errors'].append(f'DOCX extraction failed: {str(e)}')
#                 return result
            
#             # Step 3: AI Processing
#             result['steps'].append('ai_processing')
            
#             try:
#                 extracted_data, metadata = extractor.extract_from_document(file_path)
                
#                 if extracted_data:
#                     result['ai_extraction'] = {
#                         'categories_found': list(extracted_data.keys()),
#                         'metadata': metadata
#                     }
                    
#                     # Store extracted data
#                     instance.extracted_data_yaml = yaml.dump(extracted_data, default_flow_style=False)
#                     instance.processing_metadata = metadata
#                     instance.extracted_features = extracted_data
                    
#                     # Save comprehensive features to database
#                     self._save_comprehensive_features(instance, extracted_data)
                    
#                     # Extract and save sea service records
#                     self._extract_and_save_sea_service(instance, extracted_data, structured_data.get('tables', []))
                    
#                 else:
#                     result['errors'].append(f'AI extraction failed: {metadata.get("error", "Unknown error")}')
#                     return result
                    
#             except Exception as e:
#                 result['errors'].append(f'AI processing failed: {str(e)}')
#                 return result
            
#             # Step 4: Save results and calculate stats
#             result['steps'].append('saving_results')
#             instance.save()
            
#             # Calculate final stats
#             feature_count = ExtractedFeature.objects.filter(document=instance).count()
#             table_count = DocumentTable.objects.filter(document=instance).count()
#             quality_score = instance.get_extraction_quality_score()
            
#             result['extraction_stats'] = {
#                 'features_saved': feature_count,
#                 'tables_saved': table_count,
#                 'quality_score': quality_score
#             }
            
#             # Success
#             result['success'] = True
#             result['final_status'] = 'completed'
            
#             self._log_processing(instance, 'INFO', 'processing_complete', 
#                                f'Processing completed successfully. Features: {feature_count}, Quality: {quality_score:.1f}%', 
#                                result)
            
#             return result
            
#         except Exception as e:
#             result['errors'].append(f'Unexpected error: {str(e)}')
#             result['traceback'] = traceback.format_exc()
#             self._log_processing(instance, 'ERROR', 'processing_exception', 
#                                f'Processing exception: {str(e)}')
#             return result

#     def _save_document_tables(self, instance: ParsedDocument, tables_data: List[List[List[str]]]):
#         """
#         Save extracted tables to the database.
#         """
#         try:
#             saved_count = 0
            
#             for i, table in enumerate(tables_data):
#                 if table and len(table) > 0:
#                     # Enhanced header detection
#                     headers, table_data = self._detect_table_headers(table)
                    
#                     DocumentTable.objects.create(
#                         document=instance,
#                         table_index=i,
#                         table_data=table_data,
#                         table_headers=headers,
#                         row_count=len(table_data),
#                         column_count=len(table_data[0]) if table_data else 0
#                     )
#                     saved_count += 1
            
#             self._log_processing(instance, 'INFO', 'tables_saved', 
#                                f'Saved {saved_count} tables to database')
            
#         except Exception as e:
#             logger.error(f"Error saving document tables: {str(e)}")
#             self._log_processing(instance, 'ERROR', 'table_save_error', 
#                                f'Failed to save tables: {str(e)}')

#     def _detect_table_headers(self, table: List[List[str]]) -> Tuple[List[str], List[List[str]]]:
#         """
#         Enhanced header detection for tables.
#         """
#         if not table or len(table) < 2:
#             return [], table
        
#         first_row = table[0]
        
#         # Header detection heuristics
#         header_indicators = [
#             'name', 'date', 'number', 'type', 'certificate', 'issue', 'expiry',
#             'vessel', 'company', 'rank', 'flag', 'sign', 'course', 'training'
#         ]
        
#         # Check if first row contains header-like words
#         first_row_text = ' '.join(first_row).lower()
#         header_score = sum(1 for indicator in header_indicators if indicator in first_row_text)
        
#         # Decide if first row is headers
#         if header_score >= 2:
#             return first_row, table[1:]
        
#         return [], table

#     def _save_comprehensive_features(self, instance: ParsedDocument, extracted_data: Dict[str, Any]):
#         """
#         Save all extracted features to the database with comprehensive field mapping.
#         """
#         try:
#             feature_count = 0
            
#             # Category mapping for database storage
#             category_mapping = {
#                 'personal_information': 'personal',
#                 'contact_information': 'contact',
#                 'travel_documents': 'document',
#                 'medical_information': 'medical',
#                 'qualifications': 'qualification',
#                 'stcw_training': 'qualification',
#                 'sea_service': 'experience',
#                 'education': 'personal',
#                 'preferences': 'other'
#             }
            
#             # Process each category of extracted data
#             for section_name, section_data in extracted_data.items():
#                 if not isinstance(section_data, dict):
#                     continue
                    
#                 category = category_mapping.get(section_name, 'other')
                
#                 for field_name, field_value in section_data.items():
#                     if field_name == 'vessels':  # Handle vessels separately
#                         continue
                        
#                     if field_value and str(field_value).strip() and str(field_value) != "Not Available":
#                         # Calculate confidence score
#                         confidence = self._calculate_field_confidence(field_name, field_value)
                        
#                         # Create or update feature
#                         feature, created = ExtractedFeature.objects.update_or_create(
#                             document=instance,
#                             field_name=f"{section_name}.{field_name}",
#                             defaults={
#                                 'category': category,
#                                 'field_value': str(field_value),
#                                 'confidence_score': confidence,
#                                 'extraction_method': 'ai_comprehensive'
#                             }
#                         )
                        
#                         if created:
#                             feature_count += 1
            
#             self._log_processing(instance, 'INFO', 'features_saved',
#                                f'Saved {feature_count} comprehensive features to database')
            
#         except Exception as e:
#             logger.error(f"Error saving comprehensive features: {str(e)}")
#             self._log_processing(instance, 'ERROR', 'feature_save_error',
#                                f'Failed to save features: {str(e)}')

#     def _extract_and_save_sea_service(self, instance: ParsedDocument, extracted_data: Dict[str, Any], tables_data: List[List[List[str]]]):
#         """
#         Extract and save detailed sea service records from tables.
#         """
#         try:
#             vessel_count = 0
            
#             # Look for vessel service tables
#             for table in tables_data:
#                 if self._is_vessel_table(table):
#                     vessels = self._parse_vessel_table(table)
                    
#                     # Save each vessel as individual features
#                     for i, vessel in enumerate(vessels):
#                         for field, value in vessel.items():
#                             if value and str(value).strip():
#                                 ExtractedFeature.objects.update_or_create(
#                                     document=instance,
#                                     field_name=f"sea_service.vessel_{vessel_count + 1}_{field}",
#                                     defaults={
#                                         'category': 'experience',
#                                         'field_value': str(value),
#                                         'confidence_score': 0.8,
#                                         'extraction_method': 'table_parsing'
#                                     }
#                                 )
#                         vessel_count += 1
            
#             if vessel_count > 0:
#                 self._log_processing(instance, 'INFO', 'vessels_extracted',
#                                    f'Extracted and saved {vessel_count} vessel service records')
            
#         except Exception as e:
#             logger.error(f"Error extracting sea service: {str(e)}")
#             self._log_processing(instance, 'ERROR', 'vessel_extraction_error',
#                                f'Failed to extract vessel data: {str(e)}')

#     def _is_vessel_table(self, table: List[List[str]]) -> bool:
#         """
#         Check if a table contains vessel/sea service information.
#         """
#         if not table or len(table) < 2:
#             return False
        
#         # Look for vessel-related terms in the table
#         table_text = ' '.join([' '.join(row) for row in table[:3]]).lower()
        
#         vessel_indicators = [
#             'vessel', 'ship', 'company', 'rank', 'sign', 'flag', 
#             'dwt', 'grt', 'engine', 'type', 'salamis', 'cargo', 'passenger'
#         ]
        
#         indicator_count = sum(1 for indicator in vessel_indicators if indicator in table_text)
#         return indicator_count >= 3

#     def _parse_vessel_table(self, table: List[List[str]]) -> List[Dict[str, str]]:
#         """
#         Parse vessel information from table data.
#         """
#         vessels = []
        
#         try:
#             if not table or len(table) < 2:
#                 return vessels
            
#             # Find header row and data rows
#             headers = []
#             data_start_idx = 0
            
#             # Look for a row that looks like headers
#             for i, row in enumerate(table[:3]):  # Check first 3 rows
#                 row_text = ' '.join(row).lower()
#                 if any(term in row_text for term in ['company', 'vessel', 'rank', 'signed']):
#                     headers = [col.strip().lower() for col in row]
#                     data_start_idx = i + 1
#                     break
            
#             # If no clear headers found, use positional mapping based on common patterns
#             if not headers and len(table[0]) >= 6:
#                 # Common pattern: Company, Rank, Vessel, Flag, Sign On, Sign Off, ...
#                 headers = ['company', 'rank', 'vessel_name', 'flag', 'sign_on', 'sign_off', 'vessel_type', 'dwt']
#                 data_start_idx = 1
            
#             # Process data rows
#             for row in table[data_start_idx:]:
#                 if len(row) >= 4:  # Minimum viable vessel record
#                     vessel = {}
                    
#                     # Map fields based on headers or position
#                     if headers:
#                         for i, value in enumerate(row):
#                             if i < len(headers) and value and value.strip():
#                                 field_name = self._normalize_field_name(headers[i])
#                                 vessel[field_name] = value.strip()
#                     else:
#                         # Fallback positional mapping
#                         if len(row) > 0 and row[0].strip():
#                             vessel['company'] = row[0].strip()
#                         if len(row) > 1 and row[1].strip():
#                             vessel['rank'] = row[1].strip()
#                         if len(row) > 2 and row[2].strip():
#                             vessel['vessel_name'] = row[2].strip()
#                         if len(row) > 3 and row[3].strip():
#                             vessel['flag'] = row[3].strip()
                    
#                     # Only add if we have at least vessel name or company
#                     if vessel.get('vessel_name') or vessel.get('company'):
#                         vessels.append(vessel)
        
#         except Exception as e:
#             logger.error(f"Error parsing vessel table: {str(e)}")
        
#         return vessels

#     def _normalize_field_name(self, field_name: str) -> str:
#         """
#         Normalize field names for consistent storage.
#         """
#         field_name = field_name.lower().strip()
        
#         # Field name mappings
#         mappings = {
#             'vessel name': 'vessel_name',
#             'company name': 'company',
#             'signed on': 'sign_on',
#             'signed off': 'sign_off',
#             'vessel type': 'vessel_type',
#             'engine type': 'engine_type',
#             'd.w.t.': 'dwt',
#             'bh': 'engine_power',
#             'kw': 'engine_power'
#         }
        
#         return mappings.get(field_name, field_name.replace(' ', '_').replace('.', ''))

#     def _calculate_field_confidence(self, field_name: str, field_value: Any) -> float:
#         """
#         Calculate confidence score for extracted field.
#         """
#         if not field_value or str(field_value).strip() == "":
#             return 0.0
        
#         value_str = str(field_value).strip()
        
#         # Very low confidence for placeholder values
#         if value_str.lower() in ['not available', 'n/a', 'na', 'none', 'null', 'unknown']:
#             return 0.1
        
#         import re
        
#         # High confidence patterns
#         confidence_patterns = {
#             # Email
#             r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$': 0.95,
#             # Date (YYYY-MM-DD)
#             r'^\d{4}-\d{2}-\d{2}$': 0.9,
#             # Date (DD/MM/YYYY)
#             r'^\d{1,2}/\d{1,2}/\d{4}$': 0.85,
#             # Phone number
#             r'^[\+]?[\d\s\-\(\)]{10,}$': 0.85,
#             # Certificate numbers
#             r'^[A-Z0-9]{5,}$': 0.8,
#             # Names (multiple words)
#             r'^[A-Z][a-z]+(?: [A-Z][a-z]+)+$': 0.75
#         }
        
#         # Check for high-confidence patterns
#         for pattern, confidence in confidence_patterns.items():
#             if re.match(pattern, value_str):
#                 return confidence
        
#         # Field-specific confidence
#         if 'date' in field_name.lower() and len(value_str) >= 8:
#             return 0.8
#         elif 'number' in field_name.lower() and value_str.isalnum():
#             return 0.75
#         elif 'name' in field_name.lower() and len(value_str.split()) >= 2:
#             return 0.7
        
#         # Length-based confidence
#         if len(value_str) > 30:
#             return 0.8
#         elif len(value_str) > 15:
#             return 0.7
#         elif len(value_str) > 5:
#             return 0.6
#         else:
#             return 0.5

#     def _log_processing(self, instance: ParsedDocument, level: str, step: str, 
#                         message: str, extra_data: Dict[str, Any] = None):
#         """
#         Create a processing log entry.
#         """
#         try:
#             ProcessingLog.objects.create(
#                 document=instance,
#                 level=level,
#                 step=step,
#                 message=message,
#                 extra_data=extra_data or {}
#             )
#         except Exception as e:
#             logger.error(f"Failed to create processing log: {str(e)}")

#     # Debug and utility endpoints
#     @action(detail=False, methods=['get'])
#     def check_dependencies(self, request):
#         """
#         Check if all required dependencies are available.
#         """
#         try:
#             from .ai_parser_service import SeafarerFieldExtractor
            
#             # Initialize extractor
#             extractor = SeafarerFieldExtractor()
            
#             # Check dependencies
#             deps_ok, dep_errors = extractor.check_dependencies()
            
#             # Additional checks
#             checks = {
#                 'dependencies_ok': deps_ok,
#                 'dependency_errors': dep_errors,
#                 'ollama_service': self._check_ollama_service(),
#                 'docx_libraries': self._check_docx_libraries(),
#                 'file_system': self._check_file_system(),
#             }
            
#             return Response(checks)
            
#         except Exception as e:
#             return Response({
#                 'error': f"Failed to check dependencies: {str(e)}",
#                 'traceback': traceback.format_exc()
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def _check_ollama_service(self):
#         """Check if Ollama service is accessible."""
#         try:
#             from .ai_parser_service import SeafarerFieldExtractor
#             extractor = SeafarerFieldExtractor()
            
#             if extractor.llm:
#                 # Try a simple test
#                 response = extractor.llm.invoke("Hello")
#                 return {
#                     'status': 'ok',
#                     'message': 'Ollama service is accessible',
#                     'test_response_length': len(response) if response else 0
#                 }
#             else:
#                 return {
#                     'status': 'error',
#                     'message': f'Ollama LLM not initialized: {extractor.initialization_error}'
#                 }
#         except Exception as e:
#             return {
#                 'status': 'error',
#                 'message': f'Ollama check failed: {str(e)}'
#             }

#     def _check_docx_libraries(self):
#         """Check which DOCX libraries are available."""
#         libraries = {}
        
#         try:
#             from docx2python import docx2python
#             libraries['docx2python'] = 'available'
#         except ImportError:
#             libraries['docx2python'] = 'not installed'
        
#         try:
#             from docx import Document
#             libraries['python_docx'] = 'available'
#         except ImportError:
#             libraries['python_docx'] = 'not installed'
        
#         return libraries

#     def _check_file_system(self):
#         """Check file system permissions and paths."""
#         try:
#             from django.conf import settings
            
#             media_root = getattr(settings, 'MEDIA_ROOT', 'media/')
#             source_docs_path = os.path.join(media_root, 'source_documents')
            
#             return {
#                 'media_root': media_root,
#                 'media_root_exists': os.path.exists(media_root),
#                 'media_root_writable': os.access(media_root, os.W_OK) if os.path.exists(media_root) else False,
#                 'source_documents_path': source_docs_path,
#                 'source_documents_exists': os.path.exists(source_docs_path),
#                 'source_documents_writable': os.access(source_docs_path, os.W_OK) if os.path.exists(source_docs_path) else False
#             }
#         except Exception as e:
#             return {'error': str(e)}

#     @action(detail=True, methods=['get'])
#     def debug_info(self, request, pk=None):
#         """
#         Get detailed debug information for a specific document.
#         """
#         document = self.get_object()
        
#         # Get feature and table counts
#         feature_count = ExtractedFeature.objects.filter(document=document).count()
#         table_count = DocumentTable.objects.filter(document=document).count()
        
#         debug_info = {
#             'document_info': {
#                 'id': document.id,
#                 'status': document.status,
#                 'file_name': document.source_file.name if document.source_file else None,
#                 'file_path': document.source_file.path if document.source_file else None,
#                 'file_exists': os.path.exists(document.source_file.path) if document.source_file else False,
#                 'created_at': document.created_at,
#                 'updated_at': document.updated_at
#             },
#             'extraction_summary': {
#                 'features_in_db': feature_count,
#                 'tables_in_db': table_count,
#                 'quality_score': document.get_extraction_quality_score(),
#                 'has_extracted_features': bool(document.extracted_features),
#                 'extracted_data_length': len(document.extracted_data_yaml) if document.extracted_data_yaml else 0,
#                 'raw_text_length': len(document.raw_text) if document.raw_text else 0,
#                 'processing_metadata': document.processing_metadata
#             },
#             'processing_logs': []
#         }
        
#         # Get processing logs
#         logs = ProcessingLog.objects.filter(document=document).order_by('created_at')
#         for log in logs:
#             debug_info['processing_logs'].append({
#                 'level': log.level,
#                 'step': log.step,
#                 'message': log.message,
#                 'extra_data': log.extra_data,
#                 'created_at': log.created_at
#             })
        
#         # Get sample features if available
#         sample_features = ExtractedFeature.objects.filter(document=document)[:10]
#         debug_info['sample_features'] = [
#             {
#                 'field_name': f.field_name,
#                 'field_value': f.field_value[:100],
#                 'category': f.category,
#                 'confidence_score': f.confidence_score
#             }
#             for f in sample_features
#         ]
        
#         return Response(debug_info)

#     def list(self, request, *args, **kwargs):
#         """
#         Enhanced list view with processing statistics.
#         """
#         # Use summary serializer for list view
#         self.serializer_class = ParsedDocumentSummarySerializer
#         response = super().list(request, *args, **kwargs)
        
#         # Add processing statistics
#         total_docs = ParsedDocument.objects.count()
#         completed_docs = ParsedDocument.objects.filter(status='COMPLETED').count()
        
#         if isinstance(response.data, dict) and 'results' in response.data:
#             response.data['statistics'] = {
#                 'total_documents': total_docs,
#                 'completed_documents': completed_docs,
#                 'success_rate': (completed_docs / total_docs * 100) if total_docs > 0 else 0,
#                 'supported_formats': ['docx'],
#                 'processing_capabilities': [
#                     'Comprehensive field extraction',
#                     'Sea service history parsing',
#                     'Certificate and training record extraction',
#                     'Medical information extraction',
#                     'Database storage of individual features',
#                     'Table structure preservation',
#                     'Quality scoring and validation'
#                 ]
#             }
        
#         return response

"""
Enhanced views with YAML format endpoints for extracted fields.
"""

from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import ParsedDocument, ExtractedFeature, DocumentTable
from .serializers import ParsedDocumentSerializer, ParsedDocumentSummarySerializer
import logging
import os
import traceback
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DocumentUploadViewSet(viewsets.ModelViewSet):
    """
    Document upload viewset with YAML format endpoints for extracted fields.
    """
    queryset = ParsedDocument.objects.all()
    serializer_class = ParsedDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        """Handle document upload with comprehensive processing."""
        try:
            if 'source_file' not in request.data:
                return Response(
                    {'error': 'No file provided. Please upload a file with key "source_file"'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            uploaded_file = request.data['source_file']

            # Save ParsedDocument entry first
            document = ParsedDocument.objects.create(source_file=uploaded_file)

            # Run extraction
            from .ai_parser_service import EnhancedSeafarerFieldExtractor
            extractor = EnhancedSeafarerFieldExtractor()
            extracted_data, _ = extractor.extract_from_document(document.source_file.path)

            # Store extracted data
            document.extracted_features = extracted_data
            document.save()

            # Build seafarer profile
            profile = self._format_seafarer_profile(document)

            return Response({
                'document_id': document.id,
                'seafarer_profile': profile,
                'data_quality': {
                    'quality_score': document.get_extraction_quality_score(),
                    'completeness_check': self._check_profile_completeness(profile)
                },
                'yaml_export_url': f'/api/doc_parser/upload/{document.id}/yaml_profile/'
            })

        except Exception as e:
            logger.error(f"Document upload failed: {e}", exc_info=True)
            return Response(
                {'error': f"Upload failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # -------------------------------
    # Cleaning helper
    # -------------------------------
    def _clean_value(self, value: Any) -> Any:
        """Clean extracted value by removing duplicates and labels."""
        if not isinstance(value, str):
            return value

        # Split by newlines and normalize
        parts = [p.strip() for p in value.split("\n") if p.strip()]

        # Remove duplicates while preserving order
        seen = set()
        cleaned_parts = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                cleaned_parts.append(p)

        # Remove common labels
        labels_to_remove = [
            "full name", "name",
            "date of birth", "dob",
            "place of birth",
            "nationality",
            "marital status",
        ]
        cleaned_parts = [
            p for p in cleaned_parts
            if p.lower() not in labels_to_remove
        ]

        return " ".join(cleaned_parts).strip()

    def _format_seafarer_profile(self, document: ParsedDocument) -> Dict[str, Any]:
        """Format extracted data into a structured seafarer profile with cleaning."""
        extracted_data = document.extracted_features or {}
        if not extracted_data:
            return {}

        profile = {
            'personal': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('personal_information', {}).items()
            },
            'contact': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('contact_information', {}).items()
            },
            'documents': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('travel_documents', {}).items()
            },
            'medical': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('medical_information', {}).items()
            },
            'qualifications': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('qualifications', {}).items()
            },
            'training': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('stcw_training', {}).items()
            },
            'experience': extracted_data.get('sea_service', {}),
            'next_of_kin': {
                k: self._clean_value(v)
                for k, v in extracted_data.get('next_of_kin', {}).items()
            }
        }
        return profile

    def _check_profile_completeness(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Check completeness of seafarer profile."""
        required_fields = {
            'personal': ['full_name', 'nationality', 'date_of_birth'],
            'contact': ['email', 'phone_number'],
            'documents': ['passport_number', 'seaman_book_number'],
            'medical': ['medical_certificate_number'],
            'qualifications': ['certificate_of_competency']
        }

        completeness = {}
        for section, fields in required_fields.items():
            section_data = profile.get(section, {})
            completed_fields = sum(
                1 for field in fields
                if section_data.get(field) and str(section_data.get(field)) != "Not Available"
            )
            completeness[section] = {
                'completed': completed_fields,
                'total': len(fields),
                'percentage': (completed_fields / len(fields)) * 100 if fields else 0
            }
        return completeness

    @action(detail=False, methods=['post'])
    def test_extraction(self, request):
        """Test extraction on a file without saving to database."""
        if 'test_file' not in request.data:
            return Response({'error': 'No test_file provided'}, status=status.HTTP_400_BAD_REQUEST)

        test_file = request.data['test_file']

        if not test_file.name.lower().endswith('.docx'):
            return Response({'error': 'Only .docx files are supported'}, status=status.HTTP_400_BAD_REQUEST)

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            for chunk in test_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            from .ai_parser_service import EnhancedSeafarerFieldExtractor
            extractor = EnhancedSeafarerFieldExtractor()

            extracted_data, metadata = extractor.extract_from_document(tmp_file_path)

            result = {
                'file_info': {
                    'name': test_file.name,
                    'size': test_file.size
                },
                'extraction_successful': bool(extracted_data),
                'metadata': metadata
            }

            if extracted_data:
                field_count = 0
                for category, fields in extracted_data.items():
                    if isinstance(fields, dict):
                        field_count += len([v for v in fields.values() if v and str(v) != "Not Available"])
                    elif fields:
                        field_count += 1

                result['extraction_summary'] = {
                    'categories': list(extracted_data.keys()),
                    'total_fields_extracted': field_count,
                    'sample_data': {
                        k: (str(v)[:100] if isinstance(v, dict) else str(v)[:100])
                        for k, v in list(extracted_data.items())[:3]
                    }
                }
            else:
                result['error'] = metadata.get('error', 'Unknown extraction error')

            return Response(result)

        except Exception as e:
            return Response({
                'error': f'Test extraction failed: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            try:
                os.unlink(tmp_file_path)
            except:
                pass

    def list(self, request, *args, **kwargs):
        """Enhanced list view with processing statistics."""
        self.serializer_class = ParsedDocumentSummarySerializer
        response = super().list(request, *args, **kwargs)

        total_docs = ParsedDocument.objects.count()
        completed_docs = ParsedDocument.objects.filter(status='COMPLETED').count()
        failed_docs = ParsedDocument.objects.filter(status='FAILED').count()

        if isinstance(response.data, dict) and 'results' in response.data:
            response.data['statistics'] = {
                'total_documents': total_docs,
                'completed_documents': completed_docs,
                'failed_documents': failed_docs,
                'processing_documents': total_docs - completed_docs - failed_docs,
                'success_rate': (completed_docs / total_docs * 100) if total_docs > 0 else 0,
                'supported_formats': ['docx'],
                'export_formats': ['json', 'yaml'],
                'yaml_endpoints': [
                    'yaml_features - All extracted fields in YAML',
                    'yaml_profile - Complete seafarer profile in YAML',
                    'yaml_vessels - Vessel service records in YAML',
                    'yaml_certificates - Training certificates in YAML'
                ]
            }
        return response

    def retrieve(self, request, *args, **kwargs):
        """Enhanced retrieve view with processing details."""
        response = super().retrieve(request, *args, **kwargs)

        instance = self.get_object()
        if instance.status == 'COMPLETED':
            feature_count = ExtractedFeature.objects.filter(document=instance).count()
            table_count = DocumentTable.objects.filter(document=instance).count()

            response.data['processing_summary'] = {
                'extraction_method': instance.processing_metadata.get('extraction_method', 'unknown'),
                'features_extracted': feature_count,
                'tables_extracted': table_count,
                'quality_score': instance.get_extraction_quality_score(),
                'ai_extraction_used': instance.processing_metadata.get('ai_extraction', False),
                'pattern_extraction_used': instance.processing_metadata.get('pattern_extraction', True)
            }

            response.data['yaml_exports'] = {
                'all_features': f'/api/doc_parser/upload/{instance.id}/yaml_features/',
                'complete_profile': f'/api/doc_parser/upload/{instance.id}/yaml_profile/',
                'vessel_records': f'/api/doc_parser/upload/{instance.id}/yaml_vessels/',
                'certificates': f'/api/doc_parser/upload/{instance.id}/yaml_certificates/'
            }
        return response
