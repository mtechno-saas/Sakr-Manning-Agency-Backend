from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Vaccination
from .serializers import VaccinationSerializer
from .permissions import IsOwner

class VaccinationViewSet(ModelViewSet):
    serializer_class = VaccinationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        # Honour `?user=` first so the admin-creates-for-crew workflow
        # can list a specific crew member's vaccination records. This
        # filter applies to everyone (including Admin/HR) — the
        # security boundary is enforced by `IsOwner`, not here.
        user_id = self.request.query_params.get('user')
        if user_id:
            try:
                return Vaccination.objects.filter(user_id=int(user_id))
            except (TypeError, ValueError):
                pass
        # No `?user=` supplied: Admin / HR Manager see all, everyone
        # else sees only their own. Paired with `IsOwner`'s role
        # override so Admin/HR can also PATCH/DELETE any record.
        if user.is_authenticated and getattr(user, "role", None) in (
            "Admin", "HR Manager"
        ):
            return Vaccination.objects.all()
        return Vaccination.objects.filter(user=user)

    def perform_create(self, serializer):
        # Honour `user` in the payload OR `?user=` query param so an admin
        # can add a vaccination on behalf of a crew member. Without this,
        # every vaccination the admin adds is silently saved against the
        # admin's own user_id — same bug pattern we already fixed for
        # Course (7378078a), SeaService, NextOfKin and Reference.
        user_id = self.request.data.get('user') or self.request.query_params.get('user')
        if user_id:
            try:
                serializer.save(user_id=int(user_id))
                return
            except (TypeError, ValueError):
                pass
        serializer.save(user=self.request.user)
