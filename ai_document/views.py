










# import re
# import logging
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json  # Use the fixed version
# from .models import Applicant

# from .models import Applicant
# from .serializers import DocumentUploadSerializer
import logging
from decimal import Decimal, InvalidOperation
from datetime import date, datetime

logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#    """
#    Clean extracted text:
#    - Remove duplicate lines
#    - Remove repeated inline values (tables)
#    - Strip common headers/footers (boilerplate repeated across pages)
#    """
#    lines = [line.strip() for line in text.splitlines() if line.strip()]

#    # Count line frequency
#    freq = Counter(lines)

#    # If a line appears on >= 5 pages, treat as boilerplate
#    boilerplate = {line for line, count in freq.items() if count >= 5}

#    cleaned_lines = []
#    seen = set()
#    for line in lines:
#    if line in boilerplate:
#    continue  # skip repeating headers/footers

#    # Collapse table duplicates (split by | or big spaces)
#    if "|" in line:
#    parts = [p.strip() for p in line.split("|")]
#    unique_parts = []
#    for p in parts:
#    if not unique_parts or p != unique_parts[-1]:
#    unique_parts.append(p)
#    line = " | ".join(unique_parts)

#    # Collapse repeated words like "Confidential Confidential Confidential"
#    line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#    # Avoid full-line duplicates
#    if line not in seen:
#    seen.add(line)
#    cleaned_lines.append(line)

#    return "\n".join(cleaned_lines)


# class DocumentUploadView(APIView):
#    """
#    Upload a document (PDF or DOCX), extract text, convert to structured JSON,
#    save into Applicant table, and return the response.
#    """

#    def post(self, request, *args, **kwargs):
#    file = request.FILES.get("file")
#    if not file:
#    return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#    # Save file temporarily
#    file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#    processor = DocumentProcessor()
#    try:
#    result = processor.process_document(default_storage.path(file_path))

#    # Step 1: Clean extracted text
#    cleaned_text = clean_text(result.get("extracted_text", ""))

#    # Step 2: Convert text into structured JSON using LangChain + Ollama
#    # This now returns a dictionary, not a string
#    structured_json = convert_text_to_json(cleaned_text)
    
#    # Ensure structured_json is a dictionary
#    if not isinstance(structured_json, dict):
#    logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
#    structured_json = {
#    "Personal_Details": {},
#    "Education": {},
#    "Contact_Details": {},
#    "Travel_Documents": {},
#    "Professional_Qualifications": {},
#    "Next_of_Kin_Emergency_Contact": {},
#    "Health_Certificates_Vaccinations": {},
#    "Covid_19_Vaccination": {},
#    "Marine_Courses": {},
#    "Sea_Service_Details": {},
#    "Specialised_Experience": {},
#    "References": {},
#    "Declaration": {},
#    "Office_Use_Only": {},
#    "error": f"Unexpected return type: {type(structured_json)}"
#    }

#    # Step 3: Save structured data into Applicant model
#    try:
#    applicant = Applicant.objects.create(
#    personal_details=structured_json.get("Personal_Details", {}),
#    education=structured_json.get("Education", {}),
#    contact_details=structured_json.get("Contact_Details", {}),
#    travel_documents=structured_json.get("Travel_Documents", {}),
#    professional_qualifications=structured_json.get("Professional_Qualifications", {}),
#    next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#    health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
#    covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
#    marine_courses=structured_json.get("Marine_Courses", {}),
#    sea_service_details=structured_json.get("Sea_Service_Details", {}),
#    specialised_experience=structured_json.get("Specialised_Experience", {}),
#    references=structured_json.get("References", {}),
#    declaration=structured_json.get("Declaration", {}),
#    office_use_only=structured_json.get("Office_Use_Only", {}),
#    )
    
#    logger.info(f"Successfully created applicant with ID: {applicant.id}")
    
#    except Exception as db_error:
#    logger.error(f"Database save error: {db_error}")
#    # Clean up file and return error
#    default_storage.delete(file_path)
#    return Response({
#    "error": "Failed to save data to database",
#    "details": str(db_error)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#    # Clean up file after processing
#    default_storage.delete(file_path)

#    # Determine response status based on parsing quality
#    response_status = status.HTTP_200_OK
#    message = "Data saved successfully"
    
#    if "error" in structured_json:
#    response_status = status.HTTP_206_PARTIAL_CONTENT
#    message = "Data saved with parsing issues"

#    return Response({
#    "message": message,
#    "applicant_id": applicant.id,
#    "file_name": file.name,
#    "structured_data": structured_json,
#    "page_count": result.get("page_count"),
#    "word_count": len(cleaned_text.split()),
#    "parsing_quality": "low" if "error" in structured_json else "high"
#    }, status=response_status)

#    except DocumentProcessingError as e:
#    # Clean up file on error
#    try:
#    default_storage.delete(file_path)
#    except:
#    pass
#    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#    except Exception as e:
#    # Clean up file on error
#    try:
#    default_storage.delete(file_path)
#    except:
#    pass
#    logger.error(f"Unexpected error: {e}")
#    return Response({
#    "error": "Internal server error",
#    "details": str(e)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantListView(APIView):
#    """
#    List all applicants.
#    """
    
#    def get(self, request, *args, **kwargs):
#    try:
#    applicants = Applicant.objects.all().order_by('-created_at')
    
#    applicant_list = []
#    for applicant in applicants:
#    applicant_data = {
#    "id": applicant.id,
#    "name": applicant.personal_details.get("name", "Unknown") if applicant.personal_details else "Unknown",
#    "email": applicant.contact_details.get("email", "") if applicant.contact_details else "",
#    "nationality": applicant.personal_details.get("nationality", "") if applicant.personal_details else "",
#    "created_at": applicant.created_at.isoformat(),
#    }
#    applicant_list.append(applicant_data)
    
#    return Response({
#    "success": True,
#    "count": len(applicant_list),
#    "applicants": applicant_list
#    }, status=status.HTTP_200_OK)
    
#    except Exception as e:
#    logger.error(f"Error listing applicants: {e}")
#    return Response({
#    "error": "Failed to retrieve applicants",
#    "details": str(e)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantDetailView(APIView):
#    """
#    Get detailed information about a specific applicant.
#    """
    
#    def get(self, request, applicant_id, *args, **kwargs):
#    try:
#    applicant = Applicant.objects.get(id=applicant_id)
    
#    return Response({
#    "success": True,
#    "applicant": {
#    "id": applicant.id,
#    "personal_details": applicant.personal_details,
#    "education": applicant.education,
#    "contact_details": applicant.contact_details,
#    "travel_documents": applicant.travel_documents,
#    "professional_qualifications": applicant.professional_qualifications,
#    "next_of_kin_emergency_contact": applicant.next_of_kin_emergency_contact,
#    "health_certificates_vaccinations": applicant.health_certificates_vaccinations,
#    "covid_19_vaccination": applicant.covid_19_vaccination,
#    "marine_courses": applicant.marine_courses,
#    "sea_service_details": applicant.sea_service_details,
#    "specialised_experience": applicant.specialised_experience,
#    "references": applicant.references,
#    "declaration": applicant.declaration,
#    "office_use_only": applicant.office_use_only,
#    "created_at": applicant.created_at.isoformat(),
#    "updated_at": applicant.updated_at.isoformat(),
#    }
#    }, status=status.HTTP_200_OK)
    
#    except Applicant.DoesNotExist:
#    return Response({
#    "error": f"Applicant with ID {applicant_id} not found"
#    }, status=status.HTTP_404_NOT_FOUND)
    
#    except Exception as e:
#    logger.error(f"Error retrieving applicant {applicant_id}: {e}")
#    return Response({
#    "error": "Failed to retrieve applicant",
#    "details": str(e)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# """
# Integrated Document Upload View that saves extracted data to both:
# 1. ai_document.Applicant model (JSON format)
# 2. api.Users model (individual fields)

# This view processes documents and automatically syncs data between both apps.
# """

# import re
# import logging
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from django.db import transaction
# from django.core.exceptions import ValidationError

# # Import from ai_document app
# from ai_document.document_processor import DocumentProcessor, DocumentProcessingError
# from ai_document.document_to_json import convert_text_to_json
# from ai_document.models import Applicant

# # Import from api app
# from api.models import Users

# # Import the data mapper service
# from .data_mapper_service import DataMapperService

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#    """
#    Clean extracted text:
#    - Remove duplicate lines
#    - Remove repeated inline values (tables)
#    - Strip common headers/footers (boilerplate repeated across pages)
#    """
#    lines = [line.strip() for line in text.splitlines() if line.strip()]

#    # Count line frequency
#    freq = Counter(lines)

#    # If a line appears on >= 5 pages, treat as boilerplate
#    boilerplate = {line for line, count in freq.items() if count >= 5}

#    cleaned_lines = []
#    seen = set()
#    for line in lines:
#    if line in boilerplate:
#    continue  # skip repeating headers/footers

#    # Collapse table duplicates (split by | or big spaces)
#    if "|" in line:
#    parts = [p.strip() for p in line.split("|")]
#    unique_parts = []
#    for p in parts:
#    if not unique_parts or p != unique_parts[-1]:
#    unique_parts.append(p)
#    line = " | ".join(unique_parts)

#    # Collapse repeated words like "Confidential Confidential Confidential"
#    line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#    # Avoid full-line duplicates
#    if line not in seen:
#    seen.add(line)
#    cleaned_lines.append(line)

#    return "\n".join(cleaned_lines)


# class IntegratedDocumentUploadView(APIView):
#    """
#    Upload a document (PDF or DOCX), extract text, convert to structured JSON,
#    save into both Applicant table (ai_document app) and Users table (api app).
#    """

#    def post(self, request, *args, **kwargs):
#    """
#    Handle document upload and processing with dual database saving.
#    """
#    file = request.FILES.get("file")
#    if not file:
#    return Response({
#    "success": False,
#    "error": "No file uploaded"
#    }, status=status.HTTP_400_BAD_REQUEST)

#    # Validate file type
#    allowed_extensions = ['.pdf', '.docx']
#    file_extension = file.name.lower().split('.')[-1] if '.' in file.name else ''
#    if f'.{file_extension}' not in allowed_extensions:
#    return Response({
#    "success": False,
#    "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
#    }, status=status.HTTP_400_BAD_REQUEST)

#    # Save file temporarily
#    try:
#    file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))
#    except Exception as e:
#    logger.error(f"Failed to save uploaded file: {e}")
#    return Response({
#    "success": False,
#    "error": "Failed to save uploaded file"
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#    processor = DocumentProcessor()
    
#    try:
#    with transaction.atomic():
#    # Step 1: Extract text from document
#    logger.info(f"Processing document: {file.name}")
#    result = processor.process_document(default_storage.path(file_path))

#    # Step 2: Clean extracted text
#    cleaned_text = clean_text(result.get("extracted_text", ""))
#    logger.info(f"Extracted {len(cleaned_text)} characters from document")

#    # Step 3: Convert text into structured JSON using LangChain + Ollama
#    logger.info("Converting text to structured JSON")
#    structured_json = convert_text_to_json(cleaned_text)

#    # Ensure structured_json is a dictionary
#    if not isinstance(structured_json, dict):
#    logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
#    structured_json = {
#    "Personal_Details": {},
#    "Education": {},
#    "Contact_Details": {},
#    "Travel_Documents": {},
#    "Professional_Qualifications": {},
#    "Next_of_Kin_Emergency_Contact": {},
#    "Health_Certificates_Vaccinations": {},
#    "Covid_19_Vaccination": {},
#    "Marine_Courses": {},
#    "Sea_Service_Details": {},
#    "Specialised_Experience": {},
#    "References": {},
#    "Declaration": {},
#    "Office_Use_Only": {},
#    "error": f"Unexpected return type: {type(structured_json)}"
#    }

#    # Step 4: Save to ai_document.Applicant model (JSON format)
#    logger.info("Saving to Applicant model")
#    applicant = Applicant.objects.create(
#    personal_details=structured_json.get("Personal_Details", {}),
#    education=structured_json.get("Education", {}),
#    contact_details=structured_json.get("Contact_Details", {}),
#    travel_documents=structured_json.get("Travel_Documents", {}),
#    professional_qualifications=structured_json.get("Professional_Qualifications", {}),
#    next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#    health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
#    covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
#    marine_courses=structured_json.get("Marine_Courses", {}),
#    sea_service_details=structured_json.get("Sea_Service_Details", {}),
#    specialised_experience=structured_json.get("Specialised_Experience", {}),
#    references=structured_json.get("References", {}),
#    declaration=structured_json.get("Declaration", {}),
#    office_use_only=structured_json.get("Office_Use_Only", {}),
#    )
#    logger.info(f"Successfully created applicant with ID: {applicant.id}")

#    # Step 5: Convert and save to api.Users model (individual fields)
#    user = None
#    user_error = None
#    try:
#    logger.info("Converting applicant to Users model")
#    user = DataMapperService.save_applicant_as_user(applicant)
#    logger.info(f"Successfully created/updated user: {user.email} (ID: {user.id})")
#    except ValidationError as ve:
#    user_error = f"Validation error: {str(ve)}"
#    logger.warning(f"Failed to create user due to validation: {ve}")
#    except Exception as ue:
#    user_error = f"User creation error: {str(ue)}"
#    logger.error(f"Failed to create user: {ue}")

#    # Clean up file after processing
#    try:
#    default_storage.delete(file_path)
#    except Exception as e:
#    logger.warning(f"Failed to delete temporary file: {e}")

#    # Step 6: Prepare response
#    response_data = {
#    "file_name": file.name,
#    "applicant_id": applicant.id,
#    "user_id": user.id if user else None,
#    "user_email": user.email if user else None,
#    "structured_data": structured_json,
#    "page_count": result.get("page_count"),
#    "word_count": len(cleaned_text.split()),
#    "parsing_quality": "low" if "error" in structured_json else "high",
#    "user_creation_status": "success" if user else "failed",
#    "user_error": user_error,
#    }

#    # Determine response status
#    if user:
#    message = "Document processed and saved to both databases successfully"
#    response_status = status.HTTP_200_OK
#    else:
#    message = "Document processed and saved to Applicant database, but failed to save to Users database"
#    response_status = status.HTTP_206_PARTIAL_CONTENT

#    return Response({
#    "success": True,
#    "message": message,
#    "data": response_data
#    }, status=response_status)

#    except DocumentProcessingError as e:
#    logger.error(f"Document processing error: {e}")
#    # Clean up file on error
#    try:
#    default_storage.delete(file_path)
#    except:
#    pass
    
#    return Response({
#    "success": False,
#    "error": "Document processing failed",
#    "details": str(e)
#    }, status=status.HTTP_400_BAD_REQUEST)
    
#    except Exception as e:
#    logger.error(f"Unexpected error during document processing: {e}")
#    # Clean up file on error
#    try:
#    default_storage.delete(file_path)
#    except:
#    pass
    
#    return Response({
#    "success": False,
#    "error": "Internal server error",
#    "details": str(e)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ConvertApplicantToUserView(APIView):
#    """
#    Convert an existing Applicant to a Users instance.
#    Useful for batch processing or re-processing existing data.
#    """
    
#    def post(self, request, *args, **kwargs):
#    """
#    Convert an applicant to a user.
    
#    Expected payload:
#    {
#    "applicant_id": 123
#    }
#    """
#    applicant_id = request.data.get('applicant_id')
    
#    if not applicant_id:
#    return Response({
#    "success": False,
#    "error": "applicant_id is required"
#    }, status=status.HTTP_400_BAD_REQUEST)
    
#    try:
#    applicant = Applicant.objects.get(id=applicant_id)
#    except Applicant.DoesNotExist:
#    return Response({
#    "success": False,
#    "error": f"Applicant with ID {applicant_id} not found"
#    }, status=status.HTTP_404_NOT_FOUND)
    
#    try:
#    with transaction.atomic():
#    user = DataMapperService.save_applicant_as_user(applicant)
    
#    return Response({
#    "success": True,
#    "message": "Applicant converted to user successfully",
#    "data": {
#    "applicant_id": applicant.id,
#    "user_id": user.id,
#    "user_email": user.email,
#    "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
#    }
#    }, status=status.HTTP_200_OK)
    
#    except ValidationError as e:
#    return Response({
#    "success": False,
#    "error": "Validation error",
#    "details": str(e)
#    }, status=status.HTTP_400_BAD_REQUEST)
    
#    except Exception as e:
#    logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#    return Response({
#    "success": False,
#    "error": "Failed to convert applicant to user",
#    "details": str(e)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class BatchConvertApplicantsView(APIView):
#    """
#    Convert multiple applicants to users in batch.
#    """
    
#    def post(self, request, *args, **kwargs):
#    """
#    Convert multiple applicants to users.
    
#    Expected payload:
#    {
#    "applicant_ids": [1, 2, 3, 4, 5]
#    }
#    or
#    {
#    "convert_all": true  // Convert all applicants
#    }
#    """
#    applicant_ids = request.data.get('applicant_ids', [])
#    convert_all = request.data.get('convert_all', False)
    
#    if convert_all:
#    applicants = Applicant.objects.all()
#    elif applicant_ids:
#    applicants = Applicant.objects.filter(id__in=applicant_ids)
#    else:
#    return Response({
#    "success": False,
#    "error": "Either applicant_ids or convert_all=true is required"
#    }, status=status.HTTP_400_BAD_REQUEST)
    
#    results = {
#    "total_applicants": applicants.count(),
#    "successful_conversions": 0,
#    "failed_conversions": 0,
#    "errors": []
#    }
    
#    for applicant in applicants:
#    try:
#    with transaction.atomic():
#    user = DataMapperService.save_applicant_as_user(applicant)
#    results["successful_conversions"] += 1
#    logger.info(f"Successfully converted applicant {applicant.id} to user {user.id}")
    
#    except Exception as e:
#    results["failed_conversions"] += 1
#    error_msg = f"Applicant {applicant.id}: {str(e)}"
#    results["errors"].append(error_msg)
#    logger.error(f"Failed to convert applicant {applicant.id}: {e}")
    
#    return Response({
#    "success": True,
#    "message": f"Batch conversion completed. {results['successful_conversions']} successful, {results['failed_conversions']} failed.",
#    "data": results
#    }, status=status.HTTP_200_OK)


# class SyncStatusView(APIView):
#    """
#    Check sync status between Applicant and Users models.
#    """
    
#    def get(self, request, *args, **kwargs):
#    """
#    Get sync status between the two databases.
#    """
#    try:
#    total_applicants = Applicant.objects.count()
#    total_users = Users.objects.count()
    
#    # Find applicants without corresponding users (by email)
#    applicant_emails = set()
#    for applicant in Applicant.objects.all():
#    personal_details = applicant.personal_details or {}
#    contact_details = applicant.contact_details or {}
#    email = personal_details.get('email') or contact_details.get('email')
#    if email:
#    applicant_emails.add(email.lower())
    
#    user_emails = set(Users.objects.values_list('email', flat=True))
#    user_emails = {email.lower() for email in user_emails if email}
    
#    unsynced_emails = applicant_emails - user_emails
    
#    return Response({
#    "success": True,
#    "data": {
#    "total_applicants": total_applicants,
#    "total_users": total_users,
#    "applicants_with_email": len(applicant_emails),
#    "users_with_email": len(user_emails),
#    "unsynced_applicants": len(unsynced_emails),
#    "unsynced_emails": list(unsynced_emails)[:10],  # Show first 10
#    "sync_percentage": round((len(user_emails) / len(applicant_emails)) * 100, 2) if applicant_emails else 0
#    }
#    }, status=status.HTTP_200_OK)
    
#    except Exception as e:
#    logger.error(f"Error getting sync status: {e}")
#    return Response({
#    "success": False,
#    "error": "Failed to get sync status",
#    "details": str(e)
#    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json
# from .models import Applicant
# from .data_mapper_service import DataMapperService
# import logging

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#    """
#    Clean extracted text:
#    - Remove duplicate lines
#    - Remove repeated inline values (tables)
#    - Strip common headers/footers (boilerplate repeated across pages)
#    """
#    lines = [line.strip() for line in text.splitlines() if line.strip()]

#    # Count line frequency
#    freq = Counter(lines)

#    # If a line appears on >= 5 pages, treat as boilerplate
#    boilerplate = {line for line, count in freq.items() if count >= 5}

#    cleaned_lines = []
#    seen = set()
#    for line in lines:
#    if line in boilerplate:
#    continue  # skip repeating headers/footers

#    # Collapse table duplicates (split by | or big spaces)
#    if "|" in line:
#    parts = [p.strip() for p in line.split("|")]
#    unique_parts = []
#    for p in parts:
#    if not unique_parts or p != unique_parts[-1]:
#    unique_parts.append(p)
#    line = " | ".join(unique_parts)

#    # Collapse repeated words like "Confidential Confidential Confidential"
#    line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#    # Avoid full-line duplicates
#    if line not in seen:
#    seen.add(line)
#    cleaned_lines.append(line)

#    return "\n".join(cleaned_lines)


# class DocumentUploadView(APIView):
#    """
#    Upload a document (PDF or DOCX), extract text, convert to structured JSON,
#    save into Applicant table, and return the response.
#    """

#    def post(self, request, *args, **kwargs):
#    file = request.FILES.get("file")
#    if not file:
#    return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#    # Save file temporarily
#    file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#    processor = DocumentProcessor()
#    try:
#    result = processor.process_document(default_storage.path(file_path))

#    # Step 1: Clean extracted text
#    cleaned_text = clean_text(result.get("extracted_text", ""))

#    # Step 2: Convert text into structured JSON using LangChain + Ollama
#    structured_json = convert_text_to_json(cleaned_text)

#    # Step 3: Save structured data into Applicant model
#    applicant = Applicant.objects.create(
#    personal_details = structured_json.get("Personal_Details", {}),
#    education = structured_json.get("Education", {}),
#    contact_details = structured_json.get("Contact_Details", {}),
#    travel_documents = structured_json.get("Travel_Documents", {}),
#    professional_qualifications = structured_json.get("Professional_Qualifications", {}),
#    next_of_kin_emergency_contact = structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#    health_certificates_vaccinations = structured_json.get("Health_Certificates_Vaccinations", {}),
#    covid_19_vaccination = structured_json.get("Covid_19_Vaccination", {}),
#    marine_courses = structured_json.get("Marine_Courses", {}),
#    sea_service_details = structured_json.get("Sea_Service_Details", {}),
#    specialised_experience = structured_json.get("Specialised_Experience", {}),
#    references = structured_json.get("References", {}),
#    declaration = structured_json.get("Declaration", {}),
#    office_use_only = structured_json.get("Office_Use_Only", {}),
#    )

#    # Clean up file after processing
#    default_storage.delete(file_path)

#    return Response({
#    "message": "Data saved successfully",
#    "applicant_id": applicant.id,
#    "file_name": file.name,
#    "structured_data": structured_json,
#    "page_count": result.get("page_count"),
#    "word_count": len(cleaned_text.split()),
#    }, status=status.HTTP_200_OK)

#    except DocumentProcessingError as e:
#    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class IntegratedDocumentUploadView(APIView):
#    """
#    Upload a document, process it, and save data to both Applicant and Users models.
#    Also handles GET requests to check sync status.
#    """

#    def post(self, request, *args, **kwargs):
#    """Handle document upload and save to both models."""
#    file = request.FILES.get("file")
#    if not file:
#    return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#    # Save file temporarily
#    file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#    processor = DocumentProcessor()
#    try:
#    result = processor.process_document(default_storage.path(file_path))

#    # Step 1: Clean extracted text
#    cleaned_text = clean_text(result.get("extracted_text", ""))

#    # Step 2: Convert text into structured JSON
#    structured_json = convert_text_to_json(cleaned_text)

#    # Step 3: Save to Applicant model
#    applicant = Applicant.objects.create(
#    personal_details = structured_json.get("Personal_Details", {}),
#    education = structured_json.get("Education", {}),
#    contact_details = structured_json.get("Contact_Details", {}),
#    travel_documents = structured_json.get("Travel_Documents", {}),
#    professional_qualifications = structured_json.get("Professional_Qualifications", {}),
#    next_of_kin_emergency_contact = structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#    health_certificates_vaccinations = structured_json.get("Health_Certificates_Vaccinations", {}),
#    covid_19_vaccination = structured_json.get("Covid_19_Vaccination", {}),
#    marine_courses = structured_json.get("Marine_Courses", {}),
#    sea_service_details = structured_json.get("Sea_Service_Details", {}),
#    specialised_experience = structured_json.get("Specialised_Experience", {}),
#    references = structured_json.get("References", {}),
#    declaration = structured_json.get("Declaration", {}),
#    office_use_only = structured_json.get("Office_Use_Only", {}),
#    )

#    # Step 4: Map and save to Users model
#    user_data = DataMapperService.map_applicant_to_user(structured_json)
#    user = DataMapperService.save_to_users_model(user_data)

#    # Clean up file after processing
#    default_storage.delete(file_path)

#    response_data = {
#    "message": "Data saved successfully to both models",
#    "applicant_id": applicant.id,
#    "file_name": file.name,
#    "structured_data": structured_json,
#    "page_count": result.get("page_count"),
#    "word_count": len(cleaned_text.split()),
#    "sync_status": {
#    "applicant_saved": True,
#    "user_saved": user is not None,
#    "user_id": user.id if user else None
#    }
#    }

#    if user is None:
#    response_data["warning"] = "Data saved to Applicant model but failed to save to Users model"
#    logger.warning(f"Failed to save applicant {applicant.id} to Users model")

#    return Response(response_data, status=status.HTTP_200_OK)

#    except DocumentProcessingError as e:
#    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#    except Exception as e:
#    logger.error(f"Unexpected error in IntegratedDocumentUploadView: {str(e)}")
#    return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#    def get(self, request, applicant_id=None, *args, **kwargs):
#    """Check sync status for a specific applicant."""
#    if not applicant_id:
#    return Response({"error": "Applicant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#    try:
#    # Check if applicant exists
#    applicant = Applicant.objects.get(id=applicant_id)
    
#    # Try to find corresponding user by email or passport
#    user = None
#    email = applicant.contact_details.get("email")
#    passport_number = applicant.travel_documents.get("passport_number")
    
#    if email:
#    from api.models import Users
#    user = Users.objects.filter(email=email).first()
#    elif passport_number:
#    from api.models import Users
#    user = Users.objects.filter(passport_number=passport_number).first()

#    return Response({
#    "applicant_id": applicant_id,
#    "synced": user is not None,
#    "user_id": user.id if user else None,
#    "sync_date": user.created_at if user and hasattr(user, 'created_at') else None,
#    "applicant_created": applicant.created_at
#    }, status=status.HTTP_200_OK)

#    except Applicant.DoesNotExist:
#    return Response({"error": "Applicant not found"}, status=status.HTTP_404_NOT_FOUND)
#    except Exception as e:
#    logger.error(f"Error checking sync status: {str(e)}")
#    return Response({"error": "Error checking sync status"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json
# from api.models import Users
# import logging
# from django.db import transaction

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#    """
#    Clean extracted text:
#    - Remove duplicate lines
#    - Remove repeated inline values (tables)
#    - Strip common headers/footers (boilerplate repeated across pages)
#    """
#    lines = [line.strip() for line in text.splitlines() if line.strip()]

#    # Count line frequency
#    freq = Counter(lines)

#    # If a line appears on >= 5 pages, treat as boilerplate
#    boilerplate = {line for line, count in freq.items() if count >= 5}

#    cleaned_lines = []
#    seen = set()
#    for line in lines:
#    if line in boilerplate:
#    continue  # skip repeating headers/footers

#    # Collapse table duplicates (split by | or big spaces)
#    if "|" in line:
#    parts = [p.strip() for p in line.split("|")]
#    unique_parts = []
#    for p in parts:
#    if not unique_parts or p != unique_parts[-1]:
#    unique_parts.append(p)
#    line = " | ".join(unique_parts)

#    # Collapse repeated words like "Confidential Confidential Confidential"
#    line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#    # Avoid full-line duplicates
#    if line not in seen:
#    seen.add(line)
#    cleaned_lines.append(line)

#    return "\n".join(cleaned_lines)


# class DirectUsersUploadView(APIView):
#    """
#    Upload a document, process it, and save data directly to Users model.
#    """

#    def post(self, request, *args, **kwargs):
#    """Handle document upload and save directly to Users model."""
#    file = request.FILES.get("file")
#    if not file:
#    return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#    # Save file temporarily
#    file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#    processor = DocumentProcessor()
#    try:
#    result = processor.process_document(default_storage.path(file_path))

#    # Step 1: Clean extracted text
#    cleaned_text = clean_text(result.get("extracted_text", ""))

#    # Step 2: Convert text into structured JSON
#    structured_json = convert_text_to_json(cleaned_text)

#    # Step 3: Map and save directly to Users model
#    user_data = self.map_json_to_users(structured_json)
    
#    with transaction.atomic():
#    # Check if user already exists
#    existing_user = None
#    if user_data.get("email"):
#    existing_user = Users.objects.filter(email=user_data["email"]).first()
#    elif user_data.get("passport_number"):
#    existing_user = Users.objects.filter(passport_number=user_data["passport_number"]).first()
    
#    if existing_user:
#    # Update existing user
#    for key, value in user_data.items():
#    if hasattr(existing_user, key) and value not in ["", None]:
#    setattr(existing_user, key, value)
#    existing_user.save()
#    user = existing_user
#    created = False
#    else:
#    # Create new user
#    user = Users.objects.create(**user_data)
#    created = True

#    # Clean up file after processing
#    default_storage.delete(file_path)

#    return Response({
#    "message": f"User {'created' if created else 'updated'} successfully",
#    "user_id": user.id,
#    "created": created,
#    "file_name": file.name,
#    "structured_data": structured_json,
#    "page_count": result.get("page_count"),
#    "word_count": len(cleaned_text.split()),
#    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

#    except DocumentProcessingError as e:
#    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#    except Exception as e:
#    logger.error(f"Unexpected error in DirectUsersUploadView: {str(e)}")
#    return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#    def map_json_to_users(self, structured_json):
#    """
#    Map structured JSON data directly to Users model format.
#    """
#    try:
#    # Extract nested data safely
#    personal_details = structured_json.get("Personal_Details", {})
#    contact_details = structured_json.get("Contact_Details", {})
#    travel_documents = structured_json.get("Travel_Documents", {})
#    education = structured_json.get("Education", {})
#    professional_qualifications = structured_json.get("Professional_Qualifications", {})
#    next_of_kin = structured_json.get("Next_of_Kin_Emergency_Contact", {})
#    health_certs = structured_json.get("Health_Certificates_Vaccinations", {})
#    covid_vaccination = structured_json.get("Covid_19_Vaccination", {})
#    marine_courses = structured_json.get("Marine_Courses", {})
#    sea_service = structured_json.get("Sea_Service_Details", {})
#    references = structured_json.get("References", {})
    
#    # Map to Users model fields
#    user_data = {}
    
#    # Personal Information
#    if personal_details.get("first_name"):
#    user_data["first_name"] = personal_details["first_name"]
#    if personal_details.get("last_name"):
#    user_data["last_name"] = personal_details["last_name"]
#    if personal_details.get("middle_name"):
#    user_data["middle_name"] = personal_details["middle_name"]
#    if personal_details.get("date_of_birth"):
#    user_data["date_of_birth"] = self._parse_date(personal_details["date_of_birth"])
#    if personal_details.get("place_of_birth"):
#    user_data["place_of_birth"] = personal_details["place_of_birth"]
#    if personal_details.get("nationality"):
#    user_data["nationality"] = personal_details["nationality"]
#    if personal_details.get("gender"):
#    user_data["gender"] = self._normalize_gender(personal_details["gender"])
#    if personal_details.get("marital_status"):
#    user_data["marital_status"] = personal_details["marital_status"]
    
#    # Contact Information
#    if contact_details.get("email"):
#    user_data["email"] = contact_details["email"]
#    if contact_details.get("phone_number"):
#    user_data["phone_number"] = contact_details["phone_number"]
#    if contact_details.get("address"):
#    user_data["address"] = contact_details["address"]
#    if contact_details.get("city"):
#    user_data["city"] = contact_details["city"]
#    if contact_details.get("state"):
#    user_data["state"] = contact_details["state"]
#    if contact_details.get("country"):
#    user_data["country"] = contact_details["country"]
#    if contact_details.get("postal_code"):
#    user_data["postal_code"] = contact_details["postal_code"]
    
#    # Travel Documents
#    if travel_documents.get("passport_number"):
#    user_data["passport_number"] = travel_documents["passport_number"]
#    if travel_documents.get("passport_issue_date"):
#    user_data["passport_issue_date"] = self._parse_date(travel_documents["passport_issue_date"])
#    if travel_documents.get("passport_expiry_date"):
#    user_data["passport_expiry_date"] = self._parse_date(travel_documents["passport_expiry_date"])
#    if travel_documents.get("passport_issuing_country"):
#    user_data["passport_issuing_country"] = travel_documents["passport_issuing_country"]
#    if travel_documents.get("seaman_book_number"):
#    user_data["seaman_book_number"] = travel_documents["seaman_book_number"]
#    if travel_documents.get("seaman_book_issue_date"):
#    user_data["seaman_book_issue_date"] = self._parse_date(travel_documents["seaman_book_issue_date"])
#    if travel_documents.get("seaman_book_expiry_date"):
#    user_data["seaman_book_expiry_date"] = self._parse_date(travel_documents["seaman_book_expiry_date"])
    
#    # Education
#    if education.get("highest_level"):
#    user_data["education_level"] = education["highest_level"]
#    if education.get("institution"):
#    user_data["institution"] = education["institution"]
#    if education.get("graduation_year"):
#    user_data["graduation_year"] = self._parse_year(education["graduation_year"])
    
#    # Professional Information
#    if professional_qualifications.get("license_number"):
#    user_data["license_number"] = professional_qualifications["license_number"]
#    if professional_qualifications.get("license_type"):
#    user_data["license_type"] = professional_qualifications["license_type"]
#    if professional_qualifications.get("license_issue_date"):
#    user_data["license_issue_date"] = self._parse_date(professional_qualifications["license_issue_date"])
#    if professional_qualifications.get("license_expiry_date"):
#    user_data["license_expiry_date"] = self._parse_date(professional_qualifications["license_expiry_date"])
    
#    # Emergency Contact
#    if next_of_kin.get("name"):
#    user_data["emergency_contact_name"] = next_of_kin["name"]
#    if next_of_kin.get("relationship"):
#    user_data["emergency_contact_relationship"] = next_of_kin["relationship"]
#    if next_of_kin.get("phone"):
#    user_data["emergency_contact_phone"] = next_of_kin["phone"]
#    if next_of_kin.get("address"):
#    user_data["emergency_contact_address"] = next_of_kin["address"]
    
#    # Health Information
#    if health_certs.get("medical_certificate_number"):
#    user_data["medical_certificate_number"] = health_certs["medical_certificate_number"]
#    if health_certs.get("medical_certificate_issue_date"):
#    user_data["medical_certificate_issue_date"] = self._parse_date(health_certs["medical_certificate_issue_date"])
#    if health_certs.get("medical_certificate_expiry_date"):
#    user_data["medical_certificate_expiry_date"] = self._parse_date(health_certs["medical_certificate_expiry_date"])
#    if covid_vaccination.get("vaccinated") is not None:
#    user_data["covid_vaccination_status"] = self._normalize_boolean(covid_vaccination["vaccinated"])
#    if covid_vaccination.get("vaccination_date"):
#    user_data["covid_vaccination_date"] = self._parse_date(covid_vaccination["vaccination_date"])
    
#    # Experience
#    if sea_service.get("total_months"):
#    user_data["total_sea_service_months"] = self._parse_integer(sea_service["total_months"])
#    if sea_service.get("last_vessel_name"):
#    user_data["last_vessel_name"] = sea_service["last_vessel_name"]
#    if sea_service.get("last_vessel_type"):
#    user_data["last_vessel_type"] = sea_service["last_vessel_type"]
#    if sea_service.get("last_rank_held"):
#    user_data["last_rank_held"] = sea_service["last_rank_held"]
    
#    # Additional data as JSON (if Users model has a JSON field)
#    additional_data = {
#    "marine_courses": marine_courses,
#    "references": references,
#    "specialised_experience": structured_json.get("Specialised_Experience", {}),
#    "declaration": structured_json.get("Declaration", {}),
#    "office_use_only": structured_json.get("Office_Use_Only", {}),
#    }
    
#    # Only add additional_data if the field exists in Users model
#    if hasattr(Users, 'additional_data'):
#    user_data["additional_data"] = additional_data
    
#    return user_data
    
#    except Exception as e:
#    logger.error(f"Error mapping JSON to Users format: {str(e)}")
#    raise ValueError(f"Data mapping failed: {str(e)}")
    
#    def _parse_date(self, date_string):
#    """Parse date string to proper format."""
#    if not date_string or date_string == "":
#    return None
#    return str(date_string)
    
#    def _parse_year(self, year_string):
#    """Parse year string to integer."""
#    if not year_string:
#    return None
#    try:
#    return int(str(year_string))
#    except (ValueError, TypeError):
#    return None
    
#    def _parse_integer(self, value):
#    """Parse value to integer."""
#    try:
#    return int(value) if value else 0
#    except (ValueError, TypeError):
#    return 0
    
#    def _normalize_gender(self, gender):
#    """Normalize gender values."""
#    if not gender:
#    return ""
#    gender_lower = gender.lower()
#    if gender_lower in ["male", "m"]:
#    return "Male"
#    elif gender_lower in ["female", "f"]:
#    return "Female"
#    return gender
    
#    def _normalize_boolean(self, value):
#    """Normalize boolean values."""
#    if isinstance(value, bool):
#    return value
#    if isinstance(value, str):
#    return value.lower() in ["true", "yes", "1", "y"]
#    return bool(value)

















# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json
# from .models import Applicant
# from .serializers import ApplicantToUsersSerializer
# from api.models import Users
# import logging
# from django.db import transaction

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#     """
#     Clean extracted text:
#     - Remove duplicate lines
#     - Remove repeated inline values (tables)
#     - Strip common headers/footers (boilerplate repeated across pages)
#     """
#     lines = [line.strip() for line in text.splitlines() if line.strip()]

#     # Count line frequency
#     freq = Counter(lines)

#     # If a line appears on >= 5 pages, treat as boilerplate
#     boilerplate = {line for line, count in freq.items() if count >= 5}

#     cleaned_lines = []
#     seen = set()
#     for line in lines:
#         if line in boilerplate:
#             continue  # skip repeating headers/footers

#         # Collapse table duplicates (split by | or big spaces)
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|")]
#             unique_parts = []
#             for p in parts:
#                 if not unique_parts or p != unique_parts[-1]:
#                     unique_parts.append(p)
#             line = " | ".join(unique_parts)

#         # Collapse repeated words like "Confidential Confidential Confidential"
#         line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#         # Avoid full-line duplicates
#         if line not in seen:
#             seen.add(line)
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines)


# class DirectUsersUploadView(APIView):
#     """
#     Upload a document, process it, and save data directly to Users model.
#     """

#     def post(self, request, *args, **kwargs):
#         """Handle document upload and save directly to Users model."""
#         file = request.FILES.get("file")
#         if not file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         # Save file temporarily
#         file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#         processor = DocumentProcessor()
#         try:
#             result = processor.process_document(default_storage.path(file_path))

#             # Step 1: Clean extracted text
#             cleaned_text = clean_text(result.get("extracted_text", ""))

#             # Step 2: Convert text into structured JSON
#             structured_json = convert_text_to_json(cleaned_text)

#             # Step 3: Map and save directly to Users model
#             user_data = self.map_json_to_users(structured_json)

#             with transaction.atomic():
#                 # Check if user already exists
#                 existing_user = None
#                 if user_data.get("email"):
#                     existing_user = Users.objects.filter(email=user_data["email"]).first()
#                 elif user_data.get("passport_no"):
#                     existing_user = Users.objects.filter(passport_no=user_data["passport_no"]).first()

#                 if existing_user:
#                     # Update existing user
#                     for key, value in user_data.items():
#                         if hasattr(existing_user, key) and value not in ["", None]:
#                             setattr(existing_user, key, value)
#                     existing_user.save()
#                     user = existing_user
#                     created = False
#                 else:
#                     # Create new user
#                     user = Users.objects.create(**user_data)
#                     created = True

#             # Clean up file after processing
#             default_storage.delete(file_path)

#             return Response({
#                 "message": f"User {'created' if created else 'updated'} successfully",
#                 "user_id": user.id,
#                 "created": created,
#                 "file_name": file.name,
#                 "structured_data": structured_json,
#                 "page_count": result.get("page_count"),
#                 "word_count": len(cleaned_text.split()),
#             }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

#         except DocumentProcessingError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             logger.error(f"Unexpected error in DirectUsersUploadView: {str(e)}")
#             return Response({"error": f"An unexpected error occurred: {str(e)}"},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def map_json_to_users(self, structured_json):
#         """
#         Map structured JSON data directly to Users model format using correct field names.
#         """
#         try:
#             # Extract nested data safely
#             personal_details = structured_json.get("Personal_Details", {})
#             contact_details = structured_json.get("Contact_Details", {})
#             travel_documents = structured_json.get("Travel_Documents", {})
#             education = structured_json.get("Education", {})
#             professional_qualifications = structured_json.get("Professional_Qualifications", {})
#             next_of_kin = structured_json.get("Next_of_Kin_Emergency_Contact", {})
#             health_certs = structured_json.get("Health_Certificates_Vaccinations", {})
#             covid_vaccination = structured_json.get("Covid_19_Vaccination", {})
#             marine_courses = structured_json.get("Marine_Courses", {})
#             sea_service = structured_json.get("Sea_Service_Details", {})
#             references = structured_json.get("References", {})

#             user_data = {}

#             # Personal Information
#             if personal_details.get("first_name"):
#                 user_data["first_name"] = personal_details["first_name"]
#             if personal_details.get("last_name"):
#                 if user_data.get("first_name"):
#                     user_data["first_name"] = f"{user_data['first_name']} {personal_details['last_name']}"
#                 else:
#                     user_data["first_name"] = personal_details["last_name"]
#             if personal_details.get("middle_name"):
#                 user_data["middle_name"] = personal_details["middle_name"]
#             if personal_details.get("date_of_birth"):
#                 user_data["date_of_birth"] = self._parse_date(personal_details["date_of_birth"])
#             if personal_details.get("place_of_birth"):
#                 user_data["Place_Of_Birth"] = personal_details["place_of_birth"]
#             if personal_details.get("nationality"):
#                 user_data["nationality"] = personal_details["nationality"]
#             if personal_details.get("marital_status"):
#                 user_data["marital_status"] = personal_details["marital_status"]

#             # Contact Information
#             if contact_details.get("email"):
#                 user_data["email"] = contact_details["email"]
#             if contact_details.get("phone_number"):
#                 user_data["phone_number"] = contact_details["phone_number"]
#             if contact_details.get("address"):
#                 user_data["address"] = contact_details["address"]

#             # Travel Documents
#             if travel_documents.get("passport_number"):
#                 user_data["passport_no"] = travel_documents["passport_number"]
#             if travel_documents.get("passport_issue_date"):
#                 user_data["passport_issue_date"] = self._parse_date(travel_documents["passport_issue_date"])
#             if travel_documents.get("passport_expiry_date"):
#                 user_data["passport_expiry_date"] = self._parse_date(travel_documents["passport_expiry_date"])
#             if travel_documents.get("passport_issuing_country"):
#                 user_data["passport_issued_by"] = travel_documents["passport_issuing_country"]
#             if travel_documents.get("seaman_book_number"):
#                 user_data["seaman_book_no"] = travel_documents["seaman_book_number"]
#             if travel_documents.get("seaman_book_issue_date"):
#                 user_data["seaman_book_issue_date"] = self._parse_date(travel_documents["seaman_book_issue_date"])
#             if travel_documents.get("seaman_book_expiry_date"):
#                 user_data["seaman_book_expiry_date"] = self._parse_date(travel_documents["seaman_book_expiry_date"])

#             # Education
#             if education.get("institution"):
#                 user_data["college_or_school"] = education["institution"]

#             # Professional Info
#             if professional_qualifications.get("license_number"):
#                 user_data["coc_certificate_number"] = professional_qualifications["license_number"]
#             if professional_qualifications.get("license_type"):
#                 user_data["coc_certificate_name"] = professional_qualifications["license_type"]
#             if professional_qualifications.get("license_issue_date"):
#                 user_data["coc_issue_date"] = self._parse_date(professional_qualifications["license_issue_date"])
#             if professional_qualifications.get("license_expiry_date"):
#                 user_data["coc_expiry_date"] = self._parse_date(professional_qualifications["license_expiry_date"])

#             # Emergency Contact
#             if next_of_kin.get("name"):
#                 user_data["next_of_kin_full_name"] = next_of_kin["name"]
#             if next_of_kin.get("relationship"):
#                 user_data["next_of_kin_relationship"] = next_of_kin["relationship"]
#             if next_of_kin.get("phone"):
#                 user_data["next_of_kin_phone"] = next_of_kin["phone"]
#             if next_of_kin.get("address"):
#                 user_data["next_of_kin_address_country"] = next_of_kin["address"]
#             if next_of_kin.get("email"):
#                 user_data["next_of_kin_email"] = next_of_kin["email"]

#             # Health Information
#             if health_certs.get("medical_certificate_number"):
#                 user_data["health_number"] = health_certs["medical_certificate_number"]
#             if health_certs.get("medical_certificate_issue_date"):
#                 user_data["health_issue_date"] = self._parse_date(health_certs["medical_certificate_issue_date"])
#             if health_certs.get("medical_certificate_expiry_date"):
#                 user_data["health_expiry_date"] = self._parse_date(health_certs["medical_certificate_expiry_date"])

#             # COVID-19 Vaccination
#             if covid_vaccination.get("vaccine_name"):
#                 user_data["covid_vaccine_name"] = covid_vaccination["vaccine_name"]
#             if covid_vaccination.get("first_dose_date"):
#                 user_data["covid_first_dose"] = self._parse_date(covid_vaccination["first_dose_date"])
#             if covid_vaccination.get("second_dose_date"):
#                 user_data["covid_second_dose"] = self._parse_date(covid_vaccination["second_dose_date"])

#             # Default password
#             if not user_data.get("password"):
#                 user_data["password"] = "defaultpassword123"

#             return user_data

#         except Exception as e:
#             logger.error(f"Error mapping JSON to Users format: {str(e)}")
#             raise ValueError(f"Data mapping failed: {str(e)}")

#     def _parse_date(self, date_string):
#         """Parse date string to proper format."""
#         if not date_string or date_string == "":
#             return None
#         return str(date_string)

#     def _parse_year(self, year_string):
#         """Parse year string to integer."""
#         if not year_string:
#             return None
#         try:
#             return int(str(year_string))
#         except (ValueError, TypeError):
#             return None

#     def _parse_integer(self, value):
#         """Parse value to integer."""
#         try:
#             return int(value) if value else 0
#         except (ValueError, TypeError):
#             return 0

#     def _normalize_gender(self, gender):
#         """Normalize gender values."""
#         if not gender:
#             return ""
#         gender_lower = gender.lower()
#         if gender_lower in ["male", "m"]:
#             return "Male"
#         elif gender_lower in ["female", "f"]:
#             return "Female"
#         return gender

#     def _normalize_boolean(self, value):
#         """Normalize boolean values."""
#         if isinstance(value, bool):
#             return value
#         if isinstance(value, str):
#             return value.lower() in ["true", "yes", "1", "y"]
#         return bool(value)


# class ApplicantListAPIView(APIView):
#     """
#     List all applicants in API app format using ApplicantToUsersSerializer.
#     """

#     def get(self, request, *args, **kwargs):
#         try:
#             applicants = Applicant.objects.all().order_by('-created_at')
#             serializer = ApplicantToUsersSerializer(applicants, many=True)

#             return Response({
#                 "success": True,
#                 "count": len(serializer.data),
#                 "users": serializer.data
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error listing applicants in API format: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicants",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantDetailAPIView(APIView):
#     """
#     Get detailed information about a specific applicant in API app format.
#     """

#     def get(self, request, applicant_id, *args, **kwargs):
#         try:
#             applicant = Applicant.objects.get(id=applicant_id)
#             serializer = ApplicantToUsersSerializer(applicant)

#             return Response({
#                 "success": True,
#                 "user": serializer.data
#             }, status=status.HTTP_200_OK)

#         except Applicant.DoesNotExist:
#             return Response({
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             logger.error(f"Error retrieving applicant {applicant_id} in API format: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicant",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)































#ai_document/views.py

# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json
# from .models import Applicant
# from .data_mapper_service import DataMapperService
# from api.models import Users
# import logging
# from django.db import transaction

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#     """
#     Clean extracted text:
#     - Remove duplicate lines
#     - Remove repeated inline values (tables)
#     - Strip common headers/footers (boilerplate repeated across pages)
#     """
#     lines = [line.strip() for line in text.splitlines() if line.strip()]

#     # Count line frequency
#     freq = Counter(lines)

#     # If a line appears on >= 5 pages, treat as boilerplate
#     boilerplate = {line for line, count in freq.items() if count >= 5}

#     cleaned_lines = []
#     seen = set()
#     for line in lines:
#         if line in boilerplate:
#             continue  # skip repeating headers/footers

#         # Collapse table duplicates (split by | or big spaces)
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|")]
#             unique_parts = []
#             for p in parts:
#                 if not unique_parts or p != unique_parts[-1]:
#                     unique_parts.append(p)
#             line = " | ".join(unique_parts)

#         # Collapse repeated words like "Confidential Confidential Confidential"
#         line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#         # Avoid full-line duplicates
#         if line not in seen:
#             seen.add(line)
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines)


# class DocumentUploadView(APIView):
#     """
#     Upload a document (PDF or DOCX), extract text, convert to structured JSON,
#     save into both Applicant table and Users table, and return the response.
#     """

#     def post(self, request, *args, **kwargs):
#         """Handle document upload and save to both models."""
#         file = request.FILES.get("file")
#         if not file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         # Save file temporarily
#         file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#         processor = DocumentProcessor()
#         try:
#             with transaction.atomic():
#                 # Step 1: Extract text from document
#                 result = processor.process_document(default_storage.path(file_path))

#                 # Step 2: Clean extracted text
#                 cleaned_text = clean_text(result.get("extracted_text", ""))

#                 # Step 3: Convert text into structured JSON using LangChain + Ollama
#                 structured_json = convert_text_to_json(cleaned_text)
                
#                 # Ensure structured_json is a dictionary
#                 if not isinstance(structured_json, dict):
#                     logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
#                     structured_json = {
#                         "Personal_Details": {},
#                         "Education": {},
#                         "Contact_Details": {},
#                         "Travel_Documents": {},
#                         "Professional_Qualifications": {},
#                         "Next_of_Kin_Emergency_Contact": {},
#                         "Health_Certificates_Vaccinations": {},
#                         "Covid_19_Vaccination": {},
#                         "Marine_Courses": {},
#                         "Sea_Service_Details": {},
#                         "Specialised_Experience": {},
#                         "References": {},
#                         "Declaration": {},
#                         "Office_Use_Only": {},
#                         "error": f"Unexpected return type: {type(structured_json)}"
#                     }

#                 # Step 4: Save structured data into Applicant model
#                 applicant = Applicant.objects.create(
#                     personal_details=structured_json.get("Personal_Details", {}),
#                     education=structured_json.get("Education", {}),
#                     contact_details=structured_json.get("Contact_Details", {}),
#                     travel_documents=structured_json.get("Travel_Documents", {}),
#                     professional_qualifications=structured_json.get("Professional_Qualifications", {}),
#                     next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#                     health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
#                     covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
#                     marine_courses=structured_json.get("Marine_Courses", {}),
#                     sea_service_details=structured_json.get("Sea_Service_Details", {}),
#                     specialised_experience=structured_json.get("Specialised_Experience", {}),
#                     references=structured_json.get("References", {}),
#                     declaration=structured_json.get("Declaration", {}),
#                     office_use_only=structured_json.get("Office_Use_Only", {}),
#                 )
                
#                 logger.info(f"Successfully created applicant with ID: {applicant.id}")

#                 # Step 5: Convert and save to api.Users model using DataMapperService
#                 user = None
#                 user_error = None
#                 try:
#                     logger.info("Converting applicant to Users model")
#                     user = DataMapperService.save_applicant_as_user(applicant)
#                     logger.info(f"Successfully created/updated user: {user.email} (ID: {user.id})")
#                 except Exception as ue:
#                     user_error = f"User creation error: {str(ue)}"
#                     logger.error(f"Failed to create user: {ue}")

#                 # Clean up file after processing
#                 try:
#                     default_storage.delete(file_path)
#                 except Exception as e:
#                     logger.warning(f"Failed to delete temporary file: {e}")

#                 # Determine response status based on parsing quality
#                 response_status = status.HTTP_201_CREATED
#                 message = "Data saved successfully to both databases"
                
#                 if "error" in structured_json:
#                     response_status = status.HTTP_206_PARTIAL_CONTENT
#                     message = "Data saved with parsing issues"
                
#                 if not user:
#                     response_status = status.HTTP_206_PARTIAL_CONTENT
#                     message = "Data saved to Applicant database, but failed to save to Users database"

#                 return Response({
#                     "message": message,
#                     "applicant_id": applicant.id,
#                     "user_id": user.id if user else None,
#                     "user_email": user.email if user else None,
#                     "file_name": file.name,
#                     "structured_data": structured_json,
#                     "page_count": result.get("page_count"),
#                     "word_count": len(cleaned_text.split()),
#                     "parsing_quality": "low" if "error" in structured_json else "high",
#                     "user_creation_status": "success" if user else "failed",
#                     "user_error": user_error,
#                 }, status=response_status)

#         except DocumentProcessingError as e:
#             # Clean up file on error
#             try:
#                 default_storage.delete(file_path)
#             except:
#                 pass
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:
#             # Clean up file on error
#             try:
#                 default_storage.delete(file_path)
#             except:
#                 pass
#             logger.error(f"Unexpected error: {e}")
#             return Response({
#                 "error": "Internal server error",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantListView(APIView):
#     """
#     List all applicants.
#     """
    
#     def get(self, request, *args, **kwargs):
#         try:
#             applicants = Applicant.objects.all().order_by('-created_at')
        
#             applicant_list = []
#             for applicant in applicants:
#                 applicant_data = {
#                     "id": applicant.id,
#                     "name": applicant.personal_details.get("name", "Unknown") if applicant.personal_details else "Unknown",
#                     "email": applicant.contact_details.get("email", "") if applicant.contact_details else "",
#                     "nationality": applicant.personal_details.get("nationality", "") if applicant.personal_details else "",
#                     "created_at": applicant.created_at.isoformat(),
#                 }
#                 applicant_list.append(applicant_data)
        
#             return Response({
#                 "success": True,
#                 "count": len(applicant_list),
#                 "applicants": applicant_list
#             }, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             logger.error(f"Error listing applicants: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicants",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantDetailView(APIView):
#     """
#     Get detailed information about a specific applicant.
#     """
    
#     def get(self, request, applicant_id, *args, **kwargs):
#         try:
#             applicant = Applicant.objects.get(id=applicant_id)
        
#             return Response({
#                 "success": True,
#                 "applicant": {
#                     "id": applicant.id,
#                     "personal_details": applicant.personal_details,
#                     "education": applicant.education,
#                     "contact_details": applicant.contact_details,
#                     "travel_documents": applicant.travel_documents,
#                     "professional_qualifications": applicant.professional_qualifications,
#                     "next_of_kin_emergency_contact": applicant.next_of_kin_emergency_contact,
#                     "health_certificates_vaccinations": applicant.health_certificates_vaccinations,
#                     "covid_19_vaccination": applicant.covid_19_vaccination,
#                     "marine_courses": applicant.marine_courses,
#                     "sea_service_details": applicant.sea_service_details,
#                     "specialised_experience": applicant.specialised_experience,
#                     "references": applicant.references,
#                     "declaration": applicant.declaration,
#                     "office_use_only": applicant.office_use_only,
#                     "created_at": applicant.created_at.isoformat(),
#                     "updated_at": applicant.updated_at.isoformat(),
#                 }
#             }, status=status.HTTP_200_OK)
        
#         except Applicant.DoesNotExist:
#             return Response({
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         except Exception as e:
#             logger.error(f"Error retrieving applicant {applicant_id}: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicant",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ConvertApplicantToUserView(APIView):
#     """
#     Convert an existing Applicant to a Users instance.
#     Useful for batch processing or re-processing existing data.
#     """
    
#     def post(self, request, *args, **kwargs):
#         """
#         Convert an applicant to a user.
        
#         Expected payload:
#         {
#             "applicant_id": 123
#         }
#         """
#         applicant_id = request.data.get('applicant_id')
        
#         if not applicant_id:
#             return Response({
#                 "success": False,
#                 "error": "applicant_id is required"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             applicant = Applicant.objects.get(id=applicant_id)
#         except Applicant.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             with transaction.atomic():
#                 user = DataMapperService.save_applicant_as_user(applicant)
        
#             return Response({
#                 "success": True,
#                 "message": "Applicant converted to user successfully",
#                 "data": {
#                     "applicant_id": applicant.id,
#                     "user_id": user.id,
#                     "user_email": user.email,
#                     "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
#                 }
#             }, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#             return Response({
#                 "success": False,
#                 "error": "Failed to convert applicant to user",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class BatchConvertApplicantsView(APIView):
#     """
#     Convert multiple applicants to users in batch.
#     """
    
#     def post(self, request, *args, **kwargs):
#         """
#         Convert multiple applicants to users.
        
#         Expected payload:
#         {
#             "applicant_ids": [1, 2, 3, 4, 5]
#         }
#         or
#         {
#             "convert_all": true  // Convert all applicants
#         }
#         """
#         applicant_ids = request.data.get('applicant_ids', [])
#         convert_all = request.data.get('convert_all', False)
        
#         if convert_all:
#             applicants = Applicant.objects.all()
#         elif applicant_ids:
#             applicants = Applicant.objects.filter(id__in=applicant_ids)
#         else:
#             return Response({
#                 "success": False,
#                 "error": "Either applicant_ids or convert_all=true is required"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         results = {
#             "total_applicants": applicants.count(),
#             "successful_conversions": 0,
#             "failed_conversions": 0,
#             "errors": []
#         }
        
#         for applicant in applicants:
#             try:
#                 with transaction.atomic():
#                     user = DataMapperService.save_applicant_as_user(applicant)
#                     results["successful_conversions"] += 1
#                     logger.info(f"Successfully converted applicant {applicant.id} to user {user.id}")
            
#             except Exception as e:
#                 results["failed_conversions"] += 1
#                 error_msg = f"Applicant {applicant.id}: {str(e)}"
#                 results["errors"].append(error_msg)
#                 logger.error(f"Failed to convert applicant {applicant.id}: {e}")
        
#         return Response({
#             "success": True,
#             "message": f"Batch conversion completed. {results['successful_conversions']} successful, {results['failed_conversions']} failed.",
#             "data": results
#         }, status=status.HTTP_200_OK)


# class SyncStatusView(APIView):
#     """
#     Check sync status between Applicant and Users models.
#     """
    
#     def get(self, request, *args, **kwargs):
#         """
#         Get sync status between the two databases.
#         """
#         try:
#             total_applicants = Applicant.objects.count()
#             total_users = Users.objects.count()
        
#             # Find applicants without corresponding users (by email)
#             applicant_emails = set()
#             for applicant in Applicant.objects.all():
#                 personal_details = applicant.personal_details or {}
#                 contact_details = applicant.contact_details or {}
#                 email = personal_details.get('email') or contact_details.get('email')
#                 if email:
#                     applicant_emails.add(email.lower())
        
#             user_emails = set(Users.objects.values_list('email', flat=True))
#             user_emails = {email.lower() for email in user_emails if email}
        
#             unsynced_emails = applicant_emails - user_emails
        
#             return Response({
#                 "success": True,
#                 "data": {
#                     "total_applicants": total_applicants,
#                     "total_users": total_users,
#                     "applicants_with_email": len(applicant_emails),
#                     "users_with_email": len(user_emails),
#                     "unsynced_applicants": len(unsynced_emails),
#                     "unsynced_emails": list(unsynced_emails)[:10],  # Show first 10
#                     "sync_percentage": round((len(user_emails) / len(applicant_emails)) * 100, 2) if applicant_emails else 0
#                 }
#             }, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             logger.error(f"Error getting sync status: {e}")
#             return Response({
#                 "success": False,
#                 "error": "Failed to get sync status",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


















#ai_document/views.py

# import re 
# from collections import Counter 
# from rest_framework.views import APIView 
# from rest_framework.response import Response 
# from rest_framework import status 
# from django.core.files.storage import default_storage 
# from django.core.files.base import ContentFile 
# from .document_processor import DocumentProcessor, DocumentProcessingError 
# from .document_to_json import convert_text_to_json 
# from .models import Applicant 
# from .data_mapper_service import DataMapperService 
# from api.models import Users 
# import logging 
# from django.db import transaction




# # import re
# # from collections import Counter
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from django.core.files.storage import default_storage
# # from django.core.files.base import ContentFile
# # from .document_processor import DocumentProcessor, DocumentProcessingError
# # from .document_to_json import convert_text_to_json
# # from .models import Applicant
# # from .data_mapper_service import DataMapperService
# # from api.models import Users
# # import logging
# # from django.db import transaction

# logger = logging.getLogger(__name__)

# import re
# from collections import Counter

# def clean_text(text: str) -> str:
#     """
#     Clean extracted text:
#     - Remove duplicate lines
#     - Remove repeated inline values (tables)
#     - Strip common headers/footers (boilerplate repeated across pages)
#     """
#     lines = [line.strip() for line in text.splitlines() if line.strip()]

#     # Count line frequency
#     freq = Counter(lines)

#     # If a line appears on >= 5 pages, treat as boilerplate
#     boilerplate = {line for line, count in freq.items() if count >= 5}

#     cleaned_lines = []
#     seen = set()

#     for line in lines:
#         if line in boilerplate:
#             continue  # Skip repeating headers/footers

#         # Collapse table duplicates (split by | or big spaces)
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|")]
#             unique_parts = []
#             for p in parts:
#                 if not unique_parts or p != unique_parts[-1]:
#                     unique_parts.append(p)
#             line = " | ".join(unique_parts)

#         # Collapse repeated words like "Confidential Confidential Confidential"
#         line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#         # Avoid full-line duplicates
#         if line not in seen:
#             seen.add(line)
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines)




# class DocumentUploadView(APIView): """ Upload a document (PDF or DOCX), extract text, convert to structured JSON, save into both Applicant table and Users table, and return the response. """

# def post(self, request, *args, **kwargs):
#     """Handle document upload and save to both models."""
#     file = request.FILES.get("file")
#     if not file:
#         return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#     # Save file temporarily
#     file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#     processor = DocumentProcessor()
#     try:
#         with transaction.atomic():
#             # Step 1: Extract text from document
#             result = processor.process_document(default_storage.path(file_path))

#             # Step 2: Clean extracted text
#             cleaned_text = clean_text(result.get("extracted_text", ""))

#             # Step 3: Convert text into structured JSON using LangChain + Ollama
#             structured_json = convert_text_to_json(cleaned_text)
            
#             # Ensure structured_json is a dictionary
#             if not isinstance(structured_json, dict):
#                 logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
#                 structured_json = {
#                     "Personal_Details": {},
#                     "Education": {},
#                     "Contact_Details": {},
#                     "Travel_Documents": {},
#                     "Professional_Qualifications": {},
#                     "Next_of_Kin_Emergency_Contact": {},
#                     "Health_Certificates_Vaccinations": {},
#                     "Covid_19_Vaccination": {},
#                     "Marine_Courses": {},
#                     "Sea_Service_Details": {},
#                     "Specialised_Experience": {},
#                     "References": {},
#                     "Declaration": {},
#                     "Office_Use_Only": {},
#                     "Physical_Measurements": {},
#                     "Language_Skills": {},
#                     "Medical_History": {},
#                     "Assessments": {},
#                     "Competency_Tests": {},
#                     "error": f"Unexpected return type: {type(structured_json)}"
#                 }

#             # Step 4: Save structured data into Applicant model
#             applicant = Applicant.objects.create(
#                 personal_details=structured_json.get("Personal_Details", {}),
#                 education=structured_json.get("Education", {}),
#                 contact_details=structured_json.get("Contact_Details", {}),
#                 travel_documents=structured_json.get("Travel_Documents", {}),
#                 professional_qualifications=structured_json.get("Professional_Qualifications", {}),
#                 next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#                 health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
#                 covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
#                 marine_courses=structured_json.get("Marine_Courses", {}),
#                 sea_service_details=structured_json.get("Sea_Service_Details", {}),
#                 specialised_experience=structured_json.get("Specialised_Experience", {}),
#                 references=structured_json.get("References", {}),
#                 declaration=structured_json.get("Declaration", {}),
#                 office_use_only=structured_json.get("Office_Use_Only", {}),
#                 physical_measurements=structured_json.get("Physical_Measurements", {}),
#                 language_skills=structured_json.get("Language_Skills", {}),
#                 medical_history=structured_json.get("Medical_History", {}),
#                 assessments=structured_json.get("Assessments", {}),
#                 competency_tests=structured_json.get("Competency_Tests", {}),
#             )
            
#             logger.info(f"Successfully created applicant with ID: {applicant.id}")

#             # Step 5: Convert and save to api.Users model using DataMapperService
#             user = None
#             user_error = None
#             try:
#                 logger.info("Converting applicant to Users model")
#                 user = DataMapperService.save_applicant_as_user(applicant)
#                 logger.info(f"Successfully created/updated user: {user.email} (ID: {user.id})")
#             except Exception as ue:
#                 user_error = f"User creation error: {str(ue)}"
#                 logger.error(f"Failed to create user: {ue}")

#             # Clean up file after processing
#             try:
#                 default_storage.delete(file_path)
#             except Exception as e:
#                 logger.warning(f"Failed to delete temporary file: {e}")

#             # Determine response status based on parsing quality
#             response_status = status.HTTP_201_CREATED
#             message = "Data saved successfully to both databases"
            
#             if "error" in structured_json:
#                 response_status = status.HTTP_206_PARTIAL_CONTENT
#                 message = "Data saved with parsing issues"
            
#             if not user:
#                 response_status = status.HTTP_206_PARTIAL_CONTENT
#                 message = "Data saved to Applicant database, but failed to save to Users database"

#             return Response({
#                 "message": message,
#                 "applicant_id": applicant.id,
#                 "user_id": user.id if user else None,
#                 "user_email": user.email if user else None,
#                 "file_name": file.name,
#                 "structured_data": structured_json,
#                 "page_count": result.get("page_count"),
#                 "word_count": len(cleaned_text.split()),
#                 "parsing_quality": "low" if "error" in structured_json else "high",
#                 "user_creation_status": "success" if user else "failed",
#                 "user_error": user_error,
#             }, status=response_status)

#     except DocumentProcessingError as e:
#         # Clean up file on error
#         try:
#             default_storage.delete(file_path)
#         except:
#             pass
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#     except Exception as e:
#         # Clean up file on error
#         try:
#             default_storage.delete(file_path)
#         except:
#             pass
#         logger.error(f"Unexpected error: {e}")
#         return Response({
#             "error": "Internal server error",
#             "details": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantListView(APIView): """ List all applicants. """

# def get(self, request, *args, **kwargs):
#     try:
#         applicants = Applicant.objects.all().order_by('-created_at')
    
#         applicant_list = []
#         for applicant in applicants:
#             applicant_data = {
#                 "id": applicant.id,
#                 "name": applicant.personal_details.get("name", "Unknown") if applicant.personal_details else "Unknown",
#                 "email": applicant.contact_details.get("email", "") if applicant.contact_details else "",
#                 "nationality": applicant.personal_details.get("nationality", "") if applicant.personal_details else "",
#                 "created_at": applicant.created_at.isoformat(),
#             }
#             applicant_list.append(applicant_data)
    
#         return Response({
#             "success": True,
#             "count": len(applicant_list),
#             "applicants": applicant_list
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error(f"Error listing applicants: {e}")
#         return Response({
#             "error": "Failed to retrieve applicants",
#             "details": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantDetailView(APIView): """ Get detailed information about a specific applicant. """

# def get(self, request, applicant_id, *args, **kwargs):
#     try:
#         applicant = Applicant.objects.get(id=applicant_id)
    
#         return Response({
#             "success": True,
#             "applicant": {
#                 "id": applicant.id,
#                 "personal_details": applicant.personal_details,
#                 "education": applicant.education,
#                 "contact_details": applicant.contact_details,
#                 "travel_documents": applicant.travel_documents,
#                 "professional_qualifications": applicant.professional_qualifications,
#                 "next_of_kin_emergency_contact": applicant.next_of_kin_emergency_contact,
#                 "health_certificates_vaccinations": applicant.health_certificates_vaccinations,
#                 "covid_19_vaccination": applicant.covid_19_vaccination,
#                 "marine_courses": applicant.marine_courses,
#                 "sea_service_details": applicant.sea_service_details,
#                 "specialised_experience": applicant.specialised_experience,
#                 "references": applicant.references,
#                 "declaration": applicant.declaration,
#                 "office_use_only": applicant.office_use_only,
#                 "created_at": applicant.created_at.isoformat(),
#                 "updated_at": applicant.updated_at.isoformat(),
#             }
#         }, status=status.HTTP_200_OK)
    
#     except Applicant.DoesNotExist:
#         return Response({
#             "error": f"Applicant with ID {applicant_id} not found"
#         }, status=status.HTTP_404_NOT_FOUND)
    
#     except Exception as e:
#         logger.error(f"Error retrieving applicant {applicant_id}: {e}")
#         return Response({
#             "error": "Failed to retrieve applicant",
#             "details": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ConvertApplicantToUserView(APIView): """ Convert an existing Applicant to a Users instance. Useful for batch processing or re-processing existing data. """

# def post(self, request, *args, **kwargs):
#     """
#     Convert an applicant to a user.
    
#     Expected payload:
#     {
#         "applicant_id": 123
#     }
#     """
#     applicant_id = request.data.get('applicant_id')
    
#     if not applicant_id:
#         return Response({
#             "success": False,
#             "error": "applicant_id is required"
#         }, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         applicant = Applicant.objects.get(id=applicant_id)
#     except Applicant.DoesNotExist:
#         return Response({
#             "success": False,
#             "error": f"Applicant with ID {applicant_id} not found"
#         }, status=status.HTTP_404_NOT_FOUND)
    
#     try:
#         with transaction.atomic():
#             user = DataMapperService.save_applicant_as_user(applicant)
    
#         return Response({
#             "success": True,
#             "message": "Applicant converted to user successfully",
#             "data": {
#                 "applicant_id": applicant.id,
#                 "user_id": user.id,
#                 "user_email": user.email,
#                 "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
#             }
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#         return Response({
#             "success": False,
#             "error": "Failed to convert applicant to user",
#             "details": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class BatchConvertApplicantsView(APIView): """ Convert multiple applicants to users in batch. """

# def post(self, request, *args, **kwargs):
#     """
#     Convert multiple applicants to users.
    
#     Expected payload:
#     {
#         "applicant_ids": [1, 2, 3, 4, 5]
#     }
#     or
#     {
#         "convert_all": true  // Convert all applicants
#     }
#     """
#     applicant_ids = request.data.get('applicant_ids', [])
#     convert_all = request.data.get('convert_all', False)
    
#     if convert_all:
#         applicants = Applicant.objects.all()
#     elif applicant_ids:
#         applicants = Applicant.objects.filter(id__in=applicant_ids)
#     else:
#         return Response({
#             "success": False,
#             "error": "Either applicant_ids or convert_all=true is required"
#         }, status=status.HTTP_400_BAD_REQUEST)
    
#     results = {
#         "total_applicants": applicants.count(),
#         "successful_conversions": 0,
#         "failed_conversions": 0,
#         "errors": []
#     }
    
#     for applicant in applicants:
#         try:
#             with transaction.atomic():
#                 user = DataMapperService.save_applicant_as_user(applicant)
#                 results["successful_conversions"] += 1
#                 logger.info(f"Successfully converted applicant {applicant.id} to user {user.id}")
        
#         except Exception as e:
#             results["failed_conversions"] += 1
#             error_msg = f"Applicant {applicant.id}: {str(e)}"
#             results["errors"].append(error_msg)
#             logger.error(f"Failed to convert applicant {applicant.id}: {e}")
    
#     return Response({
#         "success": True,
#         "message": f"Batch conversion completed. {results['successful_conversions']} successful, {results['failed_conversions']} failed.",
#         "data": results
#     }, status=status.HTTP_200_OK)


# class SyncStatusView(APIView): """ Check sync status between Applicant and Users models. """

# def get(self, request, *args, **kwargs):
#     """
#     Get sync status between the two databases.
#     """
#     try:
#         total_applicants = Applicant.objects.count()
#         total_users = Users.objects.count()
    
#         # Find applicants without corresponding users (by email)
#         applicant_emails = set()
#         for applicant in Applicant.objects.all():
#             personal_details = applicant.personal_details or {}
#             contact_details = applicant.contact_details or {}
#             email = personal_details.get('email') or contact_details.get('email')
#             if email:
#                 applicant_emails.add(email.lower())
    
#         user_emails = set(Users.objects.values_list('email', flat=True))
#         user_emails = {email.lower() for email in user_emails if email}
    
#         unsynced_emails = applicant_emails - user_emails
    
#         return Response({
#             "success": True,
#             "data": {
#                 "total_applicants": total_applicants,
#                 "total_users": total_users,
#                 "applicants_with_email": len(applicant_emails),
#                 "users_with_email": len(user_emails),
#                 "unsynced_applicants": len(unsynced_emails),
#                 "unsynced_emails": list(unsynced_emails)[:10],  # Show first 10
#                 "sync_percentage": round((len(user_emails) / len(applicant_emails)) * 100, 2) if applicant_emails else 0
#             }
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error(f"Error getting sync status: {e}")
#         return Response({
#             "success": False,
#             "error": "Failed to get sync status",
#             "details": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json
# from .models import Applicant
# from .data_mapper_service import DataMapperService
# from api.models import Users
# import logging
# from django.db import transaction

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#     """
#     Clean extracted text:
#     - Remove duplicate lines
#     - Remove repeated inline values (tables)
#     - Strip common headers/footers (boilerplate repeated across pages)
#     """
#     lines = [line.strip() for line in text.splitlines() if line.strip()]

#     # Count line frequency
#     freq = Counter(lines)

#     # If a line appears on >= 5 pages, treat as boilerplate
#     boilerplate = {line for line, count in freq.items() if count >= 5}

#     cleaned_lines = []
#     seen = set()

#     for line in lines:
#         if line in boilerplate:
#             continue  # Skip repeating headers/footers

#         # Collapse table duplicates (split by | or big spaces)
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|")]
#             unique_parts = []
#             for p in parts:
#                 if not unique_parts or p != unique_parts[-1]:
#                     unique_parts.append(p)
#             line = " | ".join(unique_parts)

#         # Collapse repeated words like "Confidential Confidential Confidential"
#         line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#         # Avoid full-line duplicates
#         if line not in seen:
#             seen.add(line)
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines)


# class DocumentUploadView(APIView):
#     """
#     Upload a document (PDF or DOCX), extract text, convert to structured JSON,
#     save into both Applicant table and Users table, and return the response.
#     """

