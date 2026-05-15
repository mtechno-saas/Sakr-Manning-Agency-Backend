










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
import logging
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
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


class DocumentUploadView(APIView):
    """
    Upload a document (PDF or DOCX), extract text, convert to structured JSON,
    save into both Applicant table and Users table, and return the response.
    
    Uses serializers for validation and response formatting.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DocumentUploadSerializer

    def post(self, request, *args, **kwargs):
        """Handle document upload with proper serializer validation."""
        try:
            # Validate file upload using serializer
            upload_serializer = DocumentUploadSerializer(data=request.data)
            if not upload_serializer.is_valid():
                return Response(
                    upload_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            file = upload_serializer.validated_data.get('file')
            
            # File is required for AI processing
            if not file:
                return Response(
                    {"file": ["A file is required for AI document processing."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save file temporarily
            file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

            processor = DocumentProcessor()
            try:
                with transaction.atomic():
                    # Step 1: Extract text from document
                    result = processor.process_document(default_storage.path(file_path))

                    # Step 2: Clean extracted text
                    cleaned_text = clean_text(result.get("extracted_text", ""))

                    # Step 3: Convert text into structured JSON
                    structured_json = convert_text_to_json(cleaned_text)

                    # Ensure structured_json is a dictionary
                    if not isinstance(structured_json, dict):
                        logger.error(f"convert_text_to_json returned {type(structured_json)}, expected dict")
                        structured_json = {
                            "Personal_Details": {},
                            "Education": {},
                            "Contact_Details": {},
                            "Travel_Documents": {},
                            "Professional_Qualifications": {},
                            "Next_of_Kin_Emergency_Contact": {},
                            "Health_Certificates_Vaccinations": {},
                            "Covid_19_Vaccination": {},
                            "Marine_Courses": {},
                            "Sea_Service_Details": {},
                            "Specialised_Experience": {},
                            "References": {},
                            "Declaration": {},
                            "Office_Use_Only": {},
                            "Physical_Measurements": {},
                            "Language_Skills": {},
                            "Medical_History": {},
                            "Assessments": {},
                            "Competency_Tests": {},
                            "Applied_Position_Info": {},
                            "error": f"Unexpected return type: {type(structured_json)}"
                        }

                    # VALIDATION CHECK: If document is not a valid maritime CV, do NOT save to database
                    if "validation_error" in structured_json:
                        # Clean up the temporary file
                        try:
                            default_storage.delete(file_path)
                        except Exception as e:
                            logger.warning(f"Failed to delete temporary file: {e}")
                        
                        # Return error response without saving anything
                        return Response({
                            "success": False,
                            "error": "Invalid document",
                            "message": structured_json.get("validation_error", "Document is not a valid maritime CV"),
                            "file_name": file.name,
                            "structured_data": structured_json,
                            "page_count": result.get("page_count"),
                            "word_count": len(cleaned_text.split()),
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Step 4: Save structured data into Applicant model
                    applicant = Applicant.objects.create(
                        personal_details=structured_json.get("Personal_Details", {}),
                        education=structured_json.get("Education", {}),
                        contact_details=structured_json.get("Contact_Details", {}),
                        travel_documents=structured_json.get("Travel_Documents", {}),
                        professional_qualifications=structured_json.get("Professional_Qualifications", {}),
                        next_of_kin_emergency_contact=structured_json.get("Next_of_Kin_Emergency_Contact", {}),
                        health_certificates_vaccinations=structured_json.get("Health_Certificates_Vaccinations", {}),
                        covid_19_vaccination=structured_json.get("Covid_19_Vaccination", {}),
                        marine_courses=structured_json.get("Marine_Courses", {}),
                        sea_service_details=structured_json.get("Sea_Service_Details", {}),
                        specialised_experience=structured_json.get("Specialised_Experience", {}),
                        references=structured_json.get("References", {}),
                        declaration=structured_json.get("Declaration", {}),
                        office_use_only=structured_json.get("Office_Use_Only", {}),
                        physical_measurements=structured_json.get("Physical_Measurements", {}),
                        language_skills=structured_json.get("Language_Skills", {}),
                        medical_history=structured_json.get("Medical_History", {}),
                        assessments=structured_json.get("Assessments", {}),
                        competency_tests=structured_json.get("Competency_Tests", {}),
                        applied_position_info=structured_json.get("Applied_Position_Info", {}),
                    )

                    logger.info(f"Successfully created applicant with ID: {applicant.id}")

                    # Use serializer BEFORE user creation
                    applicant_serializer = ApplicantToUsersSerializer(applicant)

                    # Step 5: Convert and save to Users model
                    user = None
                    user_error = None
                    try:
                        logger.info("Converting applicant to Users model")
                        
                        # FIXED: Create user with proper type and date handling
                        from api.models import Users
                        from django.db import models
                        from datetime import datetime
                        
                        serializer_data = applicant_serializer.data

                        email = serializer_data.get('email')
                        if not email:
                            raise ValueError(['Email is required'])
                        
                        def convert_date(date_str):
                            """Convert various date formats to YYYY-MM-DD."""
                            if not date_str or not str(date_str).strip():
                                return None
                            
                            date_str = str(date_str).strip()
                            
                            # Try different date formats
                            formats = [
                                '%d/%m/%Y',  # 18/6/1994
                                '%d-%m-%Y',  # 18-6-1994
                                '%Y-%m-%d',  # 1994-06-18 (already correct)
                                '%d/%m/%y',  # 18/6/94
                                '%d-%m-%y',  # 18-6-94
                                '%Y/%m/%d',  # 1994/6/18
                            ]
                            
                            for fmt in formats:
                                try:
                                    dt = datetime.strptime(date_str, fmt)
                                    return dt.strftime('%Y-%m-%d')
                                except ValueError:
                                    continue
                            
                            # If no format works, return None
                            logger.warning(f"Could not parse date: {date_str}")
                            return None
                        
                        # Get all fields from Users model with their types
                        user_model_fields = {f.name: f for f in Users._meta.get_fields()}
                        
                        # Build defaults dict with proper type handling
                        defaults = {}
                        for field_name, value in serializer_data.items():
                            # Skip special fields
                            if field_name in ['id', 'email', 'created_at', 'updated_at', 'ranks', 'certificates', 'references', 'sea_services']:
                                continue
                            
                            # Only process if field exists in Users model
                            if field_name not in user_model_fields:
                                continue
                            
                            field = user_model_fields[field_name]
                            
                            # Handle different field types
                            if isinstance(field, (models.DateField, models.DateTimeField)):
                                # Date fields: convert format
                                defaults[field_name] = convert_date(value)
                            elif isinstance(field, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField)):
                                # Integer fields: use None if empty
                                try:
                                    defaults[field_name] = int(value) if value and str(value).strip() else None
                                except (ValueError, TypeError):
                                    defaults[field_name] = None
                            elif isinstance(field, (models.FloatField, models.DecimalField)):
                                # Float/Decimal fields: use None if empty
                                try:
                                    defaults[field_name] = float(value) if value and str(value).strip() else None
                                except (ValueError, TypeError):
                                    defaults[field_name] = None
                            elif isinstance(field, models.BooleanField):
                                # Boolean fields: use False if empty
                                defaults[field_name] = bool(value) if value else False
                            elif isinstance(field, models.JSONField):
                                # JSON fields: use empty dict/list if empty
                                defaults[field_name] = value if value else {}
                            else:
                                # String fields and others: use empty string if empty
                                defaults[field_name] = value if value else ''
                        
                        user, created = Users.objects.update_or_create(
                            email=email,
                            defaults=defaults
                        )
                        
                        action = "Created" if created else "Updated"
                        logger.info(f"{action} user: {user.email} (ID: {user.id})")
                        
                    except Exception as ue:
                        user_error = f"User creation error: {str(ue)}"
                        logger.error(f"Failed to create user: {ue}")
                        import traceback
                        logger.error(traceback.format_exc())

                    # Clean up file
                    try:
                        default_storage.delete(file_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete temporary file: {e}")

                    # Response with serialized applicant data
                    response_status = status.HTTP_201_CREATED
                    message = "Data saved successfully to both databases"

                    if "error" in structured_json:
                        response_status = status.HTTP_206_PARTIAL_CONTENT
                        message = "Data saved with parsing issues"

                    if not user:
                        response_status = status.HTTP_206_PARTIAL_CONTENT
                        message = "Data saved to Applicant database, but failed to save to Users database"

                    # applicant_serializer already created above
                    
                    return Response({
                        "success": True,
                        "message": message,
                        "applicant_id": applicant.id,
                        "user_id": user.id if user else None,
                        "user_email": user.email if user else None,
                        "file_name": file.name,
                        "applicant_data": applicant_serializer.data,
                        "structured_data": structured_json,
                        "page_count": result.get("page_count"),
                        "word_count": len(cleaned_text.split()),
                        "parsing_quality": "low" if "error" in structured_json else "high",
                        "user_creation_status": "success" if user else "failed",
                        "user_error": user_error,
                    }, status=response_status)

            except DocumentProcessingError as e:
                try:
                    default_storage.delete(file_path)
                except Exception:
                    pass
                return Response({
                    "success": False,
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                try:
                    default_storage.delete(file_path)
                except Exception:
                    pass
                logger.error(f"Unexpected error during processing: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return Response({
                    "success": False,
                    "error": "Internal server error during document processing",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Unexpected error in document upload: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                "success": False,
                "error": "Internal server error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
