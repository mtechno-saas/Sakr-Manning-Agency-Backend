from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import Company, Vacancy
from .serializers import CompanySerializer, VacancySerializer
from api.permissions import NotEmployeePermission


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

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

from rest_framework.permissions import BasePermission, SAFE_METHODS

class VacancyPermission(BasePermission):
    """
    Anyone (including public/unauthenticated) can view vacancies.
    Only authenticated Admins, HR Managers, and Recruiters can manage them.
    """
    def has_permission(self, request, view):
        # Allow public read access (GET)
        if request.method in SAFE_METHODS:
            return True
            
        # For creating/editing/deleting, user must be logged in
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Employees cannot manage vacancies
        if getattr(request.user, 'role', None) == 'Employee':
            return False
            
        return True

class VacancyViewSet(viewsets.ModelViewSet):
    """
    Manage Open Vacancies (add, delete, show, edit).
    Permission: Public can view, others can manage.
    """
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [VacancyPermission]
    filterset_fields = ['status', 'company']