#     def post(self, request, *args, **kwargs):
#         """Handle document upload and save to both models."""
#         file = request.FILES.get("file")
#         if not file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         # Save file temporarily
#         file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#         processor = DocumentProcessor()
#         try:
#             with transaction.atomic():
#                 # Step 1: Extract text from document
#                 result = processor.process_document(default_storage.path(file_path))

#                 # Step 2: Clean extracted text
#                 cleaned_text = clean_text(result.get("extracted_text", ""))

#                 # Step 3: Convert text into structured JSON
#                 structured_json = convert_text_to_json(cleaned_text)

#                 # Ensure structured_json is a dictionary
#                 if not isinstance(structured_json, dict):
#                     logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
#                     structured_json = {
#                         "Personal_Details": {},
#                         "Education": {},
#                         "Contact_Details": {},
#                         "Travel_Documents": {},
#                         "Professional_Qualifications": {},
#                         "Next_of_Kin_Emergency_Contact": {},
#                         "Health_Certificates_Vaccinations": {},
#                         "Covid_19_Vaccination": {},
#                         "Marine_Courses": {},
#                         "Sea_Service_Details": {},
#                         "Specialised_Experience": {},
#                         "References": {},
#                         "Declaration": {},
#                         "Office_Use_Only": {},
#                         "Physical_Measurements": {},
#                         "Language_Skills": {},
#                         "Medical_History": {},
#                         "Assessments": {},
#                         "Competency_Tests": {},
#                         "error": f"Unexpected return type: {type(structured_json)}"
#                     }

#                 # Step 4: Save structured data into Applicant model
#                 applicant = Applicant.objects.create(
#                     personal_details=structured_json.get("Personal_Details", {}),
#                     education=structured_json.get("Education", {}),
#                     contact_details=structured_json.get("Contact_Details", {}),
#                     travel_documents=structured_json.get("Travel_Documents", {}),
#                     professional_qualifications=structured_json.get("Professional_Qualifications", {}),
#                     next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#                     health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
#                     covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
#                     marine_courses=structured_json.get("Marine_Courses", {}),
#                     sea_service_details=structured_json.get("Sea_Service_Details", {}),
#                     specialised_experience=structured_json.get("Specialised_Experience", {}),
#                     references=structured_json.get("References", {}),
#                     declaration=structured_json.get("Declaration", {}),
#                     office_use_only=structured_json.get("Office_Use_Only", {}),
#                     physical_measurements=structured_json.get("Physical_Measurements", {}),
#                     language_skills=structured_json.get("Language_Skills", {}),
#                     medical_history=structured_json.get("Medical_History", {}),
#                     assessments=structured_json.get("Assessments", {}),
#                     competency_tests=structured_json.get("Competency_Tests", {}),
#                 )

#                 logger.info(f"Successfully created applicant with ID: {applicant.id}")

#                 # Step 5: Convert and save to Users model
#                 user = None
#                 user_error = None
#                 try:
#                     logger.info("Converting applicant to Users model")
#                     user = DataMapperService.save_applicant_as_user(applicant)
#                     logger.info(f"Successfully created/updated user: {user.email} (ID: {user.id})")
#                 except Exception as ue:
#                     user_error = f"User creation error: {str(ue)}"
#                     logger.error(f"Failed to create user: {ue}")

#                 # Clean up file
#                 try:
#                     default_storage.delete(file_path)
#                 except Exception as e:
#                     logger.warning(f"Failed to delete temporary file: {e}")

#                 # Response
#                 response_status = status.HTTP_201_CREATED
#                 message = "Data saved successfully to both databases"

#                 if "error" in structured_json:
#                     response_status = status.HTTP_206_PARTIAL_CONTENT
#                     message = "Data saved with parsing issues"

#                 if not user:
#                     response_status = status.HTTP_206_PARTIAL_CONTENT
#                     message = "Data saved to Applicant database, but failed to save to Users database"

#                 return Response({
#                     "message": message,
#                     "applicant_id": applicant.id,
#                     "user_id": user.id if user else None,
#                     "user_email": user.email if user else None,
#                     "file_name": file.name,
#                     "structured_data": structured_json,
#                     "page_count": result.get("page_count"),
#                     "word_count": len(cleaned_text.split()),
#                     "parsing_quality": "low" if "error" in structured_json else "high",
#                     "user_creation_status": "success" if user else "failed",
#                     "user_error": user_error,
#                 }, status=response_status)

#         except DocumentProcessingError as e:
#             try:
#                 default_storage.delete(file_path)
#             except Exception:
#                 pass
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             try:
#                 default_storage.delete(file_path)
#             except Exception:
#                 pass
#             logger.error(f"Unexpected error: {e}")
#             return Response({
#                 "error": "Internal server error",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantListView(APIView):
#     """List all applicants."""

#     def get(self, request, *args, **kwargs):
#         try:
#             applicants = Applicant.objects.all().order_by('-created_at')

#             applicant_list = []
#             for applicant in applicants:
#                 applicant_data = {
#                     "id": applicant.id,
#                     "name": applicant.personal_details.get("name", "Unknown") if applicant.personal_details else "Unknown",
#                     "email": applicant.contact_details.get("email", "") if applicant.contact_details else "",
#                     "nationality": applicant.personal_details.get("nationality", "") if applicant.personal_details else "",
#                     "created_at": applicant.created_at.isoformat(),
#                 }
#                 applicant_list.append(applicant_data)

#             return Response({
#                 "success": True,
#                 "count": len(applicant_list),
#                 "applicants": applicant_list
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error listing applicants: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicants",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantDetailView(APIView):
#     """Get detailed information about a specific applicant."""

#     def get(self, request, applicant_id, *args, **kwargs):
#         try:
#             applicant = Applicant.objects.get(id=applicant_id)

#             return Response({
#                 "success": True,
#                 "applicant": {
#                     "id": applicant.id,
#                     "personal_details": applicant.personal_details,
#                     "education": applicant.education,
#                     "contact_details": applicant.contact_details,
#                     "travel_documents": applicant.travel_documents,
#                     "professional_qualifications": applicant.professional_qualifications,
#                     "next_of_kin_emergency_contact": applicant.next_of_kin_emergency_contact,
#                     "health_certificates_vaccinations": applicant.health_certificates_vaccinations,
#                     "covid_19_vaccination": applicant.covid_19_vaccination,
#                     "marine_courses": applicant.marine_courses,
#                     "sea_service_details": applicant.sea_service_details,
#                     "specialised_experience": applicant.specialised_experience,
#                     "references": applicant.references,
#                     "declaration": applicant.declaration,
#                     "office_use_only": applicant.office_use_only,
#                     "created_at": applicant.created_at.isoformat(),
#                     "updated_at": applicant.updated_at.isoformat(),
#                 }
#             }, status=status.HTTP_200_OK)

#         except Applicant.DoesNotExist:
#             return Response({
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             logger.error(f"Error retrieving applicant {applicant_id}: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicant",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ConvertApplicantToUserView(APIView):
#     """Convert an existing Applicant to a Users instance."""

#     def post(self, request, *args, **kwargs):
#         """
#         Convert an applicant to a user.
#         Expected payload:
#         {
#             "applicant_id": 123
#         }
#         """
#         applicant_id = request.data.get('applicant_id')

#         if not applicant_id:
#             return Response({
#                 "success": False,
#                 "error": "applicant_id is required"
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             applicant = Applicant.objects.get(id=applicant_id)
#         except Applicant.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         try:
#             with transaction.atomic():
#                 user = DataMapperService.save_applicant_as_user(applicant)

#             return Response({
#                 "success": True,
#                 "message": "Applicant converted to user successfully",
#                 "data": {
#                     "applicant_id": applicant.id,
#                     "user_id": user.id,
#                     "user_email": user.email,
#                     "created_at": getattr(user, 'created_at', None)
#                 }
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#             return Response({
#                 "success": False,
#                 "error": "Failed to convert applicant to user",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class BatchConvertApplicantsView(APIView):
#     """Convert multiple applicants to users in batch."""

#     def post(self, request, *args, **kwargs):
#         """
#         Convert multiple applicants to users.
#         Expected payload:
#         {
#             "applicant_ids": [1, 2, 3],
#             or
#             "convert_all": true
#         }
#         """
#         applicant_ids = request.data.get('applicant_ids', [])
#         convert_all = request.data.get('convert_all', False)

#         if convert_all:
#             applicants = Applicant.objects.all()
#         elif applicant_ids:
#             applicants = Applicant.objects.filter(id__in=applicant_ids)
#         else:
#             return Response({
#                 "success": False,
#                 "error": "Either applicant_ids or convert_all=true is required"
#             }, status=status.HTTP_400_BAD_REQUEST)

#         results = {
#             "total_applicants": applicants.count(),
#             "successful_conversions": 0,
#             "failed_conversions": 0,
#             "errors": []
#         }

#         for applicant in applicants:
#             try:
#                 with transaction.atomic():
#                     user = DataMapperService.save_applicant_as_user(applicant)
#                     results["successful_conversions"] += 1
#                     logger.info(f"Successfully converted applicant {applicant.id} to user {user.id}")

#             except Exception as e:
#                 results["failed_conversions"] += 1
#                 error_msg = f"Applicant {applicant.id}: {str(e)}"
#                 results["errors"].append(error_msg)
#                 logger.error(error_msg)

#         return Response({
#             "success": True,
#             "message": (
#                 f"Batch conversion completed. "
#                 f"{results['successful_conversions']} successful, "
#                 f"{results['failed_conversions']} failed."
#             ),
#             "data": results
#         }, status=status.HTTP_200_OK)


# class SyncStatusView(APIView):
#     """Check sync status between Applicant and Users models."""

#     def get(self, request, *args, **kwargs):
#         """Get sync status between the two databases."""
#         try:
#             total_applicants = Applicant.objects.count()
#             total_users = Users.objects.count()

#             # Find applicants without corresponding users (by email)
#             applicant_emails = set()
#             for applicant in Applicant.objects.all():
#                 personal_details = applicant.personal_details or {}
#                 contact_details = applicant.contact_details or {}
#                 email = personal_details.get('email') or contact_details.get('email')
#                 if email:
#                     applicant_emails.add(email.lower())

#             user_emails = {email.lower() for email in Users.objects.values_list('email', flat=True) if email}

#             unsynced_emails = applicant_emails - user_emails

#             return Response({
#                 "success": True,
#                 "data": {
#                     "total_applicants": total_applicants,
#                     "total_users": total_users,
#                     "applicants_with_email": len(applicant_emails),
#                     "users_with_email": len(user_emails),
#                     "unsynced_applicants": len(unsynced_emails),
#                     "unsynced_emails": list(unsynced_emails)[:10],
#                     "sync_percentage": round((len(user_emails) / len(applicant_emails)) * 100, 2)
#                     if applicant_emails else 0
#                 }
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error getting sync status: {e}")
#             return Response({
#                 "success": False,
#                 "error": "Failed to get sync status",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

















# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json
# from .models import Applicant
# from .data_mapper_service import DataMapperService
# from api.models import Users
# import logging
# from django.db import transaction

# logger = logging.getLogger(__name__)


# def clean_text(text: str) -> str:
#     """
#     Clean extracted text:
#     - Remove duplicate lines
#     - Remove repeated inline values (tables)
#     - Strip common headers/footers (boilerplate repeated across pages)
#     """
#     lines = [line.strip() for line in text.splitlines() if line.strip()]

#     # Count line frequency
#     freq = Counter(lines)

#     # If a line appears on >= 5 pages, treat as boilerplate
#     boilerplate = {line for line, count in freq.items() if count >= 5}

#     cleaned_lines = []
#     seen = set()

#     for line in lines:
#         if line in boilerplate:
#             continue  # Skip repeating headers/footers

#         # Collapse table duplicates (split by | or big spaces)
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|")]
#             unique_parts = []
#             for p in parts:
#                 if not unique_parts or p != unique_parts[-1]:
#                     unique_parts.append(p)
#             line = " | ".join(unique_parts)

#         # Collapse repeated words like "Confidential Confidential Confidential"
#         line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#         # Avoid full-line duplicates
#         if line not in seen:
#             seen.add(line)
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines)


# class DocumentUploadView(APIView):
#     """
#     Upload a document (PDF or DOCX), extract text, convert to structured JSON,
#     save into both Applicant table and Users table, and return the response.
#     """

#     def post(self, request, *args, **kwargs):
#         """Handle document upload and save to both models."""
#         file = request.FILES.get("file")
#         if not file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         # Save file temporarily
#         file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

#         processor = DocumentProcessor()
#         try:
#             with transaction.atomic():
#                 # Step 1: Extract text from document
#                 result = processor.process_document(default_storage.path(file_path))

#                 # Step 2: Clean extracted text
#                 cleaned_text = clean_text(result.get("extracted_text", ""))

#                 # Step 3: Convert text into structured JSON
#                 structured_json = convert_text_to_json(cleaned_text)

#                 # Ensure structured_json is a dictionary
#                 if not isinstance(structured_json, dict):
#                     logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
#                     structured_json = {
#                         "Personal_Details": {},
#                         "Education": {},
#                         "Contact_Details": {},
#                         "Travel_Documents": {},
#                         "Professional_Qualifications": {},
#                         "Next_of_Kin_Emergency_Contact": {},
#                         "Health_Certificates_Vaccinations": {},
#                         "Covid_19_Vaccination": {},
#                         "Marine_Courses": {},
#                         "Sea_Service_Details": {},
#                         "Specialised_Experience": {},
#                         "References": {},
#                         "Declaration": {},
#                         "Office_Use_Only": {},
#                         "Physical_Measurements": {},
#                         "Language_Skills": {},
#                         "Medical_History": {},
#                         "Assessments": {},
#                         "Competency_Tests": {},
#                         "Applied_Position_Info": {},
#                         "error": f"Unexpected return type: {type(structured_json)}"
#                     }

#                 # Step 4: Save structured data into Applicant model
#                 applicant = Applicant.objects.create(
#                     personal_details=structured_json.get("Personal_Details", {}),
#                     education=structured_json.get("Education", {}),
#                     contact_details=structured_json.get("Contact_Details", {}),
#                     travel_documents=structured_json.get("Travel_Documents", {}),
#                     professional_qualifications=structured_json.get("Professional_Qualifications", {}),
#                     next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
#                     health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
#                     covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
#                     marine_courses=structured_json.get("Marine_Courses", {}),
#                     sea_service_details=structured_json.get("Sea_Service_Details", {}),
#                     specialised_experience=structured_json.get("Specialised_Experience", {}),
#                     references=structured_json.get("References", {}),
#                     declaration=structured_json.get("Declaration", {}),
#                     office_use_only=structured_json.get("Office_Use_Only", {}),
#                     physical_measurements=structured_json.get("Physical_Measurements", {}),
#                     language_skills=structured_json.get("Language_Skills", {}),
#                     medical_history=structured_json.get("Medical_History", {}),
#                     assessments=structured_json.get("Assessments", {}),
#                     competency_tests=structured_json.get("Competency_Tests", {}),
#                     applied_position_info=structured_json.get("Applied_Position_Info", {}),
#                 )

#                 logger.info(f"Successfully created applicant with ID: {applicant.id}")

#                 # Step 5: Convert and save to Users model
#                 user = None
#                 user_error = None
#                 try:
#                     logger.info("Converting applicant to Users model")
#                     user = DataMapperService.save_applicant_as_user(applicant)
#                     logger.info(f"Successfully created/updated user: {user.email} (ID: {user.id})")
#                 except Exception as ue:
#                     user_error = f"User creation error: {str(ue)}"
#                     logger.error(f"Failed to create user: {ue}")

#                 # Clean up file
#                 try:
#                     default_storage.delete(file_path)
#                 except Exception as e:
#                     logger.warning(f"Failed to delete temporary file: {e}")

#                 # Response
#                 response_status = status.HTTP_201_CREATED
#                 message = "Data saved successfully to both databases"

#                 if "error" in structured_json:
#                     response_status = status.HTTP_206_PARTIAL_CONTENT
#                     message = "Data saved with parsing issues"

#                 if not user:
#                     response_status = status.HTTP_206_PARTIAL_CONTENT
#                     message = "Data saved to Applicant database, but failed to save to Users database"

#                 return Response({
#                     "message": message,
#                     "applicant_id": applicant.id,
#                     "user_id": user.id if user else None,
#                     "user_email": user.email if user else None,
#                     "file_name": file.name,
#                     "structured_data": structured_json,
#                     "page_count": result.get("page_count"),
#                     "word_count": len(cleaned_text.split()),
#                     "parsing_quality": "low" if "error" in structured_json else "high",
#                     "user_creation_status": "success" if user else "failed",
#                     "user_error": user_error,
#                 }, status=response_status)

#         except DocumentProcessingError as e:
#             try:
#                 default_storage.delete(file_path)
#             except Exception:
#                 pass
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             try:
#                 default_storage.delete(file_path)
#             except Exception:
#                 pass
#             logger.error(f"Unexpected error: {e}")
#             return Response({
#                 "error": "Internal server error",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantListView(APIView):
#     """List all applicants."""

#     def get(self, request, *args, **kwargs):
#         try:
#             applicants = Applicant.objects.all().order_by('-created_at')

#             applicant_list = []
#             for applicant in applicants:
#                 applicant_data = {
#                     "id": applicant.id,
#                     "name": applicant.personal_details.get("name", "Unknown") if applicant.personal_details else "Unknown",
#                     "email": applicant.contact_details.get("email", "") if applicant.contact_details else "",
#                     "nationality": applicant.personal_details.get("nationality", "") if applicant.personal_details else "",
#                     "created_at": applicant.created_at.isoformat(),
#                 }
#                 applicant_list.append(applicant_data)

#             return Response({
#                 "success": True,
#                 "count": len(applicant_list),
#                 "applicants": applicant_list
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error listing applicants: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicants",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ApplicantDetailView(APIView):
#     """Get detailed information about a specific applicant."""

#     def get(self, request, applicant_id, *args, **kwargs):
#         try:
#             applicant = Applicant.objects.get(id=applicant_id)

#             return Response({
#                 "success": True,
#                 "applicant": {
#                     "id": applicant.id,
#                     "personal_details": applicant.personal_details,
#                     "education": applicant.education,
#                     "contact_details": applicant.contact_details,
#                     "travel_documents": applicant.travel_documents,
#                     "professional_qualifications": applicant.professional_qualifications,
#                     "next_of_kin_emergency_contact": applicant.next_of_kin_emergency_contact,
#                     "health_certificates_vaccinations": applicant.health_certificates_vaccinations,
#                     "covid_19_vaccination": applicant.covid_19_vaccination,
#                     "marine_courses": applicant.marine_courses,
#                     "sea_service_details": applicant.sea_service_details,
#                     "specialised_experience": applicant.specialised_experience,
#                     "references": applicant.references,
#                     "declaration": applicant.declaration,
#                     "office_use_only": applicant.office_use_only,
#                     "physical_measurements": applicant.physical_measurements,
#                     "language_skills": applicant.language_skills,
#                     "medical_history": applicant.medical_history,
#                     "assessments": applicant.assessments,
#                     "competency_tests": applicant.competency_tests,
#                     "applied_position_info": applicant.applied_position_info,
#                     "created_at": applicant.created_at.isoformat(),
#                     "updated_at": applicant.updated_at.isoformat(),
#                 }
#             }, status=status.HTTP_200_OK)

