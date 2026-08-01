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
        # Allow an admin/HR/Recruiter creating a course on behalf of a
        # crew member: honour `user` in the payload OR `?user=` query
        # param (the frontend courseService sends both). Without this
        # override, every Course the admin creates is silently owned by
        # the admin themselves and the crew member's profile never sees
        # it — same bug pattern we fixed for SeaService and the travel-
        # documents/forms previously.
        user_id = (
            self.request.data.get("user")
            or self.request.query_params.get("user")
        )
        if user_id:
            try:
                serializer.save(user_id=int(user_id))
            except (TypeError, ValueError):
                serializer.save(user=self.request.user)
        else:
            serializer.save(user=self.request.user)

    def get_queryset(self):
        # Mirrors perform_create: honour `?user=` so an admin/HR/Recruiter
        # can list the courses of a specific crew member. Falls back to
        # "own courses" for an employee that does not supply ?user=.
        user_id = self.request.query_params.get("user")
        if user_id:
            try:
                return Course.objects.filter(user_id=int(user_id))
            except (TypeError, ValueError):
                pass
        return Course.objects.filter(user=self.request.user)

# 2. The separate function for Downloading
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_course_document(request, course_id):
    # Allow admin/HR/Recruiter to download any course's document; an
    # employee can only download their own.
    qs = Course.objects.filter(id=course_id)
    if request.user.role not in ("Admin", "HR Manager", "Recruiter"):
        qs = qs.filter(user=request.user)
    course = get_object_or_404(qs)

    if not course.document:
        return Response({"error": "No document found"}, status=404)

    file_handle = course.document.open()
    response = FileResponse(file_handle, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{course.course_name}.pdf"'
    return response