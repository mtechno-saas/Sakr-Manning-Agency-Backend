



# # documents/views.py
# import re
# from collections import Counter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from .document_to_json import convert_text_to_json


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
#     Upload a document (PDF or DOCX) and return structured JSON + metadata.
#     """

#     def post(self, request, *args, **kwargs):
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

#             # Step 2: Convert text into structured JSON using LangChain + Ollama
#             structured_json = convert_text_to_json(cleaned_text)

#             # Clean up file after processing
#             default_storage.delete(file_path)

#             return Response({
#                 "file_name": file.name,
#                 "structured_data": structured_json,
#                 "page_count": result.get("page_count"),
#                 "word_count": len(cleaned_text.split()),
#             }, status=status.HTTP_200_OK)

#         except DocumentProcessingError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)









import re
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .document_processor import DocumentProcessor, DocumentProcessingError
from .document_to_json import convert_text_to_json
from .models import Applicant


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
            continue  # skip repeating headers/footers

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
    save into Applicant table, and return the response.
    """

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Save file temporarily
        file_path = default_storage.save(f"tmp/{file.name}", ContentFile(file.read()))

        processor = DocumentProcessor()
        try:
            result = processor.process_document(default_storage.path(file_path))

            # Step 1: Clean extracted text
            cleaned_text = clean_text(result.get("extracted_text", ""))

            # Step 2: Convert text into structured JSON using LangChain + Ollama
            structured_json = convert_text_to_json(cleaned_text)

            # Step 3: Save structured data into Applicant model
            applicant = Applicant.objects.create(
                personal_details = structured_json.get("Personal_Details", {}),
                education = structured_json.get("Education", {}),
                contact_details = structured_json.get("Contact_Details", {}),
                travel_documents = structured_json.get("Travel_Documents", {}),
                professional_qualifications = structured_json.get("Professional_Qualifications", {}),
                next_of_kin_emergency_contact = structured_json.get("Next_of_Kin_Emergency_Contact", {}),
                health_certificates_vaccinations = structured_json.get("Health_Certificates_Vaccinations", {}),
                covid_19_vaccination = structured_json.get("Covid_19_Vaccination", {}),
                marine_courses = structured_json.get("Marine_Courses", {}),
                sea_service_details = structured_json.get("Sea_Service_Details", {}),
                specialised_experience = structured_json.get("Specialised_Experience", {}),
                references = structured_json.get("References", {}),
                declaration = structured_json.get("Declaration", {}),
                office_use_only = structured_json.get("Office_Use_Only", {}),
            )

            # Clean up file after processing
            default_storage.delete(file_path)

            return Response({
                "message": "Data saved successfully",
                "applicant_id": applicant.id,
                "file_name": file.name,
                "structured_data": structured_json,
                "page_count": result.get("page_count"),
                "word_count": len(cleaned_text.split()),
            }, status=status.HTTP_200_OK)

        except DocumentProcessingError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