#         except Applicant.DoesNotExist:
#             return Response({
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             logger.error(f"Error retrieving applicant {applicant_id}: {e}")
#             return Response({
#                 "error": "Failed to retrieve applicant",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ConvertApplicantToUserView(APIView):
#     """Convert an existing Applicant to a Users instance."""

#     def post(self, request, *args, **kwargs):
#         """
#         Convert an applicant to a user.
#         Expected payload:
#         {
#             "applicant_id": 123
#         }
#         """
#         applicant_id = request.data.get('applicant_id')

#         if not applicant_id:
#             return Response({
#                 "success": False,
#                 "error": "applicant_id is required"
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             applicant = Applicant.objects.get(id=applicant_id)
#         except Applicant.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "error": f"Applicant with ID {applicant_id} not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         try:
#             with transaction.atomic():
#                 user = DataMapperService.save_applicant_as_user(applicant)

#             return Response({
#                 "success": True,
#                 "message": "Applicant converted to user successfully",
#                 "data": {
#                     "applicant_id": applicant.id,
#                     "user_id": user.id,
#                     "user_email": user.email,
#                     "created_at": getattr(user, 'created_at', None)
#                 }
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error converting applicant {applicant_id} to user: {e}")
#             return Response({
#                 "success": False,
#                 "error": "Failed to convert applicant to user",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class BatchConvertApplicantsView(APIView):
#     """Convert multiple applicants to users in batch."""

#     def post(self, request, *args, **kwargs):
#         """
#         Convert multiple applicants to users.
#         Expected payload:
#         {
#             "applicant_ids": [1, 2, 3],
#             or
#             "convert_all": true
#         }
#         """
#         applicant_ids = request.data.get('applicant_ids', [])
#         convert_all = request.data.get('convert_all', False)

#         if convert_all:
#             applicants = Applicant.objects.all()
#         elif applicant_ids:
#             applicants = Applicant.objects.filter(id__in=applicant_ids)
#         else:
#             return Response({
#                 "success": False,
#                 "error": "Either applicant_ids or convert_all=true is required"
#             }, status=status.HTTP_400_BAD_REQUEST)

#         results = {
#             "total_applicants": applicants.count(),
#             "successful_conversions": 0,
#             "failed_conversions": 0,
#             "errors": []
#         }

#         for applicant in applicants:
#             try:
#                 with transaction.atomic():
#                     user = DataMapperService.save_applicant_as_user(applicant)
#                 results["successful_conversions"] += 1
#                 logger.info(f"Successfully converted applicant {applicant.id} to user {user.id}")

#             except Exception as e:
#                 results["failed_conversions"] += 1
#                 error_msg = f"Applicant {applicant.id}: {str(e)}"
#                 results["errors"].append(error_msg)
#                 logger.error(error_msg)

#         return Response({
#             "success": True,
#             "message": (
#                 f"Batch conversion completed. "
#                 f"{results['successful_conversions']} successful, "
#                 f"{results['failed_conversions']} failed."
#             ),
#             "data": results
#         }, status=status.HTTP_200_OK)


# class SyncStatusView(APIView):
#     """Check sync status between Applicant and Users models."""

#     def get(self, request, *args, **kwargs):
#         """Get sync status between the two databases."""
#         try:
#             total_applicants = Applicant.objects.count()
#             total_users = Users.objects.count()

#             # Find applicants without corresponding users (by email)
#             applicant_emails = set()
#             for applicant in Applicant.objects.all():
#                 personal_details = applicant.personal_details or {}
#                 contact_details = applicant.contact_details or {}
#                 email = personal_details.get('email') or contact_details.get('email')
#                 if email:
#                     applicant_emails.add(email.lower())

#             user_emails = {email.lower() for email in Users.objects.values_list('email', flat=True) if email}

#             unsynced_emails = applicant_emails - user_emails

#             return Response({
#                 "success": True,
#                 "data": {
#                     "total_applicants": total_applicants,
#                     "total_users": total_users,
#                     "applicants_with_email": len(applicant_emails),
#                     "users_with_email": len(user_emails),
#                     "unsynced_applicants": len(unsynced_emails),
#                     "unsynced_emails": list(unsynced_emails)[:10],
#                     "sync_percentage": round((len(user_emails) / len(applicant_emails)) * 100, 2)
#                     if applicant_emails else 0
#                 }
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"Error getting sync status: {e}")
#             return Response({
#                 "success": False,
#                 "error": "Failed to get sync status",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



























"""
Fixed Django REST Framework views with proper serializer integration.
Follows DRF best practices and uses serializers for validation and responses.
"""

import re
import os
import logging
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api.permissions import IsAdmin
from .extractors import SakrTemplateExtractor, ErrorCode, client_message
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction

from .document_processor import DocumentProcessor, DocumentProcessingError
from .document_to_json import convert_text_to_json
from .models import Applicant
from .data_mapper_service import DataMapperService
# from .serializers import (
#     ApplicantToUsersSerializer,
#     DocumentUploadSerializer,
#     ConvertApplicantRequestSerializer,
#     BatchConvertRequestSerializer,
#     ApplicantListSerializer,
# )
from .serializers import ApplicantListSerializer, ApplicantToUsersSerializer, BatchConvertRequestSerializer, ConvertApplicantRequestSerializer, DocumentUploadSerializer
from api.models import Users

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean extracted text:
    - Remove duplicate lines
    - Remove repeated inline values (tables)
    - Strip common headers/footers (boilerplate repeated across pages)
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Count line frequency
    freq = Counter(lines)

    # If a line appears on >= 5 pages, treat as boilerplate
    boilerplate = {line for line, count in freq.items() if count >= 5}

    cleaned_lines = []
    seen = set()

    for line in lines:
        if line in boilerplate:
            continue  # Skip repeating headers/footers

        # Collapse table duplicates (split by | or big spaces)
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            unique_parts = []
            for p in parts:
                if not unique_parts or p != unique_parts[-1]:
                    unique_parts.append(p)
            line = " | ".join(unique_parts)

        # Collapse repeated words like "Confidential Confidential Confidential"
        line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

        # Avoid full-line duplicates
        if line not in seen:
            seen.add(line)
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def _create_related_user_models(user, applicant, convert_date_func):
    from courses.models import Course
    from api.models import SeaService, Reference
    
    _mc = applicant.marine_courses if isinstance(applicant.marine_courses, list) else []
    if _mc:
        user.courses.all().delete()
        for c in _mc:
            Course.objects.create(
                user=user,
                course_name=c.get('course_name', ''),
                course_number=c.get('number', '') or c.get('course_number', ''),
                issue_date=convert_date_func(c.get('issue_date')),
                expiry_date=convert_date_func(c.get('expiry_date')),
                issued_by=c.get('issued_by', '') or c.get('issued_by_at', ''),
                issued_at=c.get('issued_at', '')
            )

    _ss = applicant.sea_service_details if isinstance(applicant.sea_service_details, list) else []
    if _ss:
        user.sea_services.all().delete()
        for r in _ss:
            vni = r.get('vessel_name_imo_number', '') or r.get('vessel_name_imo', '') or ''
            dg = r.get('dwt_grt', '') or ''
            bk = r.get('bh_kw', '') or ''
            
            vessel_name = vni.split('/')[0].strip() if '/' in vni else vni
            imo_number = vni.split('/')[1].strip() if '/' in vni and len(vni.split('/')) > 1 else ''
            
            dwt = dg.split('/')[0].strip() if '/' in dg else dg
            grt = dg.split('/')[1].strip() if '/' in dg and len(dg.split('/')) > 1 else ''
            
            bh = bk.split('/')[0].strip() if '/' in bk else bk
            kw = bk.split('/')[1].strip() if '/' in bk and len(bk.split('/')) > 1 else ''
            
            SeaService.objects.create(
                user=user,
                company_name=r.get('company_name', ''),
                rank=r.get('rank', ''),
                vessel_name=vessel_name,
                imo_number=imo_number,
                flag=r.get('flag', ''),
                signed_on=convert_date_func(r.get('signed_on')),
                signed_off=convert_date_func(r.get('signed_off')),
                period=r.get('period', ''),
                vessel_type=r.get('vessel_type', ''),
                dwt=dwt,
                grt=grt,
                engine_type=r.get('engine_type', ''),
                bh=bh,
                kw=kw,
                reason_for_sign_off=r.get('reason_for_sign_off', '')
            )

    _ref = applicant.references if isinstance(applicant.references, list) else []
    if _ref:
        user.references.all().delete()
        for r in _ref:
            Reference.objects.create(
                user=user,
                company_name=r.get('company_management_country', '') or r.get('company_name', ''),
                position=r.get('position', ''),
                name=r.get('name', ''),
                tel=r.get('tel', ''),
                email=r.get('email', '')
            )


