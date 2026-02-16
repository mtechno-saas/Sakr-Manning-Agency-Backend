from rest_framework import viewsets, parsers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Course
from .serializers import CourseSerializer

# 1. The main ViewSet for API actions
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

# 2. The separate function for Downloading
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_course_document(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    
    if not course.document:
        return Response({"error": "No document found"}, status=404)

    file_handle = course.document.open()
    response = FileResponse(file_handle, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{course.course_name}.pdf"'
    return response