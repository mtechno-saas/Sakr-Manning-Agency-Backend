"""
Views for the Reports endpoint.

The frontend posts a filter spec; the backend returns the matching
rows for each requested entity section. There is no DB-side
"report definition" model — each request is self-contained.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ReportGenerateRequestSerializer
from .services import generate_report


class ReportsGenerateView(APIView):
    """
    POST /api/reports/generate/

    Body
    ----
    {
      "job_orders": { ...optional filters... },
      "companies":  { ...optional filters... },
      "ships":      { ...optional filters... },
      "users":      { ...optional filters... }
    }

    Each top-level block is optional. A block left out means "no
    filter on this entity" and the corresponding section is still
    included in the response with all rows (capped at 500 by
    default — see ``DEFAULT_LIMIT`` in services.py).

    Response 200 OK
    ---------------
    {
      "generated_at": "2026-08-16T...",
      "limit_per_section": 500,
      "sections": {
        "job_orders": { "total_records": N, "rows": [...] },
        "companies":  { "total_records": N, "rows": [...] },
        "ships":      { "total_records": N, "rows": [...] },
        "users":      { "total_records": N, "rows": [...] }
      }
    }

    Permissions
    -----------
    Any authenticated user. (Filtering by user role on the client
    side is enough; if the team needs server-side restriction we
    can swap in a custom permission class later.)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ReportGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = generate_report(serializer.validated_data)
        return Response(report, status=status.HTTP_200_OK)
