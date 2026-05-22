# """
# Data Mapper Service to convert extracted JSON data from ai_document app 
# to the Users model in the api app.

# This service maps the structured JSON data to individual fields in the Users model.
# """

# import logging
# from datetime import datetime
# from typing import Dict, Any, Optional, List
# from django.db import transaction
# from django.core.exceptions import ValidationError
# from django.utils.dateparse import parse_date

# # Import models from both apps
# from api.models import Users, Certificate, Rank, UserRank, Reference, SeaService
# from ai_document.models import Applicant

# logger = logging.getLogger(__name__)


# class DataMapperService:
#     """
#     Service to map extracted JSON data to Users model fields.
#     """
    
#     @staticmethod
#     def parse_date_string(date_str: str) -> Optional[datetime.date]:
#         """
#         Parse various date formats from extracted text.
        
#         Args:
#             date_str: Date string in various formats
            
#         Returns:
#             Parsed date object or None
#         """
#         if not date_str or not isinstance(date_str, str):
#             return None
        
#         # Clean the date string
#         date_str = date_str.strip().replace('/', '-').replace(' ', '')
        
#         # Try different date formats
#         date_formats = [
#             '%d-%m-%Y',  # 29-01-1968
#             '%d-%m-%y',   # 29-01-68
#             '%Y-%m-%d',   # 1968-01-29
#             '%m-%d-%Y',   # 01-29-1968
#             '%d%m%Y',     # 29011968
#         ]
        
#         for fmt in date_formats:
#             try:
#                 return datetime.strptime(date_str, fmt).date()
#             except ValueError:
#                 continue
        
#         # Try Django's built-in parser
#         try:
#             return parse_date(date_str)
#         except (ValueError, TypeError):
#             logger.warning(f"Could not parse date: {date_str}")
#             return None
    
#     @staticmethod
#     def extract_certificates_from_data(structured_data: Dict[str, Any]) -> List[str]:
#         """
#         Extract certificate names from various sections of the data.
        
#         Args:
#             structured_data: The extracted JSON data
            
#         Returns:
#             List of certificate names
#         """
#         certificates = []
        
#         # Check Professional Qualifications
#         prof_quals = structured_data.get("Professional_Qualifications", {})
#         if isinstance(prof_quals, dict):
#             certs = prof_quals.get("certificates", [])
#             if isinstance(certs, list):
#                 for cert in certs:
#                     if isinstance(cert, dict):
#                         name = cert.get("name", "")
#                         if name:
#                             certificates.append(name)
        
#         # Check Marine Courses
#         marine_courses = structured_data.get("Marine_Courses", {})
#         if isinstance(marine_courses, dict):
#             training = marine_courses.get("training", [])
#             if isinstance(training, list):
#                 for course in training:
#                     if isinstance(course, dict):
#                         name = course.get("name", "") or course.get("course_name", "")
#                         if name:
#                             certificates.append(name)
        
#         # Check Sea Service Details (sometimes contains certificates)
#         sea_service = structured_data.get("Sea_Service_Details", {})
#         if isinstance(sea_service, dict):
#             ship_exp = sea_service.get("ship_experience", [])
#             if isinstance(ship_exp, list):
#                 for exp in ship_exp:
#                     if isinstance(exp, dict):
#                         name = exp.get("name", "") or exp.get("course_name", "")
#                         if name:
#                             certificates.append(name)
        
#         return list(set(certificates))  # Remove duplicates
    
#     @staticmethod
#     def find_or_create_certificates(certificate_names: List[str]) -> List[Certificate]:
#         """
#         Find existing certificates or create new ones.
        
#         Args:
#             certificate_names: List of certificate names
            
#         Returns:
#             List of Certificate objects
#         """
#         certificates = []
        
#         for cert_name in certificate_names:
#             if not cert_name:
#                 continue
            
#             # Try to find existing certificate by name (case-insensitive)
#             cert = Certificate.objects.filter(name__icontains=cert_name).first()
            
#             if not cert:
#                 # Create new certificate with a generated code
#                 code = cert_name.upper().replace(' ', '_')[:100]
#                 cert, created = Certificate.objects.get_or_create(
#                     code=code,
#                     defaults={'name': cert_name}
#                 )
#                 if created:
#                     logger.info(f"Created new certificate: {cert_name}")
            
#             certificates.append(cert)
        
#         return certificates
    
#     @staticmethod
#     def extract_references_from_data(structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
#         """
#         Extract reference data from the structured data.
        
#         Args:
#             structured_data: The extracted JSON data
            
#         Returns:
#             List of reference dictionaries
#         """
#         references = []
        
#         refs_data = structured_data.get("References", {})
#         if isinstance(refs_data, list):
#             # References is a list
#             for ref in refs_data:
#                 if isinstance(ref, dict):
#                     references.append({
#                         'company_name': ref.get('Company_Management_Country', '') or ref.get('company_name', ''),
#                         'position': ref.get('Position', '') or ref.get('position', ''),
#                         'name': ref.get('Name', '') or ref.get('name', ''),
#                         'tel': ref.get('TEL', '') or ref.get('tel', '') or ref.get('phone', ''),
#                         'email': ref.get('EMAIL', '') or ref.get('email', ''),
#                     })
#         elif isinstance(refs_data, dict):
#             # References is a dict with a list inside
#             ref_list = refs_data.get('references', [])
#             if isinstance(ref_list, list):
#                 for ref in ref_list:
#                     if isinstance(ref, dict):
#                         references.append({
#                             'company_name': ref.get('Company_Management_Country', '') or ref.get('company_name', ''),
#                             'position': ref.get('Position', '') or ref.get('position', ''),
#                             'name': ref.get('Name', '') or ref.get('name', ''),
#                             'tel': ref.get('TEL', '') or ref.get('tel', '') or ref.get('phone', ''),
#                             'email': ref.get('EMAIL', '') or ref.get('email', ''),
#                         })
        
#         return references
    
#     @staticmethod
#     def extract_sea_services_from_data(structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
#         """
#         Extract sea service data from the structured data.
        
#         Args:
#             structured_data: The extracted JSON data
            
#         Returns:
#             List of sea service dictionaries
#         """
#         sea_services = []
        
#         sea_service_data = structured_data.get("Sea_Service_Details", {})
#         if isinstance(sea_service_data, dict):
#             ship_exp = sea_service_data.get("ship_experience", [])
#             if isinstance(ship_exp, list):
#                 for service in ship_exp:
#                     if isinstance(service, dict):
#                         sea_services.append({
#                             'company_name': service.get('Company_Name', '') or service.get('company_name', ''),
#                             'rank': service.get('Rank', '') or service.get('rank', ''),
#                             'vessel_name_imo': service.get('Vessel_Name_IMO_Number', '') or service.get('vessel_name', ''),
#                             'flag': service.get('Flag', '') or service.get('flag', ''),
#                             'signed_on': DataMapperService.parse_date_string(service.get('Signed_On', '') or service.get('signed_on', '')),
#                             'signed_off': DataMapperService.parse_date_string(service.get('Signed_Off', '') or service.get('signed_off', '')),
#                             'period': service.get('Period', '') or service.get('period', ''),
#                             'vessel_type': service.get('Vessel_Type', '') or service.get('vessel_type', ''),
#                             'dwt_grt': service.get('DWT_GRT', '') or service.get('dwt_grt', ''),
#                             'engine_type_bh_kw': service.get('Engine_Type', '') or service.get('BH_KW', '') or service.get('engine_type_bh_kw', ''),
#                             'reason_for_sign_off': service.get('Reason_for_Sign_off', '') or service.get('reason_for_sign_off', ''),
#                         })
        
#         return sea_services
    
#     @staticmethod
#     def map_applicant_to_users(applicant: Applicant) -> Users:
#         """
#         Map an Applicant instance to a Users instance.
        
#         Args:
#             applicant: Applicant instance from ai_document app
            
#         Returns:
#             Users instance for api app
#         """
#         # Get the structured data
#         personal_details = applicant.personal_details or {}
#         education = applicant.education or {}
#         contact_details = applicant.contact_details or {}
#         travel_documents = applicant.travel_documents or {}
#         professional_qualifications = applicant.professional_qualifications or {}
#         next_of_kin = applicant.next_of_kin_emergency_contact or {}
#         health_certs = applicant.health_certificates_vaccinations or {}
#         covid_vaccination = applicant.covid_19_vaccination or {}
#         declaration = applicant.declaration or {}
#         office_use = applicant.office_use_only or {}
        
#         # Create Users instance
#         user_data = {
#             # Basic info
#             'email': personal_details.get('email', '') or contact_details.get('email', ''),
#             'first_name': personal_details.get('name', '').split()[0] if personal_details.get('name') else '',
#             'middle_name': ' '.join(personal_details.get('name', '').split()[1:-1]) if len(personal_details.get('name', '').split()) > 2 else '',
            
#             # Personal details
#             'nationality': personal_details.get('nationality', ''),
#             'date_of_birth': DataMapperService.parse_date_string(personal_details.get('birth_date', '')),
#             'address': personal_details.get('address', '') or contact_details.get('address', ''),
#             'phone_number': personal_details.get('phone', '') or contact_details.get('phone', ''),
            
#             # Education
#             'college_or_school': ', '.join(education.get('schools', [])) if isinstance(education.get('schools'), list) else str(education.get('schools', '')),
#             'english_language_level': ', '.join(education.get('languages', [])) if isinstance(education.get('languages'), list) else str(education.get('languages', '')),
            
#             # Travel Documents - Passport
#             'passport_no': '',
#             'passport_issue_date': None,
#             'passport_expiry_date': None,
#             'passport_issued_by': '',
#             'passport_place_of_issue': '',
            
