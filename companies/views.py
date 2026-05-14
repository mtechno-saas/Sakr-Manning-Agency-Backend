from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from .models import Company, JobOrder, JobOrderPosition
from .models import Company, JobOrder, JobOrderPosition
from .serializers import CompanySerializer, JobOrderSerializer, JobOrderPositionSerializer
from .filters import CompanyFilter


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_class = CompanyFilter
    permission_classes = [IsAuthenticated]

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
        from django.db.models import Q
        all_positions = JobOrderPosition.objects.filter(
            job_order__status__in=['Open', 'Active', 'Pending', 'In Progress']
        ).annotate(
            filled_slots=Count('contracts', filter=Q(contracts__status__in=['Active', 'Signed']))
        )
        
        total_open_positions = sum(1 for p in all_positions if p.quantity > p.filled_slots)
        
        companies_with_positions = Company.objects.filter(
            job_orders__status__in=['Open', 'Active', 'Pending', 'In Progress'],
            job_orders__positions__in=[p.id for p in all_positions if p.quantity > p.filled_slots]
        ).distinct().count()
        
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
from api.permissions import JobOrderPermission

class JobOrderViewSet(viewsets.ModelViewSet):
    """
    Job Orders — formal manpower requests from companies.
    - Admin/HR/Recruiter: Full CRUD
    - Employee: Read-only (browse open job orders)
    """
    queryset = JobOrder.objects.all()
    serializer_class = JobOrderSerializer
    filterset_class = JobOrderFilter
    permission_classes = [JobOrderPermission]


class JobOrderPositionViewSet(viewsets.ModelViewSet):
    """
    Job Order Positions — supports single and bulk creation.

    Admin/HR/Recruiter:
        POST with a single object:
            { "job_order": 1, "rank": "2nd. Officer", "quantity": 2 }

        POST with an array (bulk create):
            [
                { "job_order": 1, "rank": "2nd. Officer", "quantity": 2 },
                { "job_order": 1, "rank": "Bosun", "quantity": 1 },
                { "job_order": 1, "rank": "Chief Cook", "quantity": 1 }
            ]

    Employee:
        POST /api/companies/job-positions/apply/
            { "position_ids": [1, 2, 3] }
        or single:
            { "position_ids": [1] }
    """
    queryset = JobOrderPosition.objects.all()
    serializer_class = JobOrderPositionSerializer
    filterset_fields = ['job_order', 'rank']
    permission_classes = [JobOrderPermission]

    def get_serializer(self, *args, **kwargs):
        # If the incoming data is a list, set many=True so DRF
        # processes it as multiple objects
        if isinstance(kwargs.get('data'), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        is_bulk = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], url_path='apply')
    def apply(self, request):
        """
        Quick Apply — Employee applies to one or more open job positions.
        POST /api/companies/job-positions/apply/

        Request (by IDs):
            { "position_ids": [1, 2, 3] }

        Request (by rank names):
            { "position_names": ["2nd. Officer", "Bosun", "Chief Cook"] }

        Request (mixed — both at once):
            { "position_ids": [1], "position_names": ["Bosun"] }

        This creates a Document (CV Application) for each position, linking:
            - user  → the logged-in employee
            - position → the rank name
            - company → the company from the job order
            
        Once the Admin approves this Document (changes status to Active), it will become a CV Submission.

        Returns the list of created Document applications.
        """
        from api.models import Document, Rank

        position_ids = request.data.get('position_ids', [])
        position_names = request.data.get('position_names', [])

        if not position_ids and not position_names:
            return Response(
                {'error': 'Provide position_ids (list of IDs) and/or position_names (list of rank names).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Collect all matching JobOrderPosition records
        from django.db.models import Q
        filters = Q()

        if position_ids and isinstance(position_ids, list):
            filters |= Q(id__in=position_ids)

        if position_names and isinstance(position_names, list):
            # Resolve rank names to JobOrderPosition records (case-insensitive)
            filters |= Q(rank__name__in=[n.strip() for n in position_names])

        positions = JobOrderPosition.objects.select_related(
            'job_order__company', 'rank'
        ).filter(filters)

        if not positions.exists():
            return Response(
                {'error': 'No valid positions found for the given IDs or names.'},
                status=status.HTTP_404_NOT_FOUND
            )

        created = []
        skipped = []

        for pos in positions:
            # Check if a pending or active document already exists for this exact position and company
            already_applied = Document.objects.filter(
                user=request.user,
                position=pos.rank.name if pos.rank else '',
                company=pos.job_order.company,
                status__in=['Pending', 'Active']
            ).exists()

            if already_applied:
                skipped.append({
                    'position_id': pos.id,
                    'rank_name': pos.rank.name if pos.rank else None,
                    'company_name': pos.job_order.company.company_name,
                    'reason': 'Already applied (Pending or Active)'
                })
                continue

            doc_title = f"Application for {pos.rank.name if pos.rank else 'Position'} at {pos.job_order.company.company_name}"
            # If the user already has a file on their profile, we can link it. Otherwise leave blank.
            user_file = request.user.file if hasattr(request.user, 'file') and request.user.file else None

            document = Document.objects.create(
                user=request.user,
                title=doc_title[:255],
                position=pos.rank.name if pos.rank else '',
                company=pos.job_order.company,
                job_position=pos,
                status='Pending',
                file=user_file
            )
            created.append({
                'document_id': document.id,
                'position_id': pos.id,
                'rank_name': pos.rank.name if pos.rank else None,
                'company_name': pos.job_order.company.company_name,
                'status': document.status,
            })

        return Response({
            'applied': created,
            'skipped': skipped,
            'total_applied': len(created),
            'total_skipped': len(skipped),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