class DocumentUploadView(APIView):
    """
    Upload a CV (PDF or DOCX) and extract a structured JSON.

    This endpoint is the LLM-backed counterpart to ``POST /ai/parse/``.
    Both endpoints accept the same multipart payload and return the
    same response shape — the only difference is the extraction
    pipeline underneath:

    1. The deterministic ``SakrTemplateExtractor`` runs FIRST (no LLM
       cost, no rate limits, no API key needed). If the document
       matches the Sakr CV form template, the deterministic output
       is used.
    2. If the deterministic extractor reports ``NOT_SAKR_TEMPLATE``
       (the document doesn't match the Sakr form), we fall back to
       the LLM path (``convert_text_to_json``). The LLM router
       inside that helper tries providers in this order:
         a. **Ollama (local, free)** — set ``OLLAMA_HOST`` env var
            on the server. Recommended model ``qwen2.5:7b``.
         b. **Groq (cloud)** — Groq keys in the request or env.
         c. **Gemini (cloud)** — last resort.
       When Ollama is up, the LLM path is free and private (the
       CV never leaves the server).
    3. If the LLM path is also unable to extract a valid maritime
       CV (validation failure, every provider down), the endpoint
       returns a 400 with the validation_error message — no save
       happens.

    Response shape (matches ``/ai/parse/`` exactly)::

        {
            "success": true,
            "extractor": "sakr_template" | "deepseek_llm",
            "confidence": 0.95,
            "data": { ... 12-section numbered format ... },
            "warnings": [],
            "file_name": "cv.pdf",
            "saved": true,                // only if save_to_db=true
            "user_id": 123,                // only if save_to_db=true
            "cv_submission_id": 456       // only if save_to_db=true
        }

    Request (multipart form-data):

        file             required — the CV file (PDF or DOCX)
        save_to_db       optional — "true" (default) to also create
                         User + CVSubmission via the same flow as
                         ``/ai/parse/``. Pass "false" for a
                         dry-run parse (no DB writes).
        deepseek_api_key  optional — per-request DeepSeek key (cloud LLM
                         fallback). Not needed when Ollama is up.
        api_keys_config  optional — JSON string with full key
                         config (cloud LLM fallback). Not needed
                         when Ollama is up.

    Auth: ``AllowAny`` for backwards compatibility with the original
    endpoint. The deterministic path never calls the LLM, so the
    public-facing endpoint is safe to hit; if you need admin-only
    access, restrict this URL at the gateway or change to
    ``[JWTAuthentication] + [IsAdmin]`` like ``/ai/parse/``.
    """
    authentication_classes = []  # AllowAny — kept for backwards compat
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DocumentUploadSerializer

    def post(self, request, *args, **kwargs):
        # --- 1. Validate the upload ----------------------------------
        upload_serializer = DocumentUploadSerializer(data=request.data)
        if not upload_serializer.is_valid():
            return Response(
                upload_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = upload_serializer.validated_data.get("file")
        if not file:
            return Response(
                {
                    "success": False,
                    "error": ErrorCode.FILE_MISSING.value,
                    "message": client_message(ErrorCode.FILE_MISSING),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        save_to_db = str(request.data.get("save_to_db", "true")).lower() == "true"

        # Save the file to a temp path so DocumentProcessor can read it
        # back. We always clean this up in the finally block.
        file_path = default_storage.save(
            f"tmp/{file.name}", ContentFile(file.read())
        )
        try:
            processor = DocumentProcessor()
            try:
                proc_result = processor.process_document(
                    default_storage.path(file_path)
                )
            except DocumentProcessingError as exc:
                logger.warning(
                    "DocumentUploadView: DocumentProcessor failed for %s: %s",
                    file.name, exc,
                )
                return Response(
                    {
                        "success": False,
                        "error": ErrorCode.FILE_UNSUPPORTED_FORMAT.value,
                        "message": str(exc),
                        "file_name": file.name,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            text = proc_result.get("extracted_text", "") or ""
            tables = proc_result.get("tables", []) or []
            # OCR meta from DocumentProcessor. The processor already
            # ran OCR (via Ollama or Gemini) when the regular text
            # extractor found very little. We pass this through to
            # the response so the client can see whether OCR kicked
            # in for this CV.
            ocr_meta = {
                "ocr_applied": bool(proc_result.get("ocr_applied")),
                "ocr_pages_processed": int(
                    proc_result.get("ocr_pages_processed") or 0
                ),
                "ocr_backend": proc_result.get("ocr_backend"),
            }

            # --- 2. Try deterministic extractor first ----------------
            result_data = None
            extractor_name = None
            confidence = None
            warnings: list[str] = []

            try:
                deterministic = SakrTemplateExtractor().extract(text, tables)
            except Exception:
                logger.exception("DocumentUploadView: SakrTemplateExtractor crashed")
                deterministic = None

            if deterministic and deterministic.ok:
                result_data = deterministic.data
                extractor_name = deterministic.extractor
                confidence = deterministic.confidence
                warnings = list(deterministic.warnings or [])
                logger.info(
                    "DocumentUploadView: deterministic parser OK for %s (confidence=%s)",
                    file.name, confidence,
                )
            else:
                # --- 3. Fall back to LLM ----------------------------
                if deterministic and deterministic.warnings:
                    warnings.extend(list(deterministic.warnings))
                fallback_reason = (
                    deterministic.error.value
                    if deterministic and deterministic.error
                    else "not_sakr_template"
                )
                logger.info(
                    "DocumentUploadView: deterministic parser failed (%s); "
                    "falling back to LLM for %s",
                    fallback_reason, file.name,
                )

                api_keys_config = self._resolve_api_keys_config(request)
                # NOTE: With Ollama configured on the server, an empty
                # api_keys_config is fine — the LLM router in
                # document_to_json.py will try Ollama first (free,
                # local, no key needed) before any cloud provider.
                # The 400 "api_keys_missing" short-circuit was the
                # right answer in the cloud-only era, but it now
                # blocks the free local fallback. We always pass the
                # dict through; if EVERY provider (Ollama + Groq +
                # Gemini) is unavailable, convert_text_to_json will
                # return a validation_error and we surface that as
                # 400 below.
                if api_keys_config is None:
                    api_keys_config = {}

                try:
                    llm_result, _updated_keys = convert_text_to_json(
                        text,
                        parsed_tables=tables,
                        api_keys_config=api_keys_config,
                    )
                except Exception as exc:
                    logger.exception(
                        "DocumentUploadView: LLM fallback crashed for %s", file.name,
                    )
                    return Response(
                        {
                            "success": False,
                            "error": "llm_failed",
                            "message": (
                                "LLM extraction failed: "
                                f"{exc.__class__.__name__}"
                            ),
                            "file_name": file.name,
                            "warnings": warnings,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                if not isinstance(llm_result, dict):
                    return Response(
                        {
                            "success": False,
                            "error": "llm_bad_response",
                            "message": (
                                "LLM returned a non-dict response "
                                f"({type(llm_result).__name__})."
                            ),
                            "file_name": file.name,
                            "warnings": warnings,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                if "validation_error" in llm_result:
                    return Response(
                        {
                            "success": False,
                            "error": "invalid_document",
                            "message": llm_result.get(
                                "validation_error",
                                "Document is not a valid maritime CV.",
                            ),
                            "file_name": file.name,
                            "warnings": warnings,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not llm_result:
                    return Response(
                        {
                            "success": False,
                            "error": "llm_empty",
                            "message": "LLM extraction returned no data.",
                            "file_name": file.name,
                            "warnings": warnings,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                result_data = llm_result
                extractor_name = "deepseek_llm"
                # LLM has no numeric confidence in this project; report
                # 0.7 as a generic "we used an LLM, treat carefully" hint.
                confidence = 0.7
                logger.info(
                    "DocumentUploadView: LLM fallback OK for %s (sections=%s)",
                    file.name, sorted(result_data.keys()),
                )

            # --- 4. Build the /ai/parse/-shaped response -------------
            response_body = {
                "success": True,
                "extractor": extractor_name,
                "confidence": confidence,
                "data": result_data,
                "warnings": warnings,
                "file_name": file.name,
                # OCR meta — useful when the original file was a
                # scanned PDF and the LLM/deterministic parser was
                # fed text from the OCR fallback rather than the
                # native PDF text layer.
                "ocr": ocr_meta,
            }

            # --- 5. Persist (optional) -------------------------------
            if save_to_db:
                try:
                    user_id, cv_submission_id, dropped_sea_service = _save_parser_output(
                        result_data,
                        file,
                        extracted_photo_path=proc_result.get("extracted_photo_path"),
                    )
                except _NoEmailError:
                    return Response(
                        {
                            "success": False,
                            "error": "email_missing",
                            "message": (
                                "Cannot save: the CV has no email address."
                            ),
                            "data": result_data,
                            "extractor": extractor_name,
                            "confidence": confidence,
                            "file_name": file.name,
                            "warnings": warnings,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                response_body["saved"] = True
                response_body["user_id"] = user_id
                response_body["cv_submission_id"] = cv_submission_id
                # Surface any sea-service records that were dropped
                # as overlapping duplicates. Frontend can show a
                # warning like "X records were ignored because they
                # overlap with longer records".
                if dropped_sea_service:
                    response_body["dropped_sea_service"] = dropped_sea_service
            else:
                response_body["saved"] = False

            return Response(response_body, status=status.HTTP_200_OK)

        except Exception:
            # Catch-all: never leak the exception text to the client.
            # The full traceback is in the server logs.
            logger.exception("DocumentUploadView: unexpected error")
            return Response(
                {
                    "success": False,
                    "error": ErrorCode.INTERNAL.value,
                    "message": client_message(ErrorCode.INTERNAL),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            # Always clean up the temp upload.
            try:
                default_storage.delete(file_path)
            except Exception:
                logger.warning(
                    "DocumentUploadView: failed to delete temp file %s",
                    file_path,
                )

    @staticmethod
    def _resolve_api_keys_config(request) -> dict | None:
        """Build the ``api_keys_config`` dict for the LLM fallback.

        Mirrors the legacy behaviour:

        * If the request supplies ``api_keys_config`` as JSON, parse it.
        * Otherwise accept a per-request ``deepseek_api_key`` and wrap it
          in the same shape ``convert_text_to_json`` expects.
        * Returns ``None`` if neither is present.

        Note: ``None`` here does NOT mean "no LLM available" — the
        LLM router will still try Ollama (local, free) on the empty
        dict. Only if Ollama is also down will ``convert_text_to_json``
        return a validation_error, which the view surfaces as 400.
        """
        import json
        import os

        api_keys_config: dict = {}
        api_keys_config_str = request.data.get("api_keys_config")
        if api_keys_config_str:
            try:
                parsed = json.loads(api_keys_config_str)
                if isinstance(parsed, str):
                    parsed = json.loads(parsed)
                if isinstance(parsed, dict):
                    api_keys_config = parsed
            except Exception:
                # Malformed JSON — fall through to the deepseek_api_key
                # check below.
                pass

        if not api_keys_config:
            deepseek_api_key = request.data.get("deepseek_api_key")
            if deepseek_api_key:
                os.environ["DEEPSEEK_API_KEY"] = deepseek_api_key
                api_keys_config = {
                    "deepseek": [
                        {
                            "key": deepseek_api_key,
                            "status": "live",
                            "reset_time": None,
                        }
                    ],
                    "gemini": "",
                }

        return api_keys_config or None


class ApplicantListView(APIView):
    """
    List all applicants using ApplicantListSerializer.
    Returns lightweight summary data for listing.
    """

    def get(self, request, *args, **kwargs):
        """Retrieve list of all applicants with serializer."""
        try:
            applicants = Applicant.objects.all().order_by('-created_at')

            # Use serializer for consistent response format
            serializer = ApplicantListSerializer(applicants, many=True)

            return Response({
                "success": True,
                "count": applicants.count(),
                "applicants": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing applicants: {e}")
            return Response({
                "success": False,
                "error": "Failed to retrieve applicants",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplicantDetailView(APIView):
    """
    Get detailed information about a specific applicant.
    Uses ApplicantToUsersSerializer for complete data.
    """

    def get(self, request, applicant_id, *args, **kwargs):
        """Retrieve complete applicant data using serializer."""
        try:
            applicant = Applicant.objects.get(id=applicant_id)

            # Use serializer for consistent response format
            serializer = ApplicantToUsersSerializer(applicant)

            return Response({
                "success": True,
                "applicant": serializer.data
            }, status=status.HTTP_200_OK)

        except Applicant.DoesNotExist:
            return Response({
                "success": False,
                "error": f"Applicant with ID {applicant_id} not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error retrieving applicant {applicant_id}: {e}")
            return Response({
                "success": False,
                "error": "Failed to retrieve applicant",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConvertApplicantToUserView(APIView):
    """
    Convert an existing Applicant to a Users instance.
    Uses serializer for request validation.
    """

    def post(self, request, *args, **kwargs):
        """
        Convert an applicant to a user with proper validation.
        """
        # Validate request using serializer
        request_serializer = ConvertApplicantRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response({
                "success": False,
                "errors": request_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        applicant_id = request_serializer.validated_data['applicant_id']

        try:
            applicant = Applicant.objects.get(id=applicant_id)
        except Applicant.DoesNotExist:
            return Response({
                "success": False,
                "error": f"Applicant with ID {applicant_id} not found"
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                user = DataMapperService.save_applicant_as_user(applicant)

            # Use serializer for applicant data
            applicant_serializer = ApplicantToUsersSerializer(applicant)

            return Response({
                "success": True,
                "message": "Applicant converted to user successfully",
                "data": {
                    "applicant_id": applicant.id,
                    "user_id": user.id,
                    "user_email": user.email,
                    "created_at": getattr(user, 'created_at', None),
                    "applicant_data": applicant_serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error converting applicant {applicant_id} to user: {e}")
            return Response({
                "success": False,
                "error": "Failed to convert applicant to user",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchConvertApplicantsView(APIView):
    """
    Convert multiple applicants to users in batch.
    Uses serializer for request validation.
    """

    def post(self, request, *args, **kwargs):
        """
        Convert multiple applicants to users with proper validation.
        """
        # Validate request using serializer
        request_serializer = BatchConvertRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response({
                "success": False,
                "errors": request_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        applicant_ids = request_serializer.validated_data.get('applicant_ids', [])
        convert_all = request_serializer.validated_data.get('convert_all', False)

        if convert_all:
            applicants = Applicant.objects.all()
        else:
            applicants = Applicant.objects.filter(id__in=applicant_ids)

        results = {
            "total_applicants": applicants.count(),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "errors": [],
            "converted_users": []
        }

        for applicant in applicants:
            try:
                with transaction.atomic():
                    user = DataMapperService.save_applicant_as_user(applicant)
                
                results["successful_conversions"] += 1
                results["converted_users"].append({
                    "applicant_id": applicant.id,
                    "user_id": user.id,
                    "user_email": user.email
                })
                logger.info(f"Successfully converted applicant {applicant.id} to user {user.id}")

            except Exception as e:
                results["failed_conversions"] += 1
                error_msg = f"Applicant {applicant.id}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)

        return Response({
            "success": True,
            "message": (
                f"Batch conversion completed. "
                f"{results['successful_conversions']} successful, "
                f"{results['failed_conversions']} failed."
            ),
            "data": results
        }, status=status.HTTP_200_OK)


class SyncStatusView(APIView):
    """
    Check sync status between Applicant and Users models.
    """

    def get(self, request, *args, **kwargs):
        """Get sync status between the two databases."""
        try:
            total_applicants = Applicant.objects.count()
            total_users = Users.objects.count()

            # Find applicants without corresponding users (by email)
            applicant_emails = set()
            for applicant in Applicant.objects.all():
                personal_details = applicant.personal_details or {}
                contact_details = applicant.contact_details or {}
                email = personal_details.get('email') or contact_details.get('email')
                if email:
                    applicant_emails.add(email.lower())

            user_emails = {email.lower() for email in Users.objects.values_list('email', flat=True) if email}

            unsynced_emails = applicant_emails - user_emails

            return Response({
                "success": True,
                "data": {
                    "total_applicants": total_applicants,
                    "total_users": total_users,
                    "applicants_with_email": len(applicant_emails),
                    "users_with_email": len(user_emails),
                    "unsynced_applicants": len(unsynced_emails),
                    "unsynced_emails": list(unsynced_emails)[:10],
                    "sync_percentage": round((len(user_emails) / len(applicant_emails)) * 100, 2)
                    if applicant_emails else 0
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return Response({
                "success": False,
                "error": "Failed to get sync status",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveApplicantView(APIView):
    """
    Accepts reviewed structured JSON from the frontend and saves it into the
    Applicant and Users tables.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            structured_json = request.data.get('structured_data')
            if not structured_json:
                return Response({'error': 'No structured_data provided'}, status=status.HTTP_400_BAD_REQUEST)

            file_name = request.data.get('file_name', 'manual_upload.pdf')

            with transaction.atomic():
                _pd  = structured_json.get('1_personal_details', {})
                _edu = structured_json.get('2_education', {})
                _cd  = structured_json.get('3_contact_details', {})
                _td  = structured_json.get('4_travel_documents', [])
                _pq  = structured_json.get('5_professional_qualification_certificate_of_competency', [])
                _nok = structured_json.get('6_next_of_kin_emergency_contact', {})
                _hcv = structured_json.get('7_health_certificates_and_vaccinations', {})
                _mc  = structured_json.get('8_marine_courses', [])
                _ss  = structured_json.get('9_complete_sea_service_details', {})
                _ref = structured_json.get('10_references', [])
                _dec = structured_json.get('11_declaration', {})
                _ofc = structured_json.get('12_for_office_use_only', {})

                ms_raw = _pd.get('marital_status', {})
                if isinstance(ms_raw, dict):
                    if ms_raw.get('married'):
                        marital_str = 'Married'
                    elif ms_raw.get('single'):
                        marital_str = 'Single'
                    else:
                        marital_str = ''
                    _pd_for_model = {**_pd, 'marital_status': marital_str}
                else:
                    _pd_for_model = _pd

                _cd_normalised = {
                    'Email': _cd.get('e_mail', '') or _cd.get('Email', ''),
                    'Mobile_Tel': _cd.get('mobile_tel', '') or _cd.get('Mobile_Tel', ''),
                    'Home_Address_City': _cd.get('home_address_city', '') or _cd.get('Home_Address_City', ''),
                }

                _td_normalised = []
                for doc in (_td if isinstance(_td, list) else []):
                    _td_normalised.append({
                        'Type': doc.get('type', doc.get('Type', '')),
                        'Document_No': doc.get('document_no', doc.get('Document_No', '')),
                        'ISS_Date': doc.get('iss_date', doc.get('ISS_Date', '')),
                        'Exp_Date': doc.get('exp_date', doc.get('Exp_Date', '')),
                        'ISS_By_Authority': doc.get('iss_by_authority', doc.get('ISS_By_Authority', '')),
                        'Place_of_Issue': doc.get('place_of_issue', doc.get('Place_of_Issue', '')),
                    })

                applicant = Applicant.objects.create(
                    personal_details=_pd_for_model,
                    education=_edu,
                    contact_details=_cd_normalised,
                    travel_documents=_td_normalised,
                    professional_qualifications=_pq,
                    next_of_kin_emergency_contact=_nok,
                    health_certificates_vaccinations=_hcv,
                    covid_19_vaccination=_hcv.get('covid_19', {}),
                    marine_courses=_mc,
                    sea_service_details=_ss.get('service_records', []),
                    specialised_experience=[],
                    references=_ref,
                    declaration=_dec,
                    office_use_only=_ofc,
                    physical_measurements={},
                    language_skills={},
                    medical_history={},
                    assessments={},
                    competency_tests={},
                    applied_position_info={},
                )

                logger.info(f'Successfully created applicant with ID: {applicant.id}')

                applicant_serializer = ApplicantToUsersSerializer(applicant)

                user = None
                user_error = None
                try:
                    logger.info('Converting applicant to Users model')
                    from api.models import Users
                    from django.db import models
                    from datetime import datetime
                    
                    serializer_data = applicant_serializer.data

                    email = serializer_data.get('email')
                    if not email:
                        raise ValueError(['Email is required'])
                    
                    def convert_date(date_str):
                        if not date_str or not str(date_str).strip():
                            return None
                        
                        date_str = str(date_str).strip()
                        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y', '%Y/%m/%d']
                        for fmt in formats:
                            try:
                                dt = datetime.strptime(date_str, fmt)
                                return dt.strftime('%Y-%m-%d')
                            except ValueError:
                                continue
                        return None
                    
                    user_model_fields = {f.name: f for f in Users._meta.get_fields()}
                    defaults = {}
                    for field_name, value in serializer_data.items():
                        if field_name in ['id', 'email', 'created_at', 'updated_at', 'ranks', 'certificates', 'references', 'sea_services']:
                            continue
                        if field_name not in user_model_fields:
                            continue
                        
                        field = user_model_fields[field_name]
                        if isinstance(field, (models.DateField, models.DateTimeField)):
                            defaults[field_name] = convert_date(value)
                        elif isinstance(field, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField)):
                            try:
                                defaults[field_name] = int(value) if value and str(value).strip() else None
                            except (ValueError, TypeError):
                                defaults[field_name] = None
                        elif isinstance(field, (models.FloatField, models.DecimalField)):
                            try:
                                defaults[field_name] = float(value) if value and str(value).strip() else None
                            except (ValueError, TypeError):
                                defaults[field_name] = None
                        elif isinstance(field, models.BooleanField):
                            defaults[field_name] = bool(value) if value else False
                        elif isinstance(field, models.JSONField):
                            defaults[field_name] = value if value else {}
                        else:
                            defaults[field_name] = value if value else ''
                    
                    user, created = Users.objects.update_or_create(
                        email=email,
                        defaults=defaults
                    )
                    _create_related_user_models(user, applicant, convert_date)
                    
                except Exception as ue:
                    user_error = f'User creation error: {str(ue)}'
                    logger.error(f'Failed to create user: {ue}')

                response_status = status.HTTP_201_CREATED
                message = 'Data saved successfully to both databases'

                if 'error' in structured_json:
                    response_status = status.HTTP_206_PARTIAL_CONTENT
                    message = 'Data saved with parsing issues'

                if not user:
                    response_status = status.HTTP_206_PARTIAL_CONTENT
                    message = 'Data saved to Applicant database, but failed to save to Users database'

                from datetime import datetime
                return Response({
                    'id': applicant.id,
                    'user': user.id if user else None,
                    'user_name': _pd_for_model.get('full_name', '') if isinstance(_pd_for_model, dict) else '',
                    'user_email_display': user.email if user else None,
                    'status': 'Pending',
                    'submitted_date': datetime.now().strftime('%Y-%m-%d'),
                    'notes': 'Saved from Review Data',
                    '_upload_meta': {
                        'success': True,
                        'message': message,
                        'user_creation_status': 'success' if user else 'failed',
                        'user_error': user_error,
                    }
                }, status=response_status)

        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'success': False,
                'error': 'Failed to save applicant',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CheckQuotaView(APIView):
    """
    Endpoint to check Groq's exact remaining quota by sending a 1-token dummy request.
    This fetches the true headers instead of just tracking session tokens.
    """

    def post(self, request):
        try:
            api_keys_config_str = request.data.get("api_keys_config", "")
            if not api_keys_config_str:
                return Response({"success": False, "error": "No API keys provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                import json
                api_keys_config = json.loads(api_keys_config_str)
            except json.JSONDecodeError:
                return Response({"success": False, "error": "Invalid API keys format"}, status=status.HTTP_400_BAD_REQUEST)

            groq_keys = api_keys_config.get("groq", [])
            active_key = None
            for key_obj in groq_keys:
                if key_obj.get("status") == "live" and key_obj.get("key"):
                    active_key = key_obj["key"]
                    break

            if not active_key:
                return Response({"success": False, "error": "No live Groq key found to check quota."})

            import requests
            from django.conf import settings
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }
            # Use the configured primary model for the quota probe so
            # we don't 404 a deprecated name.
            data = {
                "model": getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 1
            }
            res = requests.post(url, headers=headers, json=data, timeout=10)
            
            if res.status_code == 200:
                limit = res.headers.get("x-ratelimit-limit-tokens-today", "Unknown")
                remaining = res.headers.get("x-ratelimit-remaining-tokens-today", "Unknown")
                return Response({
                    "success": True, 
                    "limit": limit, 
                    "remaining": remaining,
                    "provider": "groq"
                })
            else:
                return Response({
                    "success": False,
                    "error": f"Groq API returned {res.status_code}"
                })

        except Exception as e:
            import traceback
            logger.error(f"Error checking quota: {str(e)}\n{traceback.format_exc()}")
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParseOnlyView(APIView):
    """
    Parse a CV using the deterministic Sakr-template parser.

    Unlike ``POST /ai/upload/``, this endpoint:

      * Does **not** call any LLM (no Groq, no Gemini, no rate limits).
      * Returns the extracted JSON directly for testing / side-by-side
        comparison against the LLM path.

    With ``save_to_db=true`` (form field), the parsed data is also
    persisted to the database:

      * A ``Users`` row is created (or updated if the email already
        exists) from the parser output.
      * A ``CVSubmission`` row is created and linked to the new user,
        with the uploaded file attached, plus ``expected_salary`` and
        ``availability_date`` parsed from the application-meta block.

    Intended for verifying the new parser works on real CVs before
    wiring it into ``/ai/upload/`` (Phase 3 of the refactor). Once the
    new parser is the default, this endpoint stays as a dry-run probe
    (handy for debugging OCR / form-template edge cases).

    Request (multipart form-data):

        file             required — the CV file (PDF or DOCX)
        save_to_db       optional — "true" to also create User + CVSubmission

    Response 200::

        {
            "success": true,
            "extractor": "sakr_template",
            "confidence": 0.95,
            "data": { ... },
            "warnings": [],
            "file_name": "waiter.docx",
            "saved": true,                // only if save_to_db=true
            "user_id": 123,                // only if save_to_db=true
            "cv_submission_id": 456       // only if save_to_db=true
        }

    Response 400 (parse failure)::

        {
            "success": false,
            "error": "not_a_cv",
            "message": "This document does not look like a CV.",
            "file_name": "random.pdf",
            "warnings": []
        }

    Response 400 (save failure — parser succeeded but no email)::

        {
            "success": false,
            "error": "email_missing",
            "message": "Cannot save: the CV has no email address.",
            "data": { ... }   // parser output is still returned
        }

    Auth: ``IsAdmin`` only. The CV-upload endpoints (this and
    ``/ai/upload/``) are admin-only — only Admins can submit a
    seafarer CV. Other roles get HTTP 403. Unauthenticated requests
    get HTTP 401.

    (The project does not yet wire JWT/Token auth here; when it
    does, the same IsAdmin check will start enforcing for real.
    Until then, requests still get in as before but role check applies
    to authenticated sessions only.)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DocumentUploadSerializer

    def post(self, request, *args, **kwargs):
        upload_serializer = DocumentUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        file = upload_serializer.validated_data.get("file")

        if not file:
            return Response(
                {
                    "success": False,
                    "error": ErrorCode.FILE_MISSING.value,
                    "message": client_message(ErrorCode.FILE_MISSING),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # `save_to_db=true` (form field) toggles persistence. Default is
        # false so the endpoint stays a safe dry-run probe.
        save_to_db = str(request.data.get("save_to_db", "")).lower() == "true"

        # Save the file to a temp path so DocumentProcessor can read it
        # back. We always clean this up in the finally block.
        file_path = default_storage.save(
            f"tmp/{file.name}", ContentFile(file.read())
        )
        try:
            processor = DocumentProcessor()
            try:
                proc_result = processor.process_document(
                    default_storage.path(file_path)
                )
            except DocumentProcessingError as exc:
                logger.warning(
                    "ParseOnlyView: DocumentProcessor failed for %s: %s",
                    file.name, exc,
                )
                return Response(
                    {
                        "success": False,
                        "error": ErrorCode.FILE_UNSUPPORTED_FORMAT.value,
                        "message": str(exc),
                        "file_name": file.name,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            text = proc_result.get("extracted_text", "") or ""
            tables = proc_result.get("tables", []) or []
            ocr_meta = {
                "ocr_applied": bool(proc_result.get("ocr_applied")),
                "ocr_pages_processed": int(
                    proc_result.get("ocr_pages_processed") or 0
                ),
                "ocr_backend": proc_result.get("ocr_backend"),
            }

            extractor = SakrTemplateExtractor()
            result = extractor.extract(text, tables)

            if not result.ok:
                return Response(
                    {
                        "success": False,
                        "error": result.error.value if result.error else "internal_error",
                        "message": client_message(result.error) if result.error else client_message(ErrorCode.INTERNAL),
                        "file_name": file.name,
                        "warnings": list(result.warnings),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response_body = {
                "success": True,
                "extractor": result.extractor,
                "confidence": result.confidence,
                "data": result.data,
                "warnings": list(result.warnings),
                "file_name": file.name,
                "ocr": ocr_meta,
            }

            if save_to_db:
                try:
                    user_id, cv_submission_id, dropped_sea_service = _save_parser_output(
                        result.data,
                        file,
                        extracted_photo_path=proc_result.get("extracted_photo_path"),
                    )
                except _NoEmailError:
                    return Response(
                        {
                            "success": False,
                            "error": "email_missing",
                            "message": (
                                "Cannot save: the CV has no email address."
                            ),
                            "data": result.data,
                            "file_name": file.name,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                response_body["saved"] = True
                response_body["user_id"] = user_id
                response_body["cv_submission_id"] = cv_submission_id
                # Surface any sea-service records that were dropped
                # as overlapping duplicates. Frontend can show a
                # warning like "X records were ignored because they
                # overlap with longer records".
                if dropped_sea_service:
                    response_body["dropped_sea_service"] = dropped_sea_service
            else:
                response_body["saved"] = False

            return Response(response_body, status=status.HTTP_200_OK)
        except Exception:
            # Catch-all: never leak the exception text to the client.
            # The full traceback is in the server logs.
            logger.exception("ParseOnlyView: unexpected error")
            return Response(
                {
                    "success": False,
                    "error": ErrorCode.INTERNAL.value,
                    "message": client_message(ErrorCode.INTERNAL),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            # Always clean up the temp upload.
            try:
                default_storage.delete(file_path)
            except Exception:
                logger.warning(
                    "ParseOnlyView: failed to delete temp file %s", file_path
                )


# ── save-to-db helpers ──────────────────────────────────────────────────


class _NoEmailError(Exception):
    """Raised when the parser output has no email and the caller asked
    us to persist. Treated as a 400 (not a 500) by the view."""


# Accepted application_for_position choices, in the same order as
# the Users model. Kept here (not in models.py) so the parser doesn't
# import the model at module load time.
_VALID_APPLICATION_POSITIONS = {
    "Master / Captain", "Staff Captain", "Chief Officer / Chief Mate",
    "Second Officer", "Third Officer", "Dynamic Positioning Operator (DPO)",
    "ROV Supervisor", "Offshore Installation Manager", "Deck Cadet",
    "Bosun", "ABLE SEAFARER DECK", "Able Seaman (AB)",
    "Ordinary Seaman (OS)", "Carpenter", "Pumpman", "Crane Operator",
    "Water and Pool", "Security Guard", "Life Guard", "Upholsterer",
    "Doctor", "Hotel Director", "Assistant Hotel Director", "Purser",
    "Assistant Purser", "Food & Beverage Manager", "Executive Chef",
    "Chief Housekeeper", "Guest Services Manager", "Restaurant Manager",
    "Head Waiter", "Waiter", "F&B attendant", "Bartender", "Cabin Steward",
    "Laundryman", "Cook", "2nd Cook", "3rd Cook", "Assistant Cook",
    "Baker", "Assistant Baker", "Pastry", "Assistant pastry", "Butcher",
    "Steward", "Utility Galley", "Tour Expert", "Photographer",
    "Chief Engineer", "Second Engineer", "Third Engineer", "Fourth Engineer",
    "ETO", "2ND ETO", "3RD ETO", "ELECTRICAL ENGINEER",
    "Refrigeration Engineer", "HVAC Engineer", "Engine Cadet",
    "Gas Engineer", "Cargo Engineer", "Reliquefaction Engineer",
    "Able Seafarer Engine III/5", "Motorman", "Mechanic", "Oiler",
    "Wiper/Assistant Mechanic", "Fitter", "Welder", "Plumber",
    "Assistant Plumber", "Electrician", "2nd Electrician",
    "3rd Electrician", "Assistant Electrician", "Trainee Electrician",
    "AC Technician", "Senior Accommodation Repairman",
    "junior Accommodation Repairman", "Other",
}


def _parse_date_loose(raw: str):
    """Parse a date from common Sakr-form formats: ``DD/MM/YYYY``,
    ``DD.MM.YYYY``, ``DD-MM-YYYY``. Returns ``None`` on failure."""
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_salary_to_decimal(raw: str):
    """Parse a salary string like ``"730 $"`` or ``"1200 USD"`` into a
    Decimal. Returns ``None`` if no digits are found."""
    if not raw:
        return None
    digits = "".join(ch for ch in raw if ch.isdigit() or ch == ".")
    if not digits or digits == ".":
        return None
    try:
        return Decimal(digits)
    except InvalidOperation:
        return None


def _split_full_name(full_name: str) -> tuple[str, str]:
    """Split ``"MOHAMED SHEHATA RAMADAN ABDEL BASSET"`` into
    ``("MOHAMED", "SHEHATA RAMADAN ABDEL BASSET")`` (first + rest)."""
    parts = (full_name or "").strip().split(maxsplit=1)
    if not parts:
        return "", ""
    return parts[0], (parts[1] if len(parts) > 1 else "")


def _marital_status_to_string(ms: dict | str | None) -> str:
    """Convert the parser's marital-status dict to the Users model
    string value: ``"Single"`` or ``"Married"``."""
    if isinstance(ms, str):
        return ms
    if isinstance(ms, dict):
        if ms.get("married"):
            return "Married"
        if ms.get("single"):
            return "Single"
    return ""


def _sea_service_record_length_days(record: dict) -> int | None:
    """Return the length of a sea-service record in whole days, or
    None if either date is missing/unparseable.

    We treat a record with unparseable dates as "length unknown" so
    the dedup pass leaves it alone (records without dates can't
    participate in overlap detection).
    """
    start = _parse_date_loose(record.get("signed_on") or "")
    end = _parse_date_loose(record.get("signed_off") or "")
    if start is None or end is None:
        return None
    delta = (end - start).days
    # Negative deltas (off before on) are nonsensical — treat as unknown.
    return delta if delta >= 0 else None


def _records_overlap_half_open(a: dict, b: dict) -> bool:
    """Return True if two sea-service records overlap using the
    **half-open** rule: ``[start_a, end_a)`` intersects ``[start_b, end_b)``.

    Half-open means sign-on day = previous sign-off day is NOT
    considered overlap. That's the seafarer convention: a seafarer
    signs off one vessel and signs on the next on the same day.
    """
    start_a = _parse_date_loose(a.get("signed_on") or "")
    end_a = _parse_date_loose(a.get("signed_off") or "")
    start_b = _parse_date_loose(b.get("signed_on") or "")
    end_b = _parse_date_loose(b.get("signed_off") or "")
    if not all([start_a, end_a, start_b, end_b]):
        return False
    return start_a < end_b and start_b < end_a


def _dedupe_overlapping_sea_service(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Drop sea-service records that overlap with a longer record.

    Rules:
      * Overlap is detected using the **half-open** interval rule
        (sign-on day = previous sign-off day is fine, no overlap).
      * When two records overlap, the **longer** one is kept and the
        shorter is dropped. If they have the same length, the
        earlier-in-list (parser order) one is kept.
      * Records with unparseable dates are kept as-is and excluded
        from overlap detection (we can't reason about their
        placement in time).

    Returns:
        (kept_records, dropped_records)

        ``dropped_records`` is a list of dicts of shape::

            {
                "index": <original index in the input list>,
                "record": <the dropped record>,
                "kept_index": <index of the longer record that won>,
                "kept_record": <the longer record that won>,
                "reason": "overlap_with_longer_record",
            }
    """
    kept: list[dict] = []
    dropped: list[dict] = []
    for i, record in enumerate(records):
        length_i = _sea_service_record_length_days(record)
        # If we can't measure this record's length, just keep it
        # without checking for overlap (we have no fair way to
        # decide). Same if length is zero (sign-on == sign-off).
        if length_i is None or length_i == 0:
            kept.append(record)
            continue

        # Find any kept record that overlaps with this one and is
        # longer-or-equal in length. If we find one, drop the current
        # record. If we find one that is shorter, drop that one and
        # keep the current. If multiple kept records overlap, prefer
        # dropping the shortest (so the current record, presumably
        # longer, wins).
        overlap_target_idx = None
        overlap_target_length = None
        for j, kept_record in enumerate(kept):
            if not _records_overlap_half_open(record, kept_record):
                continue
            kept_length = _sea_service_record_length_days(kept_record)
            if kept_length is None:
                # Can't compare lengths — keep current record by
                # default (safer not to drop unknown records).
                continue
            if (overlap_target_length is None
                    or kept_length < overlap_target_length):
                overlap_target_idx = j
                overlap_target_length = kept_length

        if overlap_target_idx is None:
            # No overlap with any kept record — keep this one.
            kept.append(record)
            continue

        # We have an overlap. Decide who wins.
        if length_i > overlap_target_length:
            # Current record is longer — drop the shorter one in
            # `kept` and add the current.
            loser = kept.pop(overlap_target_idx)
            kept.append(record)
            dropped.append({
                "index": None,  # filled below
                "record": loser,
                "kept_index": len(kept) - 1,  # position after append
                "kept_record": record,
                "reason": "overlap_with_longer_record",
            })
        else:
            # Current record is shorter-or-equal — drop current.
            winner = kept[overlap_target_idx]
            dropped.append({
                "index": i,
                "record": record,
                "kept_index": overlap_target_idx,
                "kept_record": winner,
                "reason": "overlap_with_longer_record",
            })

    # Fill in the `index` field for records dropped from `kept` —
    # we don't have a stable original index for those, so use None
    # and let consumers rely on `record` itself for identification.
    for d in dropped:
        if d["index"] is None:
            d["index"] = None  # already None, but be explicit

    return kept, dropped


def _save_parser_output(data: dict, uploaded_file, extracted_photo_path: str | None = None) -> tuple[int, int, list[dict]]:
    """Create or update a Users row + create a CVSubmission from the
    parser output. Returns ``(user_id, cv_submission_id, dropped_sea_service)``.

    ``dropped_sea_service`` is a list of dicts describing any sea-service
    records that were filtered out as overlapping duplicates (see
    ``_dedupe_overlapping_sea_service`` for the shape). Callers
    surface this list in the response so the frontend can show the
    user what was filtered out.

    If ``extracted_photo_path`` is provided (the best portrait the
    ``DocumentProcessor`` pulled out of the source DOCX/PDF), it gets
    attached to the user as ``profile_image``. We never fail the save
    on a missing/broken photo — we just log and move on.

    Raises ``_NoEmailError`` if the contact section has no email (the
    Users model requires a unique, non-null email).

    All writes happen inside a single ``transaction.atomic`` so we
    never end up with a User without a CVSubmission (or vice versa).
    """
    from django.db import transaction
    from api.models import Users, CVSubmission

    personal = data.get("1_personal_details") or {}
    meta = data.get("0_application_meta") or {}
    contact = data.get("3_contact_details") or {}

    full_name = (personal.get("full_name") or "").strip()
    first_name, middle_name = _split_full_name(full_name)
    email = (contact.get("e_mail") or "").strip().lower()
    if not email:
        raise _NoEmailError("parser output has no email")

    marital_str = _marital_status_to_string(personal.get("marital_status"))

    # Application position: only set if it matches a known choice; else
    # leave blank so the user can pick manually later. The raw text
    # goes to ``other_position`` regardless.
    application_pos = (meta.get("application_for_position_as") or "").strip()
    if application_pos not in _VALID_APPLICATION_POSITIONS:
        application_pos = ""

    user_defaults = {
        "first_name": first_name,
        "middle_name": middle_name,
        "marital_status": marital_str or "Single",
        "nationality": (personal.get("nationality") or "").strip() or None,
        "Place_Of_Birth": (personal.get("place_of_birth") or "").strip() or None,
        "Nearest_Port": (personal.get("nearest_port") or "").strip() or None,
        "Height_Cm": personal.get("height_cm") or None,
        "Weight_Kg": personal.get("weight_kg") or None,
        "date_of_birth": _parse_date_loose(personal.get("date_of_birth") or ""),
        "register_code": (meta.get("register_code") or "").strip() or None,
        "register_date": _parse_date_loose(meta.get("register_date") or ""),
        "application_for_position": application_pos or None,
        "other_position": (meta.get("other_position") or "").strip() or None,
        "address": (contact.get("home_address_city") or "").strip() or None,
        # phone_number is NOT NULL in the DB; fall back to "" if the CV
        # didn't provide one.
        "phone_number": (contact.get("mobile_tel") or "").strip() or "",
    }

    # Per spec, Admin-uploaded seafarers default to the "Employee" role.
    # The seafarer can later be flipped to "Crew" by an admin.
    user_defaults["role"] = "Employee"

    # Phone-verification gate. New seafarers start NOT verified; the
    # initial OTP is sent via the configured EmailService to the
    # user's email right after the user is saved (see below). The
    # seafarer must hit /api/auth/verify-otp/ before
    # /api/auth/phone-login/ will accept them.
    user_defaults["is_phone_verified"] = False

    # The seafarer's password IS their phone number (per spec). This
    # means: as soon as the User is created, the seafarer can log in
    # at POST /api/auth/phone-login/ using {phone, phone} — no separate
    # password, no email to remember.
    #
    # If the CV has no phone, fall back to the email-as-password (the
    # existing email-login flow will still work in that case).
    seafarer_phone = user_defaults.get("phone_number") or ""
    seafarer_password = seafarer_phone or email

    expected_salary_dec = _parse_salary_to_decimal(meta.get("expected_salary") or "")
    available_date = _parse_date_loose(meta.get("available_date") or "")

    with transaction.atomic():
        user, _created = Users.objects.get_or_create(
            email=email,
            defaults=user_defaults,
        )
        # If the user already existed, refresh the fields we know about
        # (cheap idempotent save). The applicant may have been updated
        # in the source-of-truth CV.
        for field, value in user_defaults.items():
            if value not in (None, ""):
                setattr(user, field, value)
        # Set the password. Django's set_password() hashes properly.
        # We always set it (even on update) so the seafarer's phone-as-
        # password stays in sync if the CV has a new phone number.
        user.set_password(seafarer_password)
        user.save()

        # Attach the extracted portrait photo to the user. We do this
        # inside the same transaction so the photo is rolled back
        # together with the User if anything later in this block fails.
        # A missing/broken photo is never fatal — we just log and
        # continue with profile_image = the existing value (or None).
        if extracted_photo_path and os.path.isfile(extracted_photo_path):
            try:
                with open(extracted_photo_path, "rb") as photo_file:
                    photo_name = f"user_{user.id}_{os.path.basename(extracted_photo_path)}"
                    user.profile_image.save(
                        photo_name,
                        ContentFile(photo_file.read()),
                        save=False,
                    )
                user.save(update_fields=["profile_image"])
                logger.info(
                    "_save_parser_output: saved profile_image for user id=%s from %s",
                    user.id, extracted_photo_path,
                )
            except Exception:
                logger.exception(
                    "_save_parser_output: failed to save profile_image for user id=%s",
                    user.id,
                )
        elif extracted_photo_path:
            logger.warning(
                "_save_parser_output: extracted_photo_path %s does not exist; "
                "skipping profile_image save",
                extracted_photo_path,
            )

        # Persist the rest of the parsed data (travel docs, qualifications,
        # NOK, health certs, marine courses, sea service) to the related
        # models. The Sakr parser returns keys like "4_travel_documents"
        # and "6_next_of_kin_emergency_contact" — the API serializer
        # expects the short names. Map and delegate to the existing
        # SeafarerApplicationSerializer.update() which handles all the
        # FKs (PersonalDocument, NextOfKin, Vaccination, Course,
        # SeaService, etc.).
        sea_service = data.get("9_complete_sea_service_details") or {}
        # Sakr uses "vessel_name_imo"; the serializer expects
        # "vessel_name_imo_number" (it splits on "/" to separate the
        # vessel name from the IMO). Rename so the split works.
        for record in sea_service.get("service_records", []):
            if "vessel_name_imo" in record and "vessel_name_imo_number" not in record:
                record["vessel_name_imo_number"] = record.pop("vessel_name_imo")

        # Drop overlapping sea-service records before saving. Two
        # records that overlap in time are usually a parsing artifact
        # (the seafarer can't physically be on two vessels at once).
        # We keep the longer of the two and drop the shorter; if
        # equal length, the earlier-in-list one wins. The dropped
        # records are returned to the caller so the response can
        # surface them to the admin.
        original_records = sea_service.get("service_records", []) or []
        if original_records:
            kept_records, dropped_records = _dedupe_overlapping_sea_service(
                original_records
            )
            sea_service["service_records"] = kept_records
        else:
            dropped_records = []

        api_payload = {
            "personal_details":        data.get("1_personal_details") or {},
            "contact_details":         data.get("3_contact_details") or {},
            "travel_documents":        data.get("4_travel_documents") or [],
            "professional_qualification": data.get("5_professional_qualification_certificate_of_competency") or [],
            "next_of_kin":             data.get("6_next_of_kin_emergency_contact") or {},
            "health_certificates":     data.get("7_health_certificates_and_vaccinations") or {},
            "marine_courses":          data.get("8_marine_courses") or [],
            "sea_service_details":     sea_service,
            "references":              data.get("10_references") or [],
            "declaration":             data.get("11_declaration") or {},
            "for_office_use_only":     data.get("12_for_office_use_only") or {},
        }
        from api.seafarer_application_serializers import SeafarerApplicationSerializer
        SeafarerApplicationSerializer().update(user, api_payload)

        cv_submission = CVSubmission.objects.create(
            user=user,
            cv_file=uploaded_file,
            expected_salary=expected_salary_dec,
            availability_date=available_date,
            status="Pending",
        )

    # After the transaction commits: send the initial OTP to the
    # seafarer's EMAIL (not their phone) via the configured email
    # service. The admin never sees the OTP in the API response —
    # only the email service does. The seafarer still enters their
    # PHONE at /api/auth/verify-otp/ (which is what we use to look
    # the user up); the OTP itself is delivered to the email address
    # on file from the CV. If the user has no email, skip the email
    # (the seafarer can still log in via /api/login/ with email +
    # email-as-password fallback).
    if user.email:
        try:
            from api.email import (
                generate_otp, get_email_service, otp_default_ttl_minutes,
            )
            from django.utils import timezone

            otp = generate_otp()
            ttl = otp_default_ttl_minutes()
            # Persist the OTP on the user row. NOTE: this is OUTSIDE
            # the transaction above — if the email dispatch fails,
            # the OTP is still on the user. Seafarer can also
            # re-request via /api/auth/request-otp/ which regenerates.
            user.otp_code = otp
            user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=ttl)
            user.save(update_fields=["otp_code", "otp_expires_at"])

            try:
                get_email_service().send_otp_email(
                    user.email, otp, ttl_minutes=ttl
                )
            except Exception:
                logger.exception(
                    "_save_parser_output: email dispatch failed for user id=%s",
                    user.id,
                )
        except Exception:
            # OTP-generation failure must not block the save — the
            # seafarer is still on the system; they can re-request.
            logger.exception("_save_parser_output: failed to send initial OTP")

    return user.id, cv_submission.id, dropped_records