#             # Travel Documents - Seaman Book
#             'seaman_book_no': '',
#             'seaman_book_issue_date': None,
#             'seaman_book_expiry_date': None,
#             'seaman_book_issued_by': '',
#             'seaman_book_place_of_issue': '',
            
#             # Other Seaman Book
#             'other_seaman_book_no': '',
#             'other_seaman_book_issue_date': None,
#             'other_seaman_book_expiry_date': None,
#             'other_seaman_book_issued_by': '',
#             'other_seaman_book_place_of_issue': '',
            
#             # Professional Qualifications
#             'coc_certificate_name': '',
#             'coc_certificate_number': '',
#             'coc_issue_date': None,
#             'coc_expiry_date': None,
#             'coc_issued_by': '',
#             'coc_issued_at': '',
            
#             # Next of Kin
#             'next_of_kin_full_name': next_of_kin.get('Full_Name', '') or next_of_kin.get('full_name', ''),
#             'next_of_kin_relationship': next_of_kin.get('Relationship', '') or next_of_kin.get('relationship', ''),
#             'next_of_kin_address_country': next_of_kin.get('Address_Country', '') or next_of_kin.get('address', ''),
#             'next_of_kin_phone': next_of_kin.get('Tel_No', '') or next_of_kin.get('Mobile', '') or next_of_kin.get('phone', ''),
#             'next_of_kin_email': next_of_kin.get('Email', '') or next_of_kin.get('email', ''),
            
#             # Health Certificates
#             'health_flag_state': health_certs.get('Flag_State', '') if isinstance(health_certs, dict) else '',
#             'health_number': health_certs.get('Number', '') if isinstance(health_certs, dict) else '',
#             'health_issue_date': DataMapperService.parse_date_string(health_certs.get('Issue_Date', '')) if isinstance(health_certs, dict) else None,
#             'health_expiry_date': DataMapperService.parse_date_string(health_certs.get('Expiry_Date', '')) if isinstance(health_certs, dict) else None,
#             'health_issued_by': health_certs.get('Issued_By', '') if isinstance(health_certs, dict) else '',
#             'health_issued_at': health_certs.get('Issued_At', '') if isinstance(health_certs, dict) else '',
            
#             # COVID Vaccination
#             'covid_vaccine_name': covid_vaccination.get('Vaccination_Name', '') or covid_vaccination.get('vaccine_name', ''),
#             'covid_first_dose': DataMapperService.parse_date_string(covid_vaccination.get('First_Dose', '') or covid_vaccination.get('first_dose', '')),
#             'covid_second_dose': DataMapperService.parse_date_string(covid_vaccination.get('Second_Dose', '') or covid_vaccination.get('second_dose', '')),
#             'covid_other_doses_or_remarks': covid_vaccination.get('Other_Doses_or_Remarks', '') or covid_vaccination.get('other_doses', ''),
            
#             # Declaration
#             'declaration_consent': bool(declaration.get('Consent_Statement', False)),
#             'declaration_date': DataMapperService.parse_date_string(declaration.get('Date', '')),
#             'declaration_place': declaration.get('place', ''),
            
#             # Office Use Only
#             'initial_assessment_comments': office_use.get('Initial_assessment_of_applicant', '') or office_use.get('Comments', ''),
#             'responsible_person_name': office_use.get('Responsible_person', '') or office_use.get('Name_Signature', ''),
#             'assessment_date': DataMapperService.parse_date_string(office_use.get('Date', '')),
#         }
        
#         # Handle travel documents
#         if isinstance(travel_documents, dict):
#             # Passport details
#             passport_details = travel_documents.get('passport_details', {})
#             if isinstance(passport_details, dict):
#                 user_data.update({
#                     'passport_no': passport_details.get('number', '') or passport_details.get('document_no', ''),
#                     'passport_issue_date': DataMapperService.parse_date_string(passport_details.get('iss_date', '') or passport_details.get('issue_date', '')),
#                     'passport_expiry_date': DataMapperService.parse_date_string(passport_details.get('exp_date', '') or passport_details.get('expiry_date', '')),
#                     'passport_issued_by': passport_details.get('authority', '') or passport_details.get('iss_by', ''),
#                     'passport_place_of_issue': passport_details.get('place_of_issue', ''),
#                 })
            
#             # Seaman book details
#             seaman_book = travel_documents.get('seaman_book_details', {}) or travel_documents.get('seaman_book', {})
#             if isinstance(seaman_book, dict):
#                 user_data.update({
#                     'seaman_book_no': seaman_book.get('passport_number', '') or seaman_book.get('book_no', ''),
#                     'seaman_book_issue_date': DataMapperService.parse_date_string(seaman_book.get('iss_date', '') or seaman_book.get('issue_date', '')),
#                     'seaman_book_expiry_date': DataMapperService.parse_date_string(seaman_book.get('exp_date', '') or seaman_book.get('expiry_date', '')),
#                     'seaman_book_issued_by': seaman_book.get('authority', '') or seaman_book.get('iss_by', ''),
#                     'seaman_book_place_of_issue': seaman_book.get('place_of_issue', ''),
#                 })
            
#             # Other seaman book
#             other_seaman_book = travel_documents.get('other_seaman_book_details', {}) or travel_documents.get('other_seaman_book', {})
#             if isinstance(other_seaman_book, dict):
#                 user_data.update({
#                     'other_seaman_book_no': other_seaman_book.get('passport_number', '') or other_seaman_book.get('book_no', ''),
#                     'other_seaman_book_issue_date': DataMapperService.parse_date_string(other_seaman_book.get('iss_date', '') or other_seaman_book.get('issue_date', '')),
#                     'other_seaman_book_expiry_date': DataMapperService.parse_date_string(other_seaman_book.get('exp_date', '') or other_seaman_book.get('expiry_date', '')),
#                     'other_seaman_book_issued_by': other_seaman_book.get('authority', '') or other_seaman_book.get('iss_by', ''),
#                     'other_seaman_book_place_of_issue': other_seaman_book.get('place_of_issue', ''),
#                 })
        
#         # Handle professional qualifications
#         if isinstance(professional_qualifications, dict):
#             certificates = professional_qualifications.get('certificates', [])
#             if isinstance(certificates, list) and certificates:
#                 # Take the first certificate as COC
#                 first_cert = certificates[0]
#                 if isinstance(first_cert, dict):
#                     user_data.update({
#                         'coc_certificate_name': first_cert.get('name', ''),
#                         'coc_certificate_number': first_cert.get('number', ''),
#                         'coc_issue_date': DataMapperService.parse_date_string(first_cert.get('issue_date', '')),
#                         'coc_expiry_date': DataMapperService.parse_date_string(first_cert.get('expiry_date', '')),
#                         'coc_issued_by': first_cert.get('issued_by', '') or first_cert.get('authority', ''),
#                         'coc_issued_at': first_cert.get('issued_at', ''),
#                     })
        
#         # Remove None values and empty strings for optional fields
#         cleaned_data = {}
#         for key, value in user_data.items():
#             if value is not None and value != '':
#                 cleaned_data[key] = value
        
#         return Users(**cleaned_data)
    
#     @staticmethod
#     @transaction.atomic
#     def save_applicant_as_user(applicant: Applicant) -> Users:
#         """
#         Convert an Applicant to a Users instance and save it with all relationships.
        
#         Args:
#             applicant: Applicant instance from ai_document app
            
#         Returns:
#             Created Users instance
#         """
#         try:
#             # Create the base Users instance
#             user = DataMapperService.map_applicant_to_users(applicant)
            
#             # Validate email
#             if not user.email:
#                 raise ValidationError("Email is required")
            
#             # Check if user already exists
#             existing_user = Users.objects.filter(email=user.email).first()
#             if existing_user:
#                 logger.info(f"User with email {user.email} already exists. Updating existing user.")
#                 # Update existing user
#                 for field, value in user.__dict__.items():
#                     if not field.startswith('_') and value is not None:
#                         setattr(existing_user, field, value)
#                 existing_user.save()
#                 user = existing_user
#             else:
#                 # Set a default password for new users
#                 user.set_password('defaultpassword123')  # You should change this
#                 user.save()
#                 logger.info(f"Created new user: {user.email}")
            
#             # Get all structured data for relationships
#             structured_data = {
#                 'Personal_Details': applicant.personal_details or {},
#                 'Education': applicant.education or {},
#                 'Contact_Details': applicant.contact_details or {},
#                 'Travel_Documents': applicant.travel_documents or {},
#                 'Professional_Qualifications': applicant.professional_qualifications or {},
#                 'Next_of_Kin_Emergency_Contact': applicant.next_of_kin_emergency_contact or {},
#                 'Health_Certificates_Vaccinations': applicant.health_certificates_vaccinations or {},
#                 'Covid_19_Vaccination': applicant.covid_19_vaccination or {},
#                 'Marine_Courses': applicant.marine_courses or {},
#                 'Sea_Service_Details': applicant.sea_service_details or {},
#                 'Specialised_Experience': applicant.specialised_experience or {},
#                 'References': applicant.references or {},
#                 'Declaration': applicant.declaration or {},
#                 'Office_Use_Only': applicant.office_use_only or {},
#             }
            
#             # Handle certificates
#             certificate_names = DataMapperService.extract_certificates_from_data(structured_data)
#             if certificate_names:
#                 certificates = DataMapperService.find_or_create_certificates(certificate_names)
#                 user.certificates.set(certificates)
#                 logger.info(f"Added {len(certificates)} certificates to user")
            
#             # Handle references
#             references_data = DataMapperService.extract_references_from_data(structured_data)
#             for ref_data in references_data:
#                 if ref_data.get('name') or ref_data.get('company_name'):
#                     Reference.objects.create(user=user, **ref_data)
#             logger.info(f"Added {len(references_data)} references to user")
            
