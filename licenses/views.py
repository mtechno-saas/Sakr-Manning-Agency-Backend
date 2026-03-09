from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework import viewsets
from .models import UserLicense
from .serializers import UserLicenseSerializer
from rest_framework.permissions import IsAuthenticated
import os

class UserLicenseViewSet(viewsets.ModelViewSet):
    serializer_class = UserLicenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return UserLicense.objects.filter(user_id=user_id)
        return UserLicense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        if user_id:
            serializer.save(user_id=user_id)
        else:
            serializer.save(user=self.request.user)

    # Add this custom action
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        license = self.get_object()
        if not license.document_file:
            return Response({"error": "No file uploaded"}, status=404)
        file_path = license.document_file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        return Response({"error": "File not found"}, status=404)
