from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Sum
from django.utils import timezone
from .models import Company, JobOrder, JobOrderPosition
from .serializers import CompanySerializer, JobOrderSerializer, JobOrderPositionSerializer
from .filters import CompanyFilter, JobOrderPositionFilter


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
            job_order__status__in=['Open']
        ).annotate(
            filled_slots=Count('contracts', filter=Q(contracts__status__in=['Active', 'Signed']))
        )

        total_open_positions = sum(max(0, p.quantity - p.filled_slots) for p in all_positions)

        companies_with_positions = Company.objects.filter(
            job_orders__status__in=['Open'],
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

    @action(detail=False, methods=['get'], url_path='open-positions-status')
    def open_positions_status(self, request):
        """
        Open Positions Status report.

        Returns one row per open JobOrderPosition, with the
        principal (company), position title (rank), vacancies
        (remaining slots), and the job order's status / dates.
        Used by the Open Positions Status UI.

        GET /api/companies/open-positions-status/

        Optional query params
        ---------------------
        status (str, optional)
            Filter by job order status. Allowed: Pending, Open, Hold,
            In Progress, Active, Fulfilled, Cancelled, Closed.
            Default: only open/active (Pending, Open, Hold, In
            Progress, Active).
        principal (int, optional)
            Filter by company id.
        position_title (str, optional)
            Case-insensitive contains-match on the rank name.

        Response 200 OK
        ---------------
        {
          "total_records": 12,
          "report_date": "2026-08-11",
          "results": [
            {
              "reference_number": "JO-2024-001",
              "principal": "Maersk Line",
              "position_title": "Master / Captain",
              "vacancies": 2,
              "status": "Open",
              "job_order_number": 1,
              "request_date": "2026-01-15",
              "target_join_date": "2026-03-01"
            },
            ...
          ]
        }
        """
        # Default: only positions whose parent job order is "Open".
        # "Close" and "Full Filled" orders are excluded.
        default_open_statuses = ['Open']
        allowed_statuses = ['Open', 'Close', 'Full Filled']

        status_filter = request.query_params.get('status')
        if status_filter:
            if status_filter not in allowed_statuses:
                return Response(
                    {"error": (
                        f"Invalid status {status_filter!r}. "
                        f"Allowed: {allowed_statuses}"
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            statuses = [status_filter]
        else:
            statuses = default_open_statuses

        # Base queryset: positions linked to job orders in the
        # allowed status set. We annotate filled_slots so we can
        # compute vacancies (= quantity - filled).
        qs = (
            JobOrderPosition.objects
            .select_related('job_order__company', 'rank')
            .annotate(
                filled_slots=Count(
                    'contracts',
                    filter=Q(contracts__status__in=['Active', 'Signed']),
                ),
            )
            .filter(job_order__status__in=statuses)
        )

        # Optional filters
        principal_id = request.query_params.get('principal')
        if principal_id and str(principal_id).strip().isdigit():
            qs = qs.filter(job_order__company_id=int(principal_id))

        title_filter = request.query_params.get('position_title')
        if title_filter:
            qs = qs.filter(rank__name__icontains=title_filter)

        results = []
        for pos in qs.order_by('job_order__request_date',
                                'job_order__reference_number',
                                'rank__name'):
            vacancies = max(0, pos.quantity - pos.filled_slots)
            if vacancies <= 0:
                # Skip fully-filled positions even if the parent
                # job order is still nominally open.
                continue
            results.append({
                "reference_number": pos.job_order.reference_number,
                "principal": pos.job_order.company.company_name,
                "position_title": pos.rank.name if pos.rank else "",
                "vacancies": vacancies,
                "status": pos.job_order.status,
                "job_order_number": pos.job_order_id,
                "request_date": (
                    pos.job_order.request_date.isoformat()
                    if pos.job_order.request_date else None
                ),
                "target_join_date": (
                    pos.job_order.target_joining_date.isoformat()
                    if pos.job_order.target_joining_date else None
                ),
            })

        return Response({
            "total_records": len(results),
            "report_date": timezone.localdate().isoformat(),
            "results": results,
        })


from api.filters import JobOrderFilter
from api.permissions import JobOrderPermission

class PublicJobOrderPermission(BasePermission):
    """
    Public GET access to job orders and positions.
    Only authenticated Admins/HR/Recruiters can create/edit/delete.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, "role", None) == "Employee":
            return False
        return True

class JobOrderViewSet(viewsets.ModelViewSet):
    """
    Job Orders — formal manpower requests from companies.
    - Admin/HR/Recruiter: Full CRUD
    - Employee: Read-only (browse open job orders)
    """
    queryset = JobOrder.objects.all().prefetch_related(
        'positions__contracts__user',
        'positions__contracts__ship',
        'positions__contracts__job_position__rank',
    )
    serializer_class = JobOrderSerializer
    filterset_class = JobOrderFilter
    permission_classes = [PublicJobOrderPermission]


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
    queryset = JobOrderPosition.objects.all().prefetch_related('contracts__user')
    serializer_class = JobOrderPositionSerializer
    filterset_class = JobOrderPositionFilter
    permission_classes = [PublicJobOrderPermission]

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