#             # Handle sea services
#             sea_services_data = DataMapperService.extract_sea_services_from_data(structured_data)
#             for service_data in sea_services_data:
#                 if service_data.get('vessel_name_imo') or service_data.get('company_name'):
#                     # Convert None dates to empty strings for fields that don't accept None
#                     if service_data.get('signed_on') is None:
#                         service_data.pop('signed_on', None)
#                     if service_data.get('signed_off') is None:
#                         service_data.pop('signed_off', None)
                    
#                     SeaService.objects.create(user=user, **service_data)
#             logger.info(f"Added {len(sea_services_data)} sea services to user")
            
#             return user
            
#         except Exception as e:
#             logger.error(f"Error saving applicant as user: {e}")
#             raise


# # Utility function to be used in views
# def convert_applicant_to_user(applicant_id: int) -> Users:
#     """
#     Convert an Applicant to a Users instance.
    
#     Args:
#         applicant_id: ID of the Applicant to convert
        
#     Returns:
#         Created Users instance
        
#     Raises:
#         Applicant.DoesNotExist: If applicant doesn't exist
#         ValidationError: If data validation fails
#     """
#     try:
#         applicant = Applicant.objects.get(id=applicant_id)
#         return DataMapperService.save_applicant_as_user(applicant)
#     except Applicant.DoesNotExist:
#         logger.error(f"Applicant with ID {applicant_id} not found")
#         raise
#     except Exception as e:
#         logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#         raise











# ai_document/data_mapper_service.py

# import logging
# from typing import Dict, Any, Optional
# from django.db import transaction
# from api.models import Users

# logger = logging.getLogger(__name__)

# class DataMapperService:
#     """
#     Service to map data from Applicant model to Users model in the api app.
#     """
    
#     @staticmethod
#     def map_applicant_to_user(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Map structured JSON data from Applicant to Users model format.
        
#         Args:
#             applicant_data: Dictionary containing the structured JSON data
            
#         Returns:
#             Dictionary formatted for Users model
#         """
#         try:
#             # Extract nested data safely
#             personal_details = applicant_data.get("Personal_Details", {})
#             contact_details = applicant_data.get("Contact_Details", {})
#             travel_documents = applicant_data.get("Travel_Documents", {})
#             education = applicant_data.get("Education", {})
#             professional_qualifications = applicant_data.get("Professional_Qualifications", {})
#             next_of_kin = applicant_data.get("Next_of_Kin_Emergency_Contact", {})
#             health_certs = applicant_data.get("Health_Certificates_Vaccinations", {})
#             covid_vaccination = applicant_data.get("Covid_19_Vaccination", {})
#             marine_courses = applicant_data.get("Marine_Courses", {})
#             sea_service = applicant_data.get("Sea_Service_Details", {})
#             references = applicant_data.get("References", {})
            
#             # Map to Users model fields
#             user_data = {
#                 # Personal Information
#                 "first_name": personal_details.get("first_name", ""),
#                 "last_name": personal_details.get("last_name", ""),
#                 "middle_name": personal_details.get("middle_name", ""),
#                 "date_of_birth": DataMapperService._parse_date(personal_details.get("date_of_birth")),
#                 "place_of_birth": personal_details.get("place_of_birth", ""),
#                 "nationality": personal_details.get("nationality", ""),
#                 "gender": DataMapperService._normalize_gender(personal_details.get("gender", "")),
#                 "marital_status": personal_details.get("marital_status", ""),
                
#                 # Contact Information
#                 "email": contact_details.get("email", ""),
#                 "phone_number": contact_details.get("phone_number", ""),
#                 "address": contact_details.get("address", ""),
#                 "city": contact_details.get("city", ""),
#                 "state": contact_details.get("state", ""),
#                 "country": contact_details.get("country", ""),
#                 "postal_code": contact_details.get("postal_code", ""),
                
#                 # Travel Documents
#                 "passport_number": travel_documents.get("passport_number", ""),
#                 "passport_issue_date": DataMapperService._parse_date(travel_documents.get("passport_issue_date")),
#                 "passport_expiry_date": DataMapperService._parse_date(travel_documents.get("passport_expiry_date")),
#                 "passport_issuing_country": travel_documents.get("passport_issuing_country", ""),
#                 "seaman_book_number": travel_documents.get("seaman_book_number", ""),
#                 "seaman_book_issue_date": DataMapperService._parse_date(travel_documents.get("seaman_book_issue_date")),
#                 "seaman_book_expiry_date": DataMapperService._parse_date(travel_documents.get("seaman_book_expiry_date")),
                
#                 # Education
#                 "education_level": education.get("highest_level", ""),
#                 "institution": education.get("institution", ""),
#                 "graduation_year": DataMapperService._parse_year(education.get("graduation_year")),
                
#                 # Professional Information
#                 "license_number": professional_qualifications.get("license_number", ""),
#                 "license_type": professional_qualifications.get("license_type", ""),
#                 "license_issue_date": DataMapperService._parse_date(professional_qualifications.get("license_issue_date")),
#                 "license_expiry_date": DataMapperService._parse_date(professional_qualifications.get("license_expiry_date")),
                
#                 # Emergency Contact
#                 "emergency_contact_name": next_of_kin.get("name", ""),
#                 "emergency_contact_relationship": next_of_kin.get("relationship", ""),
#                 "emergency_contact_phone": next_of_kin.get("phone", ""),
#                 "emergency_contact_address": next_of_kin.get("address", ""),
                
#                 # Health Information
#                 "medical_certificate_number": health_certs.get("medical_certificate_number", ""),
#                 "medical_certificate_issue_date": DataMapperService._parse_date(health_certs.get("medical_certificate_issue_date")),
#                 "medical_certificate_expiry_date": DataMapperService._parse_date(health_certs.get("medical_certificate_expiry_date")),
#                 "covid_vaccination_status": DataMapperService._normalize_boolean(covid_vaccination.get("vaccinated", False)),
#                 "covid_vaccination_date": DataMapperService._parse_date(covid_vaccination.get("vaccination_date")),
                
#                 # Experience
#                 "total_sea_service_months": DataMapperService._parse_integer(sea_service.get("total_months", 0)),
#                 "last_vessel_name": sea_service.get("last_vessel_name", ""),
#                 "last_vessel_type": sea_service.get("last_vessel_type", ""),
#                 "last_rank_held": sea_service.get("last_rank_held", ""),
                
#                 # Additional fields can be stored as JSON
#                 "additional_data": {
#                     "marine_courses": marine_courses,
#                     "references": references,
#                     "specialised_experience": applicant_data.get("Specialised_Experience", {}),
#                     "declaration": applicant_data.get("Declaration", {}),
#                 }
#             }
            
#             # Remove empty strings and None values
#             user_data = {k: v for k, v in user_data.items() if v not in ["", None]}
            
#             return user_data
            
#         except Exception as e:
#             logger.error(f"Error mapping applicant data to user format: {str(e)}")
#             raise ValueError(f"Data mapping failed: {str(e)}")
    
#     @staticmethod
#     def save_to_users_model(user_data: Dict[str, Any]) -> Optional[Users]:
#         """
#         Save mapped data to Users model.
        
#         Args:
#             user_data: Dictionary formatted for Users model
            
#         Returns:
#             Users instance if successful, None otherwise
#         """
#         try:
#             with transaction.atomic():
#                 # Check if user already exists (by email or passport)
#                 existing_user = None
#                 if user_data.get("email"):
#                     existing_user = Users.objects.filter(email=user_data["email"]).first()
#                 elif user_data.get("passport_number"):
#                     existing_user = Users.objects.filter(passport_number=user_data["passport_number"]).first()
                
#                 if existing_user:
#                     logger.info(f"User already exists with ID: {existing_user.id}")
#                     # Update existing user
#                     for key, value in user_data.items():
#                         setattr(existing_user, key, value)
#                     existing_user.save()
#                     return existing_user
#                 else:
#                     # Create new user
#                     user = Users.objects.create(**user_data)
#                     logger.info(f"New user created with ID: {user.id}")
#                     return user
                    
#         except Exception as e:
#             logger.error(f"Error saving to Users model: {str(e)}")
#             return None
    
#     @staticmethod
#     def _parse_date(date_string: Any) -> Optional[str]:
#         """Parse date string to proper format."""
#         if not date_string or date_string == "":
#             return None
#         # Add date parsing logic here if needed
#         return str(date_string)
    
#     @staticmethod
#     def _parse_year(year_string: Any) -> Optional[int]:
#         """Parse year string to integer."""
#         if not year_string:
#             return None
#         try:
#             return int(str(year_string))
#         except (ValueError, TypeError):
#             return None
    
#     @staticmethod
#     def _parse_integer(value: Any) -> int:
#         """Parse value to integer."""
#         try:
#             return int(value) if value else 0
#         except (ValueError, TypeError):
#             return 0
    
#     @staticmethod
#     def _normalize_gender(gender: str) -> str:
#         """Normalize gender values."""
#         if not gender:
#             return ""
#         gender_lower = gender.lower()
#         if gender_lower in ["male", "m"]:
#             return "Male"
#         elif gender_lower in ["female", "f"]:
#             return "Female"
#         return gender
    
#     @staticmethod
#     def _normalize_boolean(value: Any) -> bool:
#         """Normalize boolean values."""
#         if isinstance(value, bool):
#             return value
#         if isinstance(value, str):
#             return value.lower() in ["true", "yes", "1", "y"]
#         return bool(value)

















# # ai_document/data_mapper_service.py

# import logging
# from datetime import datetime
# from typing import Dict, Any, Optional, List
# from django.db import transaction
# from django.core.exceptions import ValidationError
# from django.utils.dateparse import parse_date
# import re

