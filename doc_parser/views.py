from django.shortcuts import render

# Create your views here.
# doc_parser/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ParsedDocument
from .serializers import ParsedDocumentSerializer
from .ai_parser_service import read_docx_text, extract_data_from_document

class DocumentUploadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for uploading seafarer application forms for AI parsing.
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
        instance.save()

        try:
            # --- AI Processing Step ---
            # 1. Read the text from the uploaded .docx file
            document_text = read_docx_text(instance.source_file.path)
            if not document_text:
                instance.status = 'FAILED'
                instance.save()
                return Response(
                    {"error": "Could not read text from the document."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Send the text to the AI service for extraction
            extracted_yaml = extract_data_from_document(document_text)

            # 3. Save the result and update the status
            instance.extracted_data_yaml = extracted_yaml
            instance.status = 'COMPLETED'
            instance.save()

            # Return the successful response with the extracted data
            headers = self.get_success_headers(serializer.data)
            return Response(
                self.get_serializer(instance).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        except Exception as e:
            # Handle any errors during AI processing
            instance.status = 'FAILED'
            instance.save()
            return Response(
                {"error": f"An error occurred during AI processing: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
