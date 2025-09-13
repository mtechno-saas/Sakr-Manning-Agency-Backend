from django.shortcuts import render

# Create your views here.
# doc_parser/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ParsedDocument
from .serializers import ParsedDocumentSerializer
from .ai_parser_service import extract_document_features

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
            # 1. Extract data from the uploaded document using the AI service
            extracted_yaml = extract_document_features(instance.source_file.path)
            if not extracted_yaml:
                instance.status = 'FAILED'
                instance.save()
                return Response(
                    {"error": "Could not extract data from the document."},
                    status=status.HTTP_400_BAD_REQUEST
                )


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