# # Import models from both apps
# from api.models import Users, Certificate, Rank, UserRank, Reference, SeaService
# from ai_document.models import Applicant

# logger = logging.getLogger(__name__)


# class DataMapperService:
#     """
#     Service to map extracted JSON data to Users model fields.
#     """
    
#     @staticmethod
#     def parse_date_string(date_str: str) -> Optional[datetime.date]:
#         """
#         Parse various date formats from extracted text.
        
#         Args:
#             date_str: Date string in various formats
        
#         Returns:
#             Parsed date object or None
#         """
#         if not date_str or not isinstance(date_str, str):
#             return None
        
#         # Clean the date string
#         date_str = date_str.strip().replace('/', '-').replace(' ', '')
        
#         # Try different date formats
#         date_formats = [
#             '%d-%m-%Y',  # 28-07-1975
#             '%d-%m-%y',   # 28-07-75
#             '%Y-%m-%d',   # 1975-07-28
#             '%m-%d-%Y',   # 07-28-1975
#             '%d%m%Y',    # 28071975
#         ]
        
#         for fmt in date_formats:
#             try:
#                 return datetime.strptime(date_str, fmt).date()
#             except ValueError:
#                 continue
        
#         # Try Django's built-in parser
#         try:
#             return parse_date(date_str)
#         except (ValueError, TypeError):
#             logger.warning(f"Could not parse date: {date_str}")
#             return None
    
#     @staticmethod
#     def extract_name_parts(full_name: str) -> Dict[str, str]:
#         """
#         Extract first, middle, and last name from full name.
        
#         Args:
#             full_name: Full name string
            
#         Returns:
#             Dictionary with first_name, middle_name, last_name
#         """
#         if not full_name:
#             return {"first_name": "", "middle_name": "", "last_name": ""}
        
#         name_parts = full_name.strip().split()
        
#         if len(name_parts) == 1:
#             return {"first_name": name_parts[0], "middle_name": "", "last_name": ""}
#         elif len(name_parts) == 2:
#             return {"first_name": name_parts[0], "middle_name": "", "last_name": name_parts[1]}
#         elif len(name_parts) >= 3:
#             return {
#                 "first_name": name_parts[0],
#                 "middle_name": " ".join(name_parts[1:-1]),
#                 "last_name": name_parts[-1]
#             }
        
#         return {"first_name": "", "middle_name": "", "last_name": ""}
    
#     @staticmethod
#     def calculate_age_from_birth_date(birth_date_str: str) -> Optional[int]:
#         """
#         Calculate age from birth date string.
        
#         Args:
#             birth_date_str: Birth date string
            
#         Returns:
#             Age in years or None
#         """
#         birth_date = DataMapperService.parse_date_string(birth_date_str)
#         if birth_date:
#             today = datetime.now().date()
#             age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
#             return age
#         return None
    
#     @staticmethod
#     def extract_phone_numbers(data: Dict[str, Any]) -> Dict[str, str]:
#         """
#         Extract phone and tel numbers from data.
        
#         Args:
#             data: Dictionary containing contact information
            
#         Returns:
#             Dictionary with phone_number and tel_number
#         """
#         phone_number = ""
#         tel_number = ""
        
#         # Check Personal_Details
#         personal = data.get("Personal_Details", {})
#         contact = data.get("Contact_Details", {})
        
#         # Get phone number
#         phone_number = personal.get("phone", "") or contact.get("phone", "")
        
#         # If there are multiple phone numbers, try to separate them
#         if phone_number and "," in phone_number:
#             phones = [p.strip() for p in phone_number.split(",")]
#             phone_number = phones[0]
#             if len(phones) > 1:
#                 tel_number = phones[1]
        
#         return {"phone_number": phone_number, "tel_number": tel_number}
    
#     @staticmethod
#     def map_applicant_to_users(applicant: Applicant) -> Users:
#         """
#         Map an Applicant instance to a Users instance.
        
#         Args:
#             applicant: Applicant instance from ai_document app
        
#         Returns:
#             Users instance for api app
#         """
#         # Get the structured data
#         personal_details = applicant.personal_details or {}
#         education = applicant.education or {}
#         contact_details = applicant.contact_details or {}
#         travel_documents = applicant.travel_documents or {}
#         professional_qualifications = applicant.professional_qualifications or {}
#         next_of_kin = applicant.next_of_kin_emergency_contact or {}
#         health_certs = applicant.health_certificates_vaccinations or {}
#         covid_vaccination = applicant.covid_19_vaccination or {}
#         declaration = applicant.declaration or {}
#         office_use = applicant.office_use_only or {}
        
#         # Extract name parts
#         full_name = personal_details.get('name', '')
#         name_parts = DataMapperService.extract_name_parts(full_name)
        
#         # Extract phone numbers
#         phone_data = DataMapperService.extract_phone_numbers({
#             "Personal_Details": personal_details,
#             "Contact_Details": contact_details
#         })
        
#         # Calculate age
#         birth_date_str = personal_details.get('birth_date', '')
#         age = DataMapperService.calculate_age_from_birth_date(birth_date_str)
        
#         # Create Users instance data
#         user_data = {
#             # Authentication & Basic Info
#             'email': personal_details.get('email', '') or contact_details.get('email', ''),
#             'first_name': name_parts['first_name'],
#             'middle_name': name_parts['middle_name'],
            
#             # Personal Info
#             'age': age,
#             'date_of_birth': DataMapperService.parse_date_string(birth_date_str),
#             'nationality': personal_details.get('nationality', ''),
#             'Place_Of_Birth': personal_details.get('place_of_birth', ''),
#             'marital_status': personal_details.get('marital_status', 'Single'),
            
#             # Contact Information
#             'address': personal_details.get('address', '') or contact_details.get('address', ''),
#             'phone_number': phone_data['phone_number'],
#             'tel_number': phone_data['tel_number'],
            
#             # Physical Details (default to 0 if not provided)
#             'Height_Cm': 0,
#             'Weight_Kg': 0,
#             'blood_type': '',
#             'smoker': False,
            
#             # Education
#             'college_or_school': '',
#             'english_language_level': '',
            
#             # Travel Documents - Passport
#             'passport_no': '',
#             'passport_issue_date': None,
#             'passport_expiry_date': None,
#             'passport_issued_by': '',
#             'passport_place_of_issue': '',
            
#             # Travel Documents - Seaman Book
#             'seaman_book_no': '',
#             'seaman_book_issue_date': None,
#             'seaman_book_expiry_date': None,
#             'seaman_book_issued_by': '',
#             'seaman_book_place_of_issue': '',
            
#             # Other Seaman Book
#             'other_seaman_book_no': '',
#             'other_seaman_book_issue_date': None,
#             'other_seaman_book_expiry_date': None,
#             'other_seaman_book_issued_by': '',
#             'other_seaman_book_place_of_issue': '',
            
#             # Professional Qualifications
#             'coc_certificate_name': '',
#             'coc_certificate_number': '',
#             'coc_issue_date': None,
#             'coc_expiry_date': None,
#             'coc_issued_by': 'EAMS',
#             'coc_issued_at': 'Alex.',
            
#             # GOC Certificate
#             'goc_certificate_number': '',
#             'goc_issue_date': None,
#             'goc_expiry_date': None,
#             'goc_issued_by': 'NTRA',
#             'goc_issued_at': 'Cairo',
            
#             # Next of Kin
#             'next_of_kin_full_name': next_of_kin.get('Full_Name', '') or next_of_kin.get('full_name', ''),
#             'next_of_kin_relationship': next_of_kin.get('Relationship', '') or next_of_kin.get('relationship', ''),
#             'next_of_kin_address_country': next_of_kin.get('Address_Country', '') or next_of_kin.get('address', ''),
#             'next_of_kin_phone': next_of_kin.get('Tel_No', '') or next_of_kin.get('Mobile', '') or next_of_kin.get('phone', ''),
#             'next_of_kin_email': next_of_kin.get('Email', '') or next_of_kin.get('email', ''),
            
#             # Health Certificates
#             'health_flag_state': health_certs.get('Flag_State', '') if isinstance(health_certs, dict) else '',
#             'health_number': health_certs.get('Number', '') if isinstance(health_certs, dict) else '',
#             'health_issue_date': DataMapperService.parse_date_string(health_certs.get('Issue_Date', '')) if isinstance(health_certs, dict) else None,
#             'health_expiry_date': DataMapperService.parse_date_string(health_certs.get('Expiry_Date', '')) if isinstance(health_certs, dict) else None,
#             'health_issued_by': health_certs.get('Issued_By', '') if isinstance(health_certs, dict) else '',
#             'health_issued_at': health_certs.get('Issued_At', '') if isinstance(health_certs, dict) else '',
            
#             # COVID Vaccination
#             'covid_vaccine_name': covid_vaccination.get('Vaccination_Name', '') or covid_vaccination.get('vaccine_name', ''),
#             'covid_first_dose': DataMapperService.parse_date_string(covid_vaccination.get('First_Dose', '') or covid_vaccination.get('first_dose', '')),
#             'covid_second_dose': DataMapperService.parse_date_string(covid_vaccination.get('Second_Dose', '') or covid_vaccination.get('second_dose', '')),
#             'covid_other_doses_or_remarks': covid_vaccination.get('Other_Doses_or_Remarks', '') or covid_vaccination.get('other_doses', ''),
            
#             # Physical Details (sizes)
#             'overall_size': '',
#             'shirt_size': '',
#             'trouser_size': '',
#             'shoes_size': '',
            
#             # Languages
#             'other_language': '',
#             'other_language_level': '',
            
