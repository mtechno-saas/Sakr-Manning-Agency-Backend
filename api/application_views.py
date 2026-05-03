from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Users
from .seafarer_application_serializers import SeafarerApplicationSerializer

class SeafarerApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Seafarer Employment Application.
    Provides GET, POST, PATCH, and DELETE for the aggregated seafarer profile.
    """
    queryset = Users.objects.all()
    serializer_class = SeafarerApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Users.objects.all()
        # Employee can only see their own application
        return Users.objects.filter(id=user.id)

    def destroy(self, request, *args, **kwargs):
        """
        Only Admins should be able to delete a seafarer profile.
        """
        if request.user.role != 'Admin':
            return Response(
                {"error": "Only administrators can delete a seafarer profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
