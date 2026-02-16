from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import Company, JobOrder, JobOrderPosition
from .models import Company, JobOrder, JobOrderPosition
from .serializers import CompanySerializer, JobOrderSerializer, JobOrderPositionSerializer
from .filters import CompanyFilter


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_class = CompanyFilter

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Returns comprehensive statistics about companies.
        GET /api/companies/stats/
        """
        # Total counts
        total_companies = Company.objects.count()
        
        # Count by status
        by_status = Company.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        status_counts = {item['status']: item['count'] for item in by_status}
        
        # Count by company type
        by_type = Company.objects.values('company_type').annotate(
            count=Count('id')
        ).order_by('company_type')
        type_counts = {item['company_type']: item['count'] for item in by_type}
        
        # Open positions stats
        total_open_positions = Company.objects.aggregate(
            total=Sum('open_positions')
        )['total'] or 0
        companies_with_positions = Company.objects.filter(
            open_positions__gt=0
        ).count()
        
        # Recently added companies (last 5)
        recent_companies = Company.objects.order_by('-created_at')[:5].values(
            'id', 'company_name', 'company_type', 'status', 'created_at'
        )
        
        return Response({
            'total_companies': total_companies,
            'by_status': status_counts,
            'by_type': type_counts,
            'open_positions': {
                'total': total_open_positions,
                'companies_with_openings': companies_with_positions
            },
            'recent_companies': list(recent_companies)
        })


from api.filters import JobOrderFilter

# ... (inside JobOrderViewSet)
class JobOrderViewSet(viewsets.ModelViewSet):
    queryset = JobOrder.objects.all()
    serializer_class = JobOrderSerializer
    filterset_class = JobOrderFilter


class JobOrderPositionViewSet(viewsets.ModelViewSet):
    queryset = JobOrderPosition.objects.all()
    serializer_class = JobOrderPositionSerializer
    filterset_fields = ['job_order', 'rank']