#             # Medical History
#             'disease_history': '',
#             'accident_history': '',
#             'psychiatric_treatment_history': '',
#             'addiction_history': '',
            
#             # Declaration
#             'declaration_consent': bool(declaration.get('Consent_Statement', False)),
#             'declaration_date': DataMapperService.parse_date_string(declaration.get('Date', '')),
#             'declaration_place': declaration.get('place', ''),
            
#             # Office Use Only
#             'initial_assessment_comments': office_use.get('Initial_assessment_of_applicant', '') or office_use.get('Comments', ''),
#             'responsible_person_name': office_use.get('Responsible_person', '') or office_use.get('Name_Signature', ''),
#             'assessment_date': DataMapperService.parse_date_string(office_use.get('Date', '')),
            
#             # Marlins Test (initialize empty)
#             'marlins_test_result': '',
#             'marlins_test_issued_date': None,
#             'marlins_test_issued_at': '',
#             'marlins_test_issued_by': '',
#         }
        
#         # Handle education data
#         if isinstance(education, dict):
#             schools = education.get('schools', [])
#             if isinstance(schools, list) and schools:
#                 # Extract school names
#                 school_names = []
#                 languages = []
#                 for school in schools:
#                     if isinstance(school, dict):
#                         if school.get('name'):
#                             school_names.append(school['name'])
#                         if school.get('languages'):
#                             languages.extend(school['languages'])
#                     elif isinstance(school, str):
#                         school_names.append(school)
                
#                 user_data['college_or_school'] = ', '.join(school_names)
#                 if languages:
#                     user_data['english_language_level'] = ', '.join(languages)
            
#             # Handle languages at education level
#             edu_languages = education.get('languages', [])
#             if isinstance(edu_languages, list) and edu_languages:
#                 user_data['english_language_level'] = ', '.join(edu_languages)
        
#         # Handle travel documents
#         if isinstance(travel_documents, dict):
#             # Passport details
#             passport_details = travel_documents.get('passport_details', {})
#             if isinstance(passport_details, dict):
#                 user_data.update({
#                     'passport_no': passport_details.get('number', '') or passport_details.get('document_no', ''),
#                     'passport_issue_date': DataMapperService.parse_date_string(passport_details.get('iss_date', '') or passport_details.get('issue_date', '')),
#                     'passport_expiry_date': DataMapperService.parse_date_string(passport_details.get('exp_date', '') or passport_details.get('expiry_date', '')),
#                     'passport_issued_by': passport_details.get('iss_by_authority', '') or passport_details.get('authority', ''),
#                     'passport_place_of_issue': passport_details.get('place_of_issue', ''),
#                 })
            
#             # Seaman book details
#             seaman_book = travel_documents.get('seaman_book', {})
#             if isinstance(seaman_book, dict):
#                 user_data.update({
#                     'seaman_book_no': seaman_book.get('number', '') or seaman_book.get('book_no', ''),
#                     'seaman_book_issue_date': DataMapperService.parse_date_string(seaman_book.get('iss_date', '') or seaman_book.get('issue_date', '')),
#                     'seaman_book_expiry_date': DataMapperService.parse_date_string(seaman_book.get('exp_date', '') or seaman_book.get('expiry_date', '')),
#                     'seaman_book_issued_by': seaman_book.get('iss_by_authority', '') or seaman_book.get('authority', ''),
#                     'seaman_book_place_of_issue': seaman_book.get('place_of_issue', ''),
#                 })
            
#             # Other seaman book
#             other_seaman_book = travel_documents.get('other_seaman_book', {})
#             if isinstance(other_seaman_book, dict) and other_seaman_book:
#                 user_data.update({
#                     'other_seaman_book_no': other_seaman_book.get('number', '') or other_seaman_book.get('book_no', ''),
#                     'other_seaman_book_issue_date': DataMapperService.parse_date_string(other_seaman_book.get('iss_date', '') or other_seaman_book.get('issue_date', '')),
#                     'other_seaman_book_expiry_date': DataMapperService.parse_date_string(other_seaman_book.get('exp_date', '') or other_seaman_book.get('expiry_date', '')),
#                     'other_seaman_book_issued_by': other_seaman_book.get('iss_by_authority', '') or other_seaman_book.get('authority', ''),
#                     'other_seaman_book_place_of_issue': other_seaman_book.get('place_of_issue', ''),
#                 })
        
#         # Handle professional qualifications
#         if isinstance(professional_qualifications, dict):
#             user_data.update({
#                 'coc_certificate_name': professional_qualifications.get('certificate_name', ''),
#                 'coc_certificate_number': professional_qualifications.get('number', ''),
#                 'coc_issue_date': DataMapperService.parse_date_string(professional_qualifications.get('issue_date', '')),
#                 'coc_expiry_date': DataMapperService.parse_date_string(professional_qualifications.get('expiry_date', '')),
#                 'coc_issued_by': professional_qualifications.get('issued_by', 'EAMS'),
#                 'coc_issued_at': professional_qualifications.get('issued_at', 'Alex.'),
#             })
        
#         # Remove None values and empty strings for optional fields
#         cleaned_data = {}
#         for key, value in user_data.items():
#             if value is not None and value != '':
#                 cleaned_data[key] = value
        
#         return Users(**cleaned_data)
    
#     @staticmethod
#     def extract_certificates_from_data(structured_data: Dict[str, Any]) -> List[str]:
#         """
#         Extract certificate names from various sections of the data.
        
#         Args:
#             structured_data: The extracted JSON data
        
#         Returns:
#             List of certificate names
#         """
#         certificates = []
        
#         # Check Marine Courses
#         marine_courses = structured_data.get("Marine_Courses", {})
#         if isinstance(marine_courses, dict):
#             training = marine_courses.get("training", [])
#             if isinstance(training, list):
#                 for course in training:
#                     if isinstance(course, dict):
#                         name = course.get("course_name", "")
#                         if name:
#                             certificates.append(name)
                        
#                         # Also check proficiency_in field
#                         proficiency = course.get("proficiency_in", [])
#                         if isinstance(proficiency, list):
#                             certificates.extend(proficiency)
        
#         return list(set(certificates))  # Remove duplicates
    
#     @staticmethod
#     def find_or_create_certificates(certificate_names: List[str]) -> List[Certificate]:
#         """
#         Find existing certificates or create new ones.
        
#         Args:
#             certificate_names: List of certificate names
        
#         Returns:
#             List of Certificate objects
#         """
#         certificates = []
        
#         for cert_name in certificate_names:
#             if not cert_name:
#                 continue
            
#             # Try to find existing certificate by name (case-insensitive)
#             cert = Certificate.objects.filter(name__icontains=cert_name).first()
            
#             if not cert:
#                 # Create new certificate with a generated code
#                 code = cert_name.upper().replace(' ', '_')[:100]
#                 cert, created = Certificate.objects.get_or_create(
#                     code=code,
#                     defaults={'name': cert_name}
#                 )
#                 if created:
#                     logger.info(f"Created new certificate: {cert_name}")
            
#             certificates.append(cert)
        
#         return certificates
    
#     @staticmethod
#     def extract_references_from_data(structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
#         """
#         Extract reference data from the structured data.
        
#         Args:
#             structured_data: The extracted JSON data
        
#         Returns:
#             List of reference dictionaries
#         """
#         references = []
        
#         refs_data = structured_data.get("References", {})
#         if isinstance(refs_data, list):
#             # References is a list
#             for ref in refs_data:
#                 if isinstance(ref, dict):
#                     references.append({
#                         'company_name': ref.get('Company_Management_Country', '') or ref.get('company_name', ''),
#                         'position': ref.get('Position', '') or ref.get('position', ''),
#                         'name': ref.get('Name', '') or ref.get('name', ''),
#                         'tel': ref.get('TEL', '') or ref.get('tel', '') or ref.get('phone', ''),
#                         'email': ref.get('EMAIL', '') or ref.get('email', ''),
#                     })
#         elif isinstance(refs_data, dict):
#             # References is a dict with a list inside
#             ref_list = refs_data.get('references', [])
#             if isinstance(ref_list, list):
#                 for ref in ref_list:
#                     if isinstance(ref, dict):
#                         references.append({
#                             'company_name': ref.get('Company_Management_Country', '') or ref.get('company_name', ''),
#                             'position': ref.get('Position', '') or ref.get('position', ''),
#                             'name': ref.get('Name', '') or ref.get('name', ''),
#                             'tel': ref.get('TEL', '') or ref.get('tel', '') or ref.get('phone', ''),
#                             'email': ref.get('EMAIL', '') or ref.get('email', ''),
#                         })
        
#         return references
    
#     @staticmethod
#     def extract_sea_services_from_data(structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
#         """
#         Extract sea service data from the structured data.
        
#         Args:
#             structured_data: The extracted JSON data
        
#         Returns:
#             List of sea service dictionaries
#         """
#         sea_services = []
        
#         sea_service_data = structured_data.get("Sea_Service_Details", {})
#         if isinstance(sea_service_data, dict):
#             ship_exp = sea_service_data.get("ship_experience", [])
#             if isinstance(ship_exp, list):
#                 for service in ship_exp:
#                     if isinstance(service, dict):
#                         sea_services.append({
#                             'company_name': service.get('Company_Name', '') or service.get('company_name', ''),
#                             'rank': service.get('Rank', '') or service.get('rank', ''),
#                             'vessel_name_imo': service.get('Vessel_Name_IMO_Number', '') or service.get('vessel_name', ''),
#                             'flag': service.get('Flag', '') or service.get('flag', ''),
#                             'signed_on': DataMapperService.parse_date_string(service.get('Signed_On', '') or service.get('signed_on', '')),
#                             'signed_off': DataMapperService.parse_date_string(service.get('Signed_Off', '') or service.get('signed_off', '')),
#                             'period': service.get('Period', '') or service.get('period', ''),
#                             'vessel_type': service.get('Vessel_Type', '') or service.get('vessel_type', ''),
#                             'dwt_grt': service.get('DWT_GRT', '') or service.get('dwt_grt', ''),
#                             'engine_type_bh_kw': service.get('Engine_Type', '') or service.get('BH_KW', '') or service.get('engine_type_bh_kw', ''),
#                             'reason_for_sign_off': service.get('Reason_for_Sign_off', '') or service.get('reason_for_sign_off', ''),
#                         })
        
