# from django.shortcuts import render

# # Create your views here.
# """
# Django REST Framework views for document management.
# Handles file uploads, processing, and retrieval operations.
# """

# from rest_framework import viewsets, status, permissions
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from django.http import Http404, HttpResponse
# from django.db.models import Q
# from django.core.exceptions import ValidationError
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
# import os
# import logging
# from datetime import datetime

# from .models import Document
# from .serializers import (
#     DocumentUploadSerializer,
#     DocumentDetailSerializer,
#     DocumentListSerializer,
#     DocumentProcessingSerializer,
#     DocumentSearchSerializer
# )
# from .document_processor import DocumentProcessor, DocumentProcessingError


# logger = logging.getLogger(__name__)


# class DocumentViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for managing documents.
#     Provides CRUD operations and additional actions for document processing.
#     """
    
#     queryset = Document.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]
    
#     def get_serializer_class(self):
#         """
#         Return appropriate serializer based on action.
#         """
#         if self.action == 'create':
#             return DocumentUploadSerializer
#         elif self.action == 'list':
#             return DocumentListSerializer
#         elif self.action in ['retrieve', 'update', 'partial_update']:
#             return DocumentDetailSerializer
#         elif self.action == 'search':
#             return DocumentSearchSerializer
#         else:
#             return DocumentDetailSerializer
    
#     def perform_create(self, serializer):
#         """
#         Handle document creation and trigger processing.
#         """
#         document = serializer.save()
        
#         # Trigger document processing asynchronously
#         self._process_document_async(document)
        
#         logger.info(f"Document uploaded: {document.title} (ID: {document.id})")
    
#     def _process_document_async(self, document):
#         """
#         Process document asynchronously.
#         In production, this should use Celery or similar task queue.
#         """
#         try:
#             # Update status to processing
#             document.status = 'processing'
#             document.save()
            
#             # Process the document
#             processor = DocumentProcessor()
#             file_path = document.file.path
            
#             result = processor.process_document(file_path, document.document_type)
            
#             # Update document with processing results
#             document.extracted_text = result.get('extracted_text', '')
#             document.page_count = result.get('page_count')
#             document.word_count = result.get('word_count', 0)
#             document.status = 'completed'
#             document.processing_error = None
#             document.save()
            
#             logger.info(f"Document processed successfully: {document.title}")
            
#         except DocumentProcessingError as e:
#             # Handle processing errors
#             document.status = 'failed'
#             document.processing_error = str(e)
#             document.save()
            
#             logger.error(f"Document processing failed: {document.title} - {str(e)}")
        
#         except Exception as e:
#             # Handle unexpected errors
#             document.status = 'failed'
#             document.processing_error = f"Unexpected error: {str(e)}"
#             document.save()
            
#             logger.error(f"Unexpected error processing document: {document.title} - {str(e)}")
    
#     @action(detail=True, methods=['post'])
#     def reprocess(self, request, pk=None):
#         """
#         Reprocess a document.
#         Useful when processing failed or needs to be updated.
#         """
#         document = self.get_object()
        
#         if not os.path.exists(document.file.path):
#             return Response(
#                 {'error': 'Document file not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         # Reset processing status
#         document.status = 'pending'
#         document.processing_error = None
#         document.save()
        
#         # Trigger reprocessing
#         self._process_document_async(document)
        
#         return Response(
#             {'message': 'Document reprocessing started'},
#             status=status.HTTP_202_ACCEPTED
#         )
    
#     @action(detail=True, methods=['get'])
#     def download(self, request, pk=None):
#         """
#         Download the original document file.
#         """
#         document = self.get_object()
        
#         if not document.file or not os.path.exists(document.file.path):
#             return Response(
#                 {'error': 'Document file not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         try:
#             with open(document.file.path, 'rb') as file:
#                 response = HttpResponse(
#                     file.read(),
#                     content_type='application/octet-stream'
#                 )
#                 response['Content-Disposition'] = f'attachment; filename="{document.file.name}"'
#                 return response
        
