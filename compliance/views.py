from rest_framework import viewsets
from .models import Audit, IncidentReport
from .serializers import AuditSerializer, IncidentReportSerializer

from api.filters import AuditFilter, IncidentReportFilter

class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    filterset_class = AuditFilter

class IncidentReportViewSet(viewsets.ModelViewSet):
    queryset = IncidentReport.objects.all()
    serializer_class = IncidentReportSerializer
    filterset_class = IncidentReportFilter