#         return sea_services
    
#     @staticmethod
#     @transaction.atomic
#     def save_applicant_as_user(applicant: Applicant) -> Users:
#         """
#         Convert an Applicant to a Users instance and save it with all relationships.
        
#         Args:
#             applicant: Applicant instance from ai_document app
        
#         Returns:
#             Created Users instance
#         """
#         try:
#             # Create the base Users instance
#             user = DataMapperService.map_applicant_to_users(applicant)
            
#             # Validate email
#             if not user.email:
#                 raise ValidationError("Email is required")
            
#             # Check if user already exists
#             existing_user = Users.objects.filter(email=user.email).first()
#             if existing_user:
#                 logger.info(f"User with email {user.email} already exists. Updating existing user.")
#                 # Update existing user
#                 for field, value in user.__dict__.items():
#                     if not field.startswith('_') and value is not None:
#                         setattr(existing_user, field, value)
#                 existing_user.save()
#                 user = existing_user
#             else:
#                 # Set a default password for new users
#                 user.set_password('defaultpassword123')  # You should change this
#                 user.save()
#                 logger.info(f"Created new user: {user.email}")
            
#             # Get all structured data for relationships
#             structured_data = {
#                 'Personal_Details': applicant.personal_details or {},
#                 'Education': applicant.education or {},
#                 'Contact_Details': applicant.contact_details or {},
#                 'Travel_Documents': applicant.travel_documents or {},
#                 'Professional_Qualifications': applicant.professional_qualifications or {},
#                 'Next_of_Kin_Emergency_Contact': applicant.next_of_kin_emergency_contact or {},
#                 'Health_Certificates_Vaccinations': applicant.health_certificates_vaccinations or {},
#                 'Covid_19_Vaccination': applicant.covid_19_vaccination or {},
#                 'Marine_Courses': applicant.marine_courses or {},
#                 'Sea_Service_Details': applicant.sea_service_details or {},
#                 'Specialised_Experience': applicant.specialised_experience or {},
#                 'References': applicant.references or {},
#                 'Declaration': applicant.declaration or {},
#                 'Office_Use_Only': applicant.office_use_only or {},
#             }
            
#             # Handle certificates
#             certificate_names = DataMapperService.extract_certificates_from_data(structured_data)
#             if certificate_names:
#                 certificates = DataMapperService.find_or_create_certificates(certificate_names)
#                 user.certificates.set(certificates)
#                 logger.info(f"Added {len(certificates)} certificates to user")
            
#             # Handle references
#             references_data = DataMapperService.extract_references_from_data(structured_data)
#             for ref_data in references_data:
#                 if ref_data.get('name') or ref_data.get('company_name'):
#                     Reference.objects.create(user=user, **ref_data)
#             logger.info(f"Added {len(references_data)} references to user")
            
#             # Handle sea services
#             sea_services_data = DataMapperService.extract_sea_services_from_data(structured_data)
#             for service_data in sea_services_data:
#                 if service_data.get('vessel_name_imo') or service_data.get('company_name'):
#                     # Convert None dates to empty strings for fields that don't accept None
#                     if service_data.get('signed_on') is None:
#                         service_data.pop('signed_on', None)
#                     if service_data.get('signed_off') is None:
#                         service_data.pop('signed_off', None)
                    
#                     SeaService.objects.create(user=user, **service_data)
#             logger.info(f"Added {len(sea_services_data)} sea services to user")
            
#             return user
            
#         except Exception as e:
#             logger.error(f"Error saving applicant as user: {e}")
#             raise


# # Utility function to be used in views
# def convert_applicant_to_user(applicant_id: int) -> Users:
#     """
#     Convert an Applicant to a Users instance.
    
#     Args:
#         applicant_id: ID of the Applicant to convert
    
#     Returns:
#         Created Users instance
    
#     Raises:
#         Applicant.DoesNotExist: If applicant doesn't exist
#         ValidationError: If data validation fails
#     """
#     try:
#         applicant = Applicant.objects.get(id=applicant_id)
#         return DataMapperService.save_applicant_as_user(applicant)
#     except Applicant.DoesNotExist:
#         logger.error(f"Applicant with ID {applicant_id} not found")
#         raise
#     except Exception as e:
#         logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#         raise









# ai_document/data_mapper_service.py

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
import re

# Import models from both apps
from api.models import Users, Certificate, Rank, UserRank, Reference, SeaService
from ai_document.models import Applicant

logger = logging.getLogger(__name__)