#         except Exception as e:
#             logger.error(f"Error downloading document {pk}: {str(e)}")
#             return Response(
#                 {'error': 'Failed to download document'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     @action(detail=True, methods=['get'])
#     def text(self, request, pk=None):
#         """
#         Get extracted text content from the document.
#         """
#         document = self.get_object()
        
#         if document.status != 'completed':
#             return Response(
#                 {
#                     'error': 'Document not processed yet',
#                     'status': document.status,
#                     'processing_error': document.processing_error
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         return Response({
#             'document_id': document.id,
#             'title': document.title,
#             'extracted_text': document.extracted_text,
#             'word_count': document.word_count,
#             'page_count': document.page_count
#         })
    
#     @action(detail=False, methods=['get'])
#     def search(self, request):
#         """
#         Search documents based on various criteria.
#         """
#         serializer = DocumentSearchSerializer(data=request.query_params)
#         serializer.is_valid(raise_exception=True)
        
#         queryset = self.get_queryset()
        
#         # Apply filters
#         query = serializer.validated_data.get('query')
#         if query:
#             queryset = queryset.filter(
#                 Q(title__icontains=query) |
#                 Q(description__icontains=query) |
#                 Q(extracted_text__icontains=query)
#             )
        
#         document_type = serializer.validated_data.get('document_type')
#         if document_type:
#             queryset = queryset.filter(document_type=document_type)
        
#         status_filter = serializer.validated_data.get('status')
#         if status_filter:
#             queryset = queryset.filter(status=status_filter)
        
#         date_from = serializer.validated_data.get('date_from')
#         if date_from:
#             queryset = queryset.filter(created_at__date__gte=date_from)
        
#         date_to = serializer.validated_data.get('date_to')
#         if date_to:
#             queryset = queryset.filter(created_at__date__lte=date_to)
        
#         # Paginate results
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = DocumentListSerializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
        
#         serializer = DocumentListSerializer(queryset, many=True)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['get'])
#     @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
#     def stats(self, request):
#         """
#         Get statistics about documents.
#         """
#         queryset = self.get_queryset()
        
#         stats = {
#             'total_documents': queryset.count(),
#             'by_type': {
#                 'pdf': queryset.filter(document_type='pdf').count(),
#                 'docx': queryset.filter(document_type='docx').count(),
#             },
#             'by_status': {
#                 'pending': queryset.filter(status='pending').count(),
#                 'processing': queryset.filter(status='processing').count(),
#                 'completed': queryset.filter(status='completed').count(),
#                 'failed': queryset.filter(status='failed').count(),
#             },
#             'total_pages': queryset.aggregate(
#                 total=models.Sum('page_count')
#             )['total'] or 0,
#             'total_words': queryset.aggregate(
#                 total=models.Sum('word_count')
#             )['total'] or 0,
#         }
        
#         return Response(stats)
    
#     @action(detail=False, methods=['post'])
#     def bulk_upload(self, request):
#         """
#         Handle bulk document upload.
#         """
#         files = request.FILES.getlist('files')
#         if not files:
#             return Response(
#                 {'error': 'No files provided'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         results = []
#         errors = []
        
#         for file in files:
#             try:
#                 # Create document data
#                 document_data = {
#                     'title': file.name,
#                     'file': file
#                 }
                
#                 serializer = DocumentUploadSerializer(data=document_data)
#                 if serializer.is_valid():
#                     document = serializer.save()
#                     self._process_document_async(document)
                    
#                     results.append({
#                         'id': document.id,
#                         'title': document.title,
#                         'status': 'uploaded'
#                     })
#                 else:
#                     errors.append({
#                         'file': file.name,
#                         'errors': serializer.errors
#                     })
            
#             except Exception as e:
#                 errors.append({
#                     'file': file.name,
#                     'error': str(e)
#                 })
        
#         return Response({
#             'uploaded': len(results),
#             'failed': len(errors),
#             'results': results,
#             'errors': errors
#         }, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED)


# # Additional utility views
# from rest_framework.views import APIView


# class DocumentProcessorStatusView(APIView):
#     """
#     View to check the status of document processing capabilities.
#     """
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get(self, request):
#         """
#         Get information about document processing capabilities.
#         """
#         processor = DocumentProcessor()
        
#         return Response({
#             'supported_formats': processor.supported_formats,
#             'pdf_available': 'pdf' in processor.supported_formats,
#             'docx_available': 'docx' in processor.supported_formats,
#             'timestamp': datetime.now().isoformat()
#         })


# class DocumentHealthCheckView(APIView):
#     """
#     Health check view for document processing system.
#     """
#     permission_classes = []  # Public endpoint
    
#     def get(self, request):
#         """
#         Perform health check on document processing system.
#         """
#         try:
#             # Check database connectivity
#             document_count = Document.objects.count()
            
#             # Check document processor
#             processor = DocumentProcessor()
            
#             return Response({
#                 'status': 'healthy',
#                 'document_count': document_count,
#                 'supported_formats': processor.supported_formats,
#                 'timestamp': datetime.now().isoformat()
#             })
        
#         except Exception as e:
#             return Response({
#                 'status': 'unhealthy',
#                 'error': str(e),
#                 'timestamp': datetime.now().isoformat()
#             }, status=status.HTTP_503_SERVICE_UNAVAILABLE)



# # documents/views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError






# class DocumentUploadView(APIView):
#     """
#     Upload a document (PDF or DOCX) and return extracted text + metadata.
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

#             # Clean up file after processing
#             default_storage.delete(file_path)

#             return Response({
#                 "file_name": file.name,
#                 "extracted_text": result.get("extracted_text"),
#                 "page_count": result.get("page_count"),
#                 "word_count": result.get("word_count"),
#             }, status=status.HTTP_200_OK)

#         except DocumentProcessingError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)






# def clean_text(text: str) -> str:
#     """
#     Clean extracted text:
#     - Remove duplicate lines
#     - Remove repeated inline table values (e.g., 'Name | John | John | John')
#     - Collapse multiple spaces
#     - Remove excessive headers/footers repetition
#     """
#     seen = set()
#     cleaned_lines = []

#     for line in text.splitlines():
#         line = line.strip()
#         if not line:
#             continue

#         # Collapse repeated tokens in tables (split by | or multiple spaces)
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|")]
#             unique_parts = []
#             for p in parts:
#                 if not unique_parts or p != unique_parts[-1]:
#                     unique_parts.append(p)
#             line = " | ".join(unique_parts)

#         # Collapse long sequences of repeated words
#         line = re.sub(r'\b(\w+)( \1){2,}\b', r'\1', line)

#         # Skip if already seen
#         if line not in seen:
#             seen.add(line)
#             cleaned_lines.append(line)

#     return "\n".join(cleaned_lines)



# # documents/views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .document_processor import DocumentProcessor, DocumentProcessingError
# from collections import Counter

# import re





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
#     Upload a document (PDF or DOCX) and return extracted text + metadata.
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

#             # Clean extracted text to remove redundancy
#             cleaned_text = clean_text(result.get("extracted_text", ""))

#             # Clean up file after processing
#             default_storage.delete(file_path)

#             return Response({
#                 "file_name": file.name,
#                 "extracted_text": cleaned_text,
#                 "page_count": result.get("page_count"),
#                 "word_count": len(cleaned_text.split()),
#             }, status=status.HTTP_200_OK)

#         except DocumentProcessingError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





# documents/views.py
import re
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .document_processor import DocumentProcessor, DocumentProcessingError
from .document_to_json import convert_text_to_json


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
    Upload a document (PDF or DOCX) and return structured JSON + metadata.
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

            # Clean up file after processing
            default_storage.delete(file_path)

            return Response({
                "file_name": file.name,
                "structured_data": structured_json,
                "page_count": result.get("page_count"),
                "word_count": len(cleaned_text.split()),
            }, status=status.HTTP_200_OK)

        except DocumentProcessingError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