class DataMapperService:
    """
    Service to map extracted JSON data to Users model fields.
    """
    
    @staticmethod
    def parse_date_string(date_str: str) -> Optional[datetime.date]:
        """
        Parse various date formats from extracted text.
        
        Args:
            date_str: Date string in various formats
        
        Returns:
            Parsed date object or None
        """
        if not date_str or not isinstance(date_str, str):
            return None
        
        # Clean the date string
        date_str = date_str.strip().replace('/', '-').replace(' ', '')
        
        # Try different date formats
        date_formats = [
            '%d-%m-%Y',  # 28-07-1975
            '%d-%m-%y',   # 28-07-75
            '%Y-%m-%d',   # 1975-07-28
            '%m-%d-%Y',   # 07-28-1975
            '%d%m%Y',    # 28071975
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # Try Django's built-in parser
        try:
            return parse_date(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse date: {date_str}")
            return None
    
    @staticmethod
    def extract_name_parts(full_name: str) -> Dict[str, str]:
        """
        Extract first, middle, and last name from full name.
        
        Args:
            full_name: Full name string
            
        Returns:
            Dictionary with first_name, middle_name, last_name
        """
        if not full_name:
            return {"first_name": "", "middle_name": "", "last_name": ""}
        
        name_parts = full_name.strip().split()
        if len(name_parts) == 1:
            return {"first_name": name_parts[0], "middle_name": "", "last_name": ""}
        else:
            return {
                "first_name": name_parts[0],
                "middle_name": " ".join(name_parts[1:]),
                "last_name": ""
            }
    
    @staticmethod
    def calculate_age_from_birth_date(birth_date_str: str) -> Optional[int]:
        """
        Calculate age from birth date string.
        
        Args:
            birth_date_str: Birth date string
            
        Returns:
            Age in years or None
        """
        birth_date = DataMapperService.parse_date_string(birth_date_str)
        if birth_date:
            today = datetime.now().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        return None
    
    @staticmethod
    def extract_phone_numbers(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract phone and tel numbers from data.
        
        Args:
            data: Dictionary containing contact information
            
        Returns:
            Dictionary with phone_number and tel_number
        """
        phone_number = ""
        tel_number = ""
        
        # Check Personal_Details
        personal = data.get("Personal_Details", {})
        contact = data.get("Contact_Details", {})
        
        # Get phone number
        phone_number = personal.get("phone", "") or contact.get("phone", "")
        
        # If there are multiple phone numbers, try to separate them
        if phone_number and "," in phone_number:
            phones = [p.strip() for p in phone_number.split(",")]
            phone_number = phones[0]
            if len(phones) > 1:
                tel_number = phones[1]
        
        return {"phone_number": phone_number, "tel_number": tel_number}
    
    @staticmethod
    def map_applicant_to_users(applicant: Applicant) -> Users:
        """
        Map an Applicant instance to a Users instance.
        
        Args:
            applicant: Applicant instance from ai_document app
        
        Returns:
            Users instance for api app
        """
        # Get the structured data - INCLUDING NEW FIELDS
        personal_details = applicant.personal_details or {}
        education = applicant.education or {}
        contact_details = applicant.contact_details or {}
        travel_documents = applicant.travel_documents or {}
        professional_qualifications = applicant.professional_qualifications or {}
        next_of_kin = applicant.next_of_kin_emergency_contact or {}
        health_certs = applicant.health_certificates_vaccinations or {}
        covid_vaccination = applicant.covid_19_vaccination or {}
        declaration = applicant.declaration or {}
        office_use = applicant.office_use_only or {}
        
        # NEW FIELDS - Access the new categories
        physical_measurements = applicant.physical_measurements or {}
        language_skills = applicant.language_skills or {}
        medical_history = applicant.medical_history or {}
        assessments = applicant.assessments or {}
        competency_tests = applicant.competency_tests or {}
        
        # Extract name parts
        full_name = personal_details.get('name', '')
        name_parts = DataMapperService.extract_name_parts(full_name)
        
        # Extract phone numbers
        phone_data = DataMapperService.extract_phone_numbers({
            "Personal_Details": personal_details,
            "Contact_Details": contact_details
        })
        
        # Calculate age
        birth_date_str = personal_details.get('birth_date', '')
        age = DataMapperService.calculate_age_from_birth_date(birth_date_str)
        
        # Create Users instance data
        user_data = {
            # Authentication & Basic Info
            'email': personal_details.get('email', '') or contact_details.get('email', ''),
            'first_name': name_parts['first_name'],
            'middle_name': name_parts['middle_name'],
            
            # Personal Info
            'age': age,
            'date_of_birth': DataMapperService.parse_date_string(birth_date_str),
            'nationality': personal_details.get('nationality', ''),
            'Place_Of_Birth': personal_details.get('place_of_birth', ''),
            'marital_status': personal_details.get('marital_status', 'Single'),
            
            # Contact Information
            'address': personal_details.get('address', '') or contact_details.get('address', ''),
            'phone_number': phone_data['phone_number'],
            'tel_number': phone_data['tel_number'],
            
            # Physical Details (default to 0 if not provided)
            'Height_Cm': 0,
            'Weight_Kg': 0,
            'blood_type': '',
            'smoker': False,
            
            # Education
            'college_or_school': '',
            'english_language_level': language_skills.get('english_language_level', '') or language_skills.get('english_level', ''),
            
            # Travel Documents - Passport
            'passport_no': '',
            'passport_issue_date': None,
            'passport_expiry_date': None,
            'passport_issued_by': '',
            'passport_place_of_issue': '',
            
            # Travel Documents - Seaman Book
            'seaman_book_no': '',
            'seaman_book_issue_date': None,
            'seaman_book_expiry_date': None,
            'seaman_book_issued_by': '',
            'seaman_book_place_of_issue': '',
            
            # Other Seaman Book
            'other_seaman_book_no': '',
            'other_seaman_book_issue_date': None,
            'other_seaman_book_expiry_date': None,
            'other_seaman_book_issued_by': '',
            'other_seaman_book_place_of_issue': '',
            
            # Professional Qualifications
            'coc_certificate_name': '',
            'coc_certificate_number': '',
            'coc_issue_date': None,
            'coc_expiry_date': None,
            'coc_issued_by': 'EAMS',
            'coc_issued_at': 'Alex.',
            
            # GOC Certificate
            'goc_certificate_number': '',
            'goc_issue_date': None,
            'goc_expiry_date': None,
            'goc_issued_by': 'NTRA',
            'goc_issued_at': 'Cairo',
            
            # Next of Kin
            'next_of_kin_full_name': next_of_kin.get('Full_Name', '') or next_of_kin.get('full_name', ''),
            'next_of_kin_relationship': next_of_kin.get('Relationship', '') or next_of_kin.get('relationship', ''),
            'next_of_kin_address_country': next_of_kin.get('Address_Country', '') or next_of_kin.get('address', ''),
            'next_of_kin_phone': next_of_kin.get('Tel_No', '') or next_of_kin.get('Mobile', '') or next_of_kin.get('phone', ''),
            'next_of_kin_email': next_of_kin.get('Email', '') or next_of_kin.get('email', ''),
            
            # Health Certificates
            'health_flag_state': health_certs.get('Flag_State', '') if isinstance(health_certs, dict) else '',
            'health_number': health_certs.get('Number', '') if isinstance(health_certs, dict) else '',
            'health_issue_date': DataMapperService.parse_date_string(health_certs.get('Issue_Date', '')) if isinstance(health_certs, dict) else None,
            'health_expiry_date': DataMapperService.parse_date_string(health_certs.get('Expiry_Date', '')) if isinstance(health_certs, dict) else None,
            'health_issued_by': health_certs.get('Issued_By', '') if isinstance(health_certs, dict) else '',
            'health_issued_at': health_certs.get('Issued_At', '') if isinstance(health_certs, dict) else '',
            
            # COVID Vaccination
            'covid_vaccine_name': covid_vaccination.get('Vaccination_Name', '') or covid_vaccination.get('vaccine_name', ''),
            'covid_first_dose': DataMapperService.parse_date_string(covid_vaccination.get('First_Dose', '') or covid_vaccination.get('first_dose', '')),
            'covid_second_dose': DataMapperService.parse_date_string(covid_vaccination.get('Second_Dose', '') or covid_vaccination.get('second_dose', '')),
            'covid_other_doses_or_remarks': covid_vaccination.get('Other_Doses_or_Remarks', '') or covid_vaccination.get('other_doses', ''),
            
            # Physical Details (sizes) - NOW MAPPED FROM physical_measurements
            'overall_size': physical_measurements.get('overall_size', '') or physical_measurements.get('Overall_Size', ''),
            'shirt_size': physical_measurements.get('shirt_size', '') or physical_measurements.get('Shirt_Size', ''),
            'trouser_size': physical_measurements.get('trouser_size', '') or physical_measurements.get('Trouser_Size', ''),
            'shoes_size': physical_measurements.get('shoes_size', '') or physical_measurements.get('Shoes_Size', ''),
            
            # Languages - NOW MAPPED FROM language_skills
            'other_language': language_skills.get('other_language', '') or language_skills.get('Other_Language', ''),
            'other_language_level': language_skills.get('other_language_level', '') or language_skills.get('Other_Language_Level', ''),
            
            # Medical History - NOW MAPPED FROM medical_history
            'disease_history': medical_history.get('disease_history', '') or medical_history.get('Disease_History', ''),
            'accident_history': medical_history.get('accident_history', '') or medical_history.get('Accident_History', ''),
            'psychiatric_treatment_history': medical_history.get('psychiatric_treatment_history', '') or medical_history.get('Psychiatric_Treatment_History', ''),
            'addiction_history': medical_history.get('addiction_history', '') or medical_history.get('Addiction_History', ''),
            
            # Declaration
            'declaration_consent': bool(declaration.get('Consent_Statement', False)),
            'declaration_date': DataMapperService.parse_date_string(declaration.get('Date', '')),
            'declaration_place': declaration.get('place', ''),
            
            # Office Use Only
            'initial_assessment_comments': office_use.get('Initial_assessment_of_applicant', '') or office_use.get('Comments', ''),
            'responsible_person_name': office_use.get('Responsible_person', '') or office_use.get('Name_Signature', ''),
            'assessment_date': DataMapperService.parse_date_string(office_use.get('Date', '')),
            
            # Marlins Test - NOW MAPPED FROM assessments and competency_tests
            'marlins_test_result': competency_tests.get('marlins_test_result', '') or assessments.get('marlins_test_result', ''),
            'marlins_test_issued_date': DataMapperService.parse_date_string(
                competency_tests.get('marlins_test_issued_date', '') or 
                assessments.get('marlins_test_issued_date', '')
            ),
            'marlins_test_issued_at': competency_tests.get('marlins_test_issued_at', '') or assessments.get('marlins_test_issued_at', ''),
            'marlins_test_issued_by': competency_tests.get('marlins_test_issued_by', '') or assessments.get('marlins_test_issued_by', ''),
        }
        
        # Handle education data
        if isinstance(education, dict):
            schools = education.get('schools', [])
            if isinstance(schools, list) and schools:
                # Extract school names
                school_names = []
                languages = []
                for school in schools:
                    if isinstance(school, dict):
                        if school.get('name'):
                            school_names.append(school['name'])
                        if school.get('languages'):
                            languages.extend(school['languages'])
                    elif isinstance(school, str):
                        school_names.append(school)
                
                user_data['college_or_school'] = ', '.join(school_names)
                if languages and not user_data['english_language_level']:
                    user_data['english_language_level'] = ', '.join(languages)
            
            # Handle languages at education level
            edu_languages = education.get('languages', [])
            if isinstance(edu_languages, list) and edu_languages and not user_data['english_language_level']:
                user_data['english_language_level'] = ', '.join(edu_languages)
        
        # Handle travel documents
        if isinstance(travel_documents, dict):
            # Passport details
            passport_details = travel_documents.get('passport_details', {})
            if isinstance(passport_details, dict):
                user_data.update({
                    'passport_no': passport_details.get('number', '') or passport_details.get('document_no', ''),
                    'passport_issue_date': DataMapperService.parse_date_string(passport_details.get('iss_date', '') or passport_details.get('issue_date', '')),
                    'passport_expiry_date': DataMapperService.parse_date_string(passport_details.get('exp_date', '') or passport_details.get('expiry_date', '')),
                    'passport_issued_by': passport_details.get('iss_by_authority', '') or passport_details.get('authority', ''),
                    'passport_place_of_issue': passport_details.get('place_of_issue', ''),
                })
            
            # Seaman book details
            seaman_book = travel_documents.get('seaman_book', {})
            if isinstance(seaman_book, dict):
                user_data.update({
                    'seaman_book_no': seaman_book.get('number', '') or seaman_book.get('book_no', ''),
                    'seaman_book_issue_date': DataMapperService.parse_date_string(seaman_book.get('iss_date', '') or seaman_book.get('issue_date', '')),
                    'seaman_book_expiry_date': DataMapperService.parse_date_string(seaman_book.get('exp_date', '') or seaman_book.get('expiry_date', '')),
                    'seaman_book_issued_by': seaman_book.get('iss_by_authority', '') or seaman_book.get('authority', ''),
                    'seaman_book_place_of_issue': seaman_book.get('place_of_issue', ''),
                })
            
            # Other seaman book
            other_seaman_book = travel_documents.get('other_seaman_book', {})
            if isinstance(other_seaman_book, dict) and other_seaman_book:
                user_data.update({
                    'other_seaman_book_no': other_seaman_book.get('number', '') or other_seaman_book.get('book_no', ''),
                    'other_seaman_book_issue_date': DataMapperService.parse_date_string(other_seaman_book.get('iss_date', '') or other_seaman_book.get('issue_date', '')),
                    'other_seaman_book_expiry_date': DataMapperService.parse_date_string(other_seaman_book.get('exp_date', '') or other_seaman_book.get('expiry_date', '')),
                    'other_seaman_book_issued_by': other_seaman_book.get('iss_by_authority', '') or other_seaman_book.get('authority', ''),
                    'other_seaman_book_place_of_issue': other_seaman_book.get('place_of_issue', ''),
                })
        
        # Handle professional qualifications
        if isinstance(professional_qualifications, dict):
            user_data.update({
                'coc_certificate_name': professional_qualifications.get('certificate_name', ''),
                'coc_certificate_number': professional_qualifications.get('number', ''),
                'coc_issue_date': DataMapperService.parse_date_string(professional_qualifications.get('issue_date', '')),
                'coc_expiry_date': DataMapperService.parse_date_string(professional_qualifications.get('expiry_date', '')),
                'coc_issued_by': professional_qualifications.get('issued_by', 'EAMS'),
                'coc_issued_at': professional_qualifications.get('issued_at', 'Alex.'),
            })
        
        # Remove None values and empty strings for optional fields
        cleaned_data = {}
        for key, value in user_data.items():
            if value is not None and value != '':
                cleaned_data[key] = value
        
        return Users(**cleaned_data)
    
    @staticmethod
    def extract_certificates_from_data(structured_data: Dict[str, Any]) -> List[str]:
        """
        Extract certificate names from various sections of the data.
        
        Args:
            structured_data: The extracted JSON data
        
        Returns:
            List of certificate names
        """
        certificates = []
        
        # Check Marine Courses
        marine_courses = structured_data.get("Marine_Courses", {})
        if isinstance(marine_courses, dict):
            training = marine_courses.get("training", [])
            if isinstance(training, list):
                for course in training:
                    if isinstance(course, dict):
                        name = course.get("course_name", "")
                        if name:
                            certificates.append(name)
                        
                        # Also check proficiency_in field
                        proficiency = course.get("proficiency_in", [])
                        if isinstance(proficiency, list):
                            certificates.extend(proficiency)
        
        return list(set(certificates))  # Remove duplicates
    
    @staticmethod
    def find_or_create_certificates(certificate_names: List[str]) -> List[Certificate]:
        """
        Find existing certificates or create new ones.
        
        Args:
            certificate_names: List of certificate names
        
        Returns:
            List of Certificate objects
        """
        certificates = []
        
        for cert_name in certificate_names:
            if not cert_name:
                continue
            
            # Try to find existing certificate by name (case-insensitive)
            cert = Certificate.objects.filter(name__icontains=cert_name).first()
            
            if not cert:
                # Create new certificate with a generated code
                code = cert_name.upper().replace(' ', '_')[:100]
                cert, created = Certificate.objects.get_or_create(
                    code=code,
                    defaults={'name': cert_name}
                )
                if created:
                    logger.info(f"Created new certificate: {cert_name}")
            
            certificates.append(cert)
        
        return certificates
    
    @staticmethod
    def extract_references_from_data(structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract reference data from the structured data.
        
        Args:
            structured_data: The extracted JSON data
        
        Returns:
            List of reference dictionaries
        """
        references = []
        
        refs_data = structured_data.get("References", {})
        if isinstance(refs_data, list):
            # References is a list
            for ref in refs_data:
                if isinstance(ref, dict):
                    references.append({
                        'company_name': ref.get('Company_Management_Country', '') or ref.get('company_name', ''),
                        'position': ref.get('Position', '') or ref.get('position', ''),
                        'name': ref.get('Name', '') or ref.get('name', ''),
                        'tel': ref.get('TEL', '') or ref.get('tel', '') or ref.get('phone', ''),
                        'email': ref.get('EMAIL', '') or ref.get('email', ''),
                    })
        elif isinstance(refs_data, dict):
            # References is a dict with a list inside
            ref_list = refs_data.get('references', [])
            if isinstance(ref_list, list):
                for ref in ref_list:
                    if isinstance(ref, dict):
                        references.append({
                            'company_name': ref.get('Company_Management_Country', '') or ref.get('company_name', ''),
                            'position': ref.get('Position', '') or ref.get('position', ''),
                            'name': ref.get('Name', '') or ref.get('name', ''),
                            'tel': ref.get('TEL', '') or ref.get('tel', '') or ref.get('phone', ''),
                            'email': ref.get('EMAIL', '') or ref.get('email', ''),
                        })
        
        return references
    
    @staticmethod
    def extract_sea_services_from_data(structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract sea service data from the structured data.
        
        Args:
            structured_data: The extracted JSON data
        
        Returns:
            List of sea service dictionaries
        """
        sea_services = []
        
        sea_service_data = structured_data.get("Sea_Service_Details", {})
        if isinstance(sea_service_data, dict):
            ship_exp = sea_service_data.get("ship_experience", [])
            if isinstance(ship_exp, list):
                for service in ship_exp:
                    if isinstance(service, dict):
                        sea_services.append({
                            'company_name': service.get('Company_Name', '') or service.get('company_name', ''),
                            'rank': service.get('Rank', '') or service.get('rank', ''),
                            'vessel_name_imo': service.get('Vessel_Name_IMO_Number', '') or service.get('vessel_name', ''),
                            'flag': service.get('Flag', '') or service.get('flag', ''),
                            'signed_on': DataMapperService.parse_date_string(service.get('Signed_On', '') or service.get('signed_on', '')),
                            'signed_off': DataMapperService.parse_date_string(service.get('Signed_Off', '') or service.get('signed_off', '')),
                            'period': service.get('Period', '') or service.get('period', ''),
                            'vessel_type': service.get('Vessel_Type', '') or service.get('vessel_type', ''),
                            'dwt': service.get('DWT', '') or service.get('dwt', ''),
                            'grt': service.get('GRT', '') or service.get('grt', ''),
                            'engine_type': service.get('Engine_Type', '') or service.get('engine_type', ''),
                            'bh': service.get('BH', '') or service.get('bh', ''),
                            'kw': service.get('KW', '') or service.get('kw', ''),
                            'reason_for_sign_off': service.get('Reason_for_Sign_off', '') or service.get('reason_for_sign_off', ''),
                        })
        
        return sea_services
    
    @staticmethod
    @transaction.atomic
    def save_applicant_as_user(applicant: Applicant) -> Users:
        """
        Convert an Applicant to a Users instance and save it with all relationships.
        
        Args:
            applicant: Applicant instance from ai_document app
        
        Returns:
            Created Users instance
        """
        try:
            # Create the base Users instance
            user = DataMapperService.map_applicant_to_users(applicant)
            
            # Validate email
            if not user.email:
                raise ValidationError("Email is required")
            
            # Check if user already exists
            existing_user = Users.objects.filter(email=user.email).first()
            if existing_user:
                logger.info(f"User with email {user.email} already exists. Updating existing user.")
                # Update existing user
                for field, value in user.__dict__.items():
                    if not field.startswith('_') and value is not None:
                        setattr(existing_user, field, value)
                existing_user.save()
                user = existing_user
            else:
                # Set a default password for new users
                user.set_password('defaultpassword123')  # You should change this
                user.save()
                logger.info(f"Created new user: {user.email}")
            
            # Get all structured data for relationships - INCLUDING NEW FIELDS
            structured_data = {
                'Personal_Details': applicant.personal_details or {},
                'Education': applicant.education or {},
                'Contact_Details': applicant.contact_details or {},
                'Travel_Documents': applicant.travel_documents or {},
                'Professional_Qualifications': applicant.professional_qualifications or {},
                'Next_of_Kin_Emergency_Contact': applicant.next_of_kin_emergency_contact or {},
                'Health_Certificates_Vaccinations': applicant.health_certificates_vaccinations or {},
                'Covid_19_Vaccination': applicant.covid_19_vaccination or {},
                'Marine_Courses': applicant.marine_courses or {},
                'Sea_Service_Details': applicant.sea_service_details or {},
                'Specialised_Experience': applicant.specialised_experience or {},
                'References': applicant.references or {},
                'Declaration': applicant.declaration or {},
                'Office_Use_Only': applicant.office_use_only or {},
                'Physical_Measurements': applicant.physical_measurements or {},
                'Language_Skills': applicant.language_skills or {},
                'Medical_History': applicant.medical_history or {},
                'Assessments': applicant.assessments or {},
                'Competency_Tests': applicant.competency_tests or {},
            }
            
            # Handle certificates
            certificate_names = DataMapperService.extract_certificates_from_data(structured_data)
            if certificate_names:
                certificates = DataMapperService.find_or_create_certificates(certificate_names)
                user.certificates.set(certificates)
                logger.info(f"Added {len(certificates)} certificates to user")
            
            # Handle references
            references_data = DataMapperService.extract_references_from_data(structured_data)
            for ref_data in references_data:
                if ref_data.get('name') or ref_data.get('company_name'):
                    Reference.objects.create(user=user, **ref_data)
            logger.info(f"Added {len(references_data)} references to user")
            
            # Handle sea services
            sea_services_data = DataMapperService.extract_sea_services_from_data(structured_data)
            for service_data in sea_services_data:
                if service_data.get('vessel_name_imo') or service_data.get('company_name'):
                    # Convert None dates to empty strings for fields that don't accept None
                    if service_data.get('signed_on') is None:
                        service_data.pop('signed_on', None)
                    if service_data.get('signed_off') is None:
                        service_data.pop('signed_off', None)
                    
                    SeaService.objects.create(user=user, **service_data)
            logger.info(f"Added {len(sea_services_data)} sea services to user")
            
            return user
            
        except Exception as e:
            logger.error(f"Error saving applicant as user: {e}")
            raise


# Utility function to be used in views
def convert_applicant_to_user(applicant_id: int) -> Users:
    """
    Convert an Applicant to a Users instance.
    
    Args:
        applicant_id: ID of the Applicant to convert
    
    Returns:
        Created Users instance
    
    Raises:
        Applicant.DoesNotExist: If applicant doesn't exist
        ValidationError: If data validation fails
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)
        return DataMapperService.save_applicant_as_user(applicant)
    except Applicant.DoesNotExist:
        logger.error(f"Applicant with ID {applicant_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error converting applicant {applicant_id} to user: {e}")
        raise