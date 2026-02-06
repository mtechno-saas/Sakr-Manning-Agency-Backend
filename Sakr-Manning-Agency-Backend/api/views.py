
# # api/views.py
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import api_view, parser_classes
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from rest_framework.response import Response
# from rest_framework import status, viewsets, generics
# from rest_framework.permissions import AllowAny
# from .models import Users, Rank, UserRank, Contract, Reference, SeaService, Certificate
# from .serializer import (
#     UsersSerializer, UserRankSerializer, ContractSerializer, 
#     ReferenceSerializer, SeaServiceSerializer, CertificateSerializer, 
#     RankSerializer, RegisterSerializer
# )
# from .filters import UsersFilter
# from .permissions import IsHROrReadOnly
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
# from rest_framework.response import Response

# from .models import Users
# from .permissions import IsHROrReadOnly
# from .serializer import UsersSerializer
# from .serializer import UserMeSerializer



# class RegisterView(generics.CreateAPIView):
#     queryset = Users.objects.all()
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = Users.objects.all()
#     serializer_class = UsersSerializer
#     permission_classes = [IsAuthenticated]

#     @action(detail=False, methods=["get"], url_path="me")
#     def me(self, request):
#         serializer = UserMeSerializer(request.user)
#         return Response(serializer.data)

# # --- List and Create Views ---

# @api_view(['GET'])
# def get_all_users(request):
#     users = Users.objects.all()
#     serializer = UsersSerializer(users, many=True)
#     return Response({"users": serializer.data})


# @api_view(["POST"])
# @parser_classes([MultiPartParser, FormParser])
# def create_user(request):
#     serializer = UsersSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def get_filter_users(request):
#     filterset = UsersFilter(request.GET, queryset=Users.objects.prefetch_related('user_ranks__rank', 'certificates').all().order_by("id"))
#     serializer = UsersSerializer(filterset.qs, many=True)
#     return Response({"users": serializer.data})


# # --- Detail, Update, and Delete View ---

# @api_view(['GET', 'PUT', 'DELETE'])
# def user_detail(request, pk):
#     """
#     Retrieve, update or delete a user instance.
#     """
#     user = get_object_or_404(Users, id=pk)

#     if request.method == 'GET':
#         serializer = UsersSerializer(user)
#         return Response(serializer.data)

#     elif request.method == 'PUT':
#         serializer = UsersSerializer(user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# # --- Other Views ---

# @api_view(["POST"])
# def assign_rank(request, user_id, rank_id):
#     try:
#         user = Users.objects.get(pk=user_id)
#         rank = Rank.objects.get(pk=rank_id)
#     except (Users.DoesNotExist, Rank.DoesNotExist):
#         return Response({"error": "User or Rank not found"}, status=status.HTTP_404_NOT_FOUND)

#     user_rank = UserRank.objects.create(user=user, rank=rank)
#     serializer = UserRankSerializer(user_rank)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)


# class ContractViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for managing seafarer contracts.
#     """
#     queryset = Contract.objects.all()
#     serializer_class = ContractSerializer


# class ReferenceViewSet(viewsets.ModelViewSet):
#     queryset = Reference.objects.all()
#     serializer_class = ReferenceSerializer


# class SeaServiceViewSet(viewsets.ModelViewSet):
#     queryset = SeaService.objects.all()
#     serializer_class = SeaServiceSerializer


# class CertificateViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for managing certificates.
#     """
#     queryset = Certificate.objects.all()
#     serializer_class = CertificateSerializer


# class RankViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for managing ranks.
#     """
#     queryset = Rank.objects.all()
#     serializer_class = RankSerializer


# # --- User-specific Certificate and Rank Endpoints ---

# @api_view(['GET'])
# def get_user_certificates(request, user_id):
#     """
#     Get all certificates that a specific user has taken.
#     """
#     try:
#         user = Users.objects.get(pk=user_id)
#     except Users.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     certificates = user.certificates.all()
#     serializer = CertificateSerializer(certificates, many=True)
#     return Response({
#         "user_id": user_id,
#         "user_name": f"{user.first_name} {user.middle_name}",
#         "certificates": serializer.data
#     })


# @api_view(['GET'])
# def get_user_ranks(request, user_id):
#     """
#     Get all ranks that a specific user wants to apply for (has been assigned).
#     """
#     try:
#         user = Users.objects.get(pk=user_id)
#     except Users.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     user_ranks = UserRank.objects.filter(user=user).select_related('rank')
#     serializer = UserRankSerializer(user_ranks, many=True)
#     return Response({
#         "user_id": user_id,
#         "user_name": f"{user.first_name} {user.middle_name}",
#         "ranks": serializer.data
#     })


# @api_view(['POST'])
# def add_user_certificate(request, user_id):
#     """
#     Add a certificate to a user.
#     Expected payload: {"certificate_id": 1}
#     """
#     try:
#         user = Users.objects.get(pk=user_id)
#     except Users.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     certificate_id = request.data.get('certificate_id')
#     if not certificate_id:
#         return Response({"error": "certificate_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         certificate = Certificate.objects.get(pk=certificate_id)
#     except Certificate.DoesNotExist:
#         return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     user.certificates.add(certificate)
#     return Response({
#         "message": f"Certificate '{certificate.name}' added to user {user.first_name} {user.middle_name}",
#         "certificate": CertificateSerializer(certificate).data
#     }, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def add_user_rank(request, user_id):
#     """
#     Add a rank to a user (rank they want to apply for).
#     Expected payload: {"rank_id": 1}
#     """
#     try:
#         user = Users.objects.get(pk=user_id)
#     except Users.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     rank_id = request.data.get('rank_id')
#     if not rank_id:
#         return Response({"error": "rank_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         rank = Rank.objects.get(pk=rank_id)
#     except Rank.DoesNotExist:
#         return Response({"error": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     # Check if user already has this rank
#     if UserRank.objects.filter(user=user, rank=rank).exists():
#         return Response({"error": "User already has this rank"}, status=status.HTTP_400_BAD_REQUEST)
    
#     user_rank = UserRank.objects.create(user=user, rank=rank)
#     serializer = UserRankSerializer(user_rank)
#     return Response({
#         "message": f"Rank '{rank.name}' added to user {user.first_name} {user.middle_name}",
#         "user_rank": serializer.data
#     }, status=status.HTTP_201_CREATED)


# @api_view(['DELETE'])
# def remove_user_certificate(request, user_id, certificate_id):
#     """
#     Remove a certificate from a user.
#     """
#     try:
#         user = Users.objects.get(pk=user_id)
#         certificate = Certificate.objects.get(pk=certificate_id)
#     except Users.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Certificate.DoesNotExist:
#         return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     user.certificates.remove(certificate)
#     return Response({
#         "message": f"Certificate '{certificate.name}' removed from user {user.first_name} {user.middle_name}"
#     }, status=status.HTTP_200_OK)


# @api_view(['DELETE'])
# def remove_user_rank(request, user_id, rank_id):
#     """
#     Remove a rank from a user.
#     """
#     try:
#         user = Users.objects.get(pk=user_id)
#         rank = Rank.objects.get(pk=rank_id)
#     except Users.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Rank.DoesNotExist:
#         return Response({"error": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     try:
#         user_rank = UserRank.objects.get(user=user, rank=rank)
#         user_rank.delete()
#         return Response({
#             "message": f"Rank '{rank.name}' removed from user {user.first_name} {user.middle_name}"
#         }, status=status.HTTP_200_OK)
#     except UserRank.DoesNotExist:
#         return Response({"error": "User does not have this rank"}, status=status.HTTP_404_NOT_FOUND)







from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from finance.models import FinanceRecord
from .models import Company, Interview, CVSubmission
from .serializer import CompanySerializer, InterviewSerializer, CVSubmissionSerializer
from .filters import CompanyFilter, InterviewFilter, CVSubmissionFilter

from .models import (
    Users, Rank, UserRank, Contract, Reference, SeaService, Certificate,
    Company, Interview, CVSubmission, UserCertificate, Declaration
)
from .serializer import (
    UsersSerializer, UserRankSerializer, ContractSerializer, ContractListSerializer,
    ReferenceSerializer, SeaServiceSerializer, CertificateSerializer,
    RankSerializer, RegisterSerializer, UserMeSerializer,
    CompanySerializer, CompanyListSerializer,
    InterviewSerializer, InterviewCalendarSerializer,
    FinanceRecordSerializer,
    CVSubmissionSerializer, CVSubmissionListSerializer,
    UserCertificateSerializer, DeclarationSerializer
)
from .filters import UsersFilter, InterviewFilter, FinanceRecordFilter, CVSubmissionFilter, CompanyFilter
from .permissions import (
    IsAdmin, IsHRManager, IsRecruiter, IsEmployee,
    IsHROrReadOnly, IsOwnerOrHR, UserPermission,
    CVPermission, InterviewPermission, FinancePermission,
    CompanyPermission, ContractPermission
)


from django.core.cache import cache
from rest_framework.views import APIView

class RegisterView(generics.CreateAPIView):
    queryset = Users.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete online status cache immediately
            cache.delete(f'online_user_{request.user.id}')
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    User Management - Role-based access:
    - Admin: Full access
    - HR Manager: Manage non-admin users
    - Recruiter: View only
    - Employee: Own profile only
    """
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated, UserPermission]
    filterset_class = UsersFilter

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Users.objects.all()
        # Employee can only see themselves
        return Users.objects.filter(id=user.id)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """User statistics for dashboard"""
        if request.user.role not in ['Admin', 'HR Manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        users = Users.objects.all()
        return Response({
            'total_users': users.count(),
            'admins': users.filter(role='Admin').count(),
            'hr_managers': users.filter(role='HR Manager').count(),
            'recruiters': users.filter(role='Recruiter').count(),
            'employees': users.filter(role='Employee').count(),
            'active_users': users.filter(is_active=True).count(),
        })


# --- Function-based views with permission checks ---

@api_view(['GET'])
def get_all_users(request):
    """Get all users - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager', 'Recruiter']:
        return Response({'error': 'Permission denied'}, status=403)
    
    users = Users.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response({"users": serializer.data})


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_user(request):
    """Create user - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied'}, status=403)
    
    # HR can't create admins
    if request.user.role == 'HR Manager' and request.data.get('role') == 'Admin':
        return Response({'error': 'Cannot create admin users'}, status=403)
    
    serializer = UsersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_filter_users(request):
    """Filter users - Role-based access"""
    if request.user.role not in ['Admin', 'HR Manager', 'Recruiter']:
        return Response({'error': 'Permission denied'}, status=403)
    
    filterset = UsersFilter(
        request.GET, 
        queryset=Users.objects.prefetch_related('user_ranks__rank', 'certificates').all().order_by("id")
    )
    serializer = UsersSerializer(filterset.qs, many=True)
    return Response({"users": serializer.data})


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    """User detail - Role-based access"""
    user = get_object_or_404(Users, id=pk)
    
    # Permission check
    if request.user.role == 'Employee' and request.user.id != pk:
        return Response({'error': 'Permission denied'}, status=403)
    
    if request.user.role == 'Recruiter' and request.method != 'GET':
        return Response({'error': 'Permission denied'}, status=403)
    
    if request.user.role == 'HR Manager' and user.role == 'Admin':
        return Response({'error': 'Cannot modify admin users'}, status=403)

    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UsersSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.user.role != 'Admin':
            return Response({'error': 'Only admins can delete users'}, status=403)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def assign_rank(request, user_id, rank_id):
    """Assign rank - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
        rank = Rank.objects.get(pk=rank_id)
    except (Users.DoesNotExist, Rank.DoesNotExist):
        return Response({"error": "User or Rank not found"}, status=status.HTTP_404_NOT_FOUND)

    user_rank = UserRank.objects.create(user=user, rank=rank)
    serializer = UserRankSerializer(user_rank)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# =====================
# VIEWSETS WITH ROLE-BASED PERMISSIONS
# =====================

class ContractViewSet(viewsets.ModelViewSet):
    """
    Documents Management - Role-based access:
    - Admin/HR: Full access
    - Recruiter: Read only
    - Employee: Own contracts only
    """
    queryset = Contract.objects.select_related('user', 'ship', 'company', 'rank').all()
    permission_classes = [IsAuthenticated, ContractPermission]

    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        return ContractSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Contract.objects.select_related('user', 'ship', 'company', 'rank').all()
        return Contract.objects.filter(user=user)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Contract statistics for Documents Management dashboard"""
        if request.user.role not in ['Admin', 'HR Manager', 'Recruiter']:
            contracts = Contract.objects.filter(user=request.user)
        else:
            contracts = Contract.objects.all()
        
        today = timezone.now().date()
        return Response({
            'signed_contracts': contracts.filter(status='Signed').count(),
            'pending_signature': contracts.filter(status='Pending Signature').count(),
            'drafts': contracts.filter(status='Draft').count(),
            'critical': contracts.filter(
                sign_off_date__lte=today + timedelta(days=7),
                status__in=['Active', 'Signed']
            ).count(),
            'warning': contracts.filter(
                sign_off_date__lte=today + timedelta(days=30),
                sign_off_date__gt=today + timedelta(days=7),
                status__in=['Active', 'Signed']
            ).count(),
            'notice': contracts.filter(
                sign_off_date__lte=today + timedelta(days=60),
                sign_off_date__gt=today + timedelta(days=30),
                status__in=['Active', 'Signed']
            ).count(),
        })


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Companies Management - Role-based access:
    - Admin: Full access
    - HR/Recruiter: View and edit
    - Employee: Read only
    """
    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated, CompanyPermission]
    filterset_class = CompanyFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Company statistics"""
        companies = Company.objects.all()
        return Response({
            'total_companies': companies.count(),
            'active_companies': companies.filter(status='Active').count(),
            'total_open_positions': companies.aggregate(total=Sum('open_positions'))['total'] or 0,
        })


class InterviewViewSet(viewsets.ModelViewSet):
    """
    Interviews Scheduling - Role-based access:
    - Admin/HR/Recruiter: Full access
    - Employee: Own interviews only (read)
    """
    queryset = Interview.objects.select_related('candidate', 'company', 'position').all()
    permission_classes = [IsAuthenticated, InterviewPermission]
    filterset_class = InterviewFilter

    def get_serializer_class(self):
        if self.action == 'calendar':
            return InterviewCalendarSerializer
        return InterviewSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Interview.objects.select_related('candidate', 'company', 'position').all()
        return Interview.objects.filter(candidate=user)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Interview statistics for dashboard cards"""
        today = timezone.now().date()
        week_end = today + timedelta(days=7)
        
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            interviews = Interview.objects.all()
        else:
            interviews = Interview.objects.filter(candidate=request.user)
        
        return Response({
            'today_interviews': interviews.filter(scheduled_date=today).count(),
            'this_week': interviews.filter(
                scheduled_date__gte=today,
                scheduled_date__lte=week_end
            ).count(),
            'pending_confirmation': interviews.filter(status='Pending Confirmation').count(),
        })

    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        """Get interviews for calendar view"""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        interviews = self.get_queryset()
        if month and year:
            interviews = interviews.filter(
                scheduled_date__month=month,
                scheduled_date__year=year
            )
        
        serializer = InterviewCalendarSerializer(interviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        """Get interview counts by status"""
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            interviews = Interview.objects.all()
        else:
            interviews = Interview.objects.filter(candidate=request.user)
        
        return Response({
            'scheduled': interviews.filter(status='Scheduled').count(),
            'completed': interviews.filter(status='Completed').count(),
            'cancelled': interviews.filter(status='Cancelled').count(),
            'rescheduled': interviews.filter(status='Rescheduled').count(),
            'no_show': interviews.filter(status='No Show').count(),
            'total': interviews.count(),
        })


class FinanceRecordViewSet(viewsets.ModelViewSet):
    """
    Finance Records Management - Role-based access:
    - Admin/HR: Full access
    - Recruiter: Read only
    - Employee: Own records only (read)
    """
    queryset = FinanceRecord.objects.select_related('user', 'company').all()
    serializer_class = FinanceRecordSerializer
    permission_classes = [IsAuthenticated, FinancePermission]
    filterset_class = FinanceRecordFilter

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager']:
            return FinanceRecord.objects.select_related('user', 'company').all()
        return FinanceRecord.objects.filter(user=user)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Finance statistics"""
        if request.user.role not in ['Admin', 'HR Manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        records = FinanceRecord.objects.all()
        return Response({
            'total_records': records.count(),
            'pending': records.filter(status='Pending').count(),
            'approved': records.filter(status='Approved').count(),
            'paid': records.filter(status='Paid').count(),
        })

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Export finance records"""
        if request.user.role not in ['Admin', 'HR Manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        records = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)


class CVSubmissionViewSet(viewsets.ModelViewSet):
    """
    CVs Management - Role-based access:
    - Admin/HR: Full access
    - Recruiter: View and update status
    - Employee: Own CVs only
    """
    queryset = CVSubmission.objects.select_related('user', 'position', 'company').all()
    permission_classes = [IsAuthenticated, CVPermission]
    filterset_class = CVSubmissionFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return CVSubmissionListSerializer
        return CVSubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return CVSubmission.objects.select_related('user', 'position', 'company').all()
        return CVSubmission.objects.filter(user=user)

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        # Employee can only submit CV for themselves
        if self.request.user.role == 'Employee':
            serializer.save(user=self.request.user)
        else:
            if 'user' not in serializer.validated_data:
                raise ValidationError({"user": ["This field is required."]})
            serializer.save()

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """CV statistics for dashboard"""
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            cvs = CVSubmission.objects.all()
        else:
            cvs = CVSubmission.objects.filter(user=request.user)
        
        total = cvs.count()
        return Response({
            'total': total,
            'under_review': cvs.filter(status='Under Review').count(),
            'interviewed': cvs.filter(status='Interviewed').count(),
            'pending': cvs.filter(status='Pending').count(),
            'approved': cvs.filter(status='Approved').count(),
            'under_review_percent': round((cvs.filter(status='Under Review').count() / total * 100) if total > 0 else 0),
            'interviewed_percent': round((cvs.filter(status='Interviewed').count() / total * 100) if total > 0 else 0),
            'pending_percent': round((cvs.filter(status='Pending').count() / total * 100) if total > 0 else 0),
            'approved_percent': round((cvs.filter(status='Approved').count() / total * 100) if total > 0 else 0),
        })

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Update CV status - Recruiter+ access"""
        if request.user.role not in ['Admin', 'HR Manager', 'Recruiter']:
            return Response({'error': 'Permission denied'}, status=403)
        
        cv = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(CVSubmission.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=400)
        
        cv.status = new_status
        if new_status in ['Approved', 'Rejected']:
            cv.reviewed_by = request.user
            cv.reviewed_date = timezone.now().date()
        cv.save()
        
        return Response(CVSubmissionSerializer(cv).data)


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
    permission_classes = [IsAuthenticated, IsHROrReadOnly]


class SeaServiceViewSet(viewsets.ModelViewSet):
    queryset = SeaService.objects.all()
    serializer_class = SeaServiceSerializer
    permission_classes = [IsAuthenticated, IsHROrReadOnly]


class CertificateViewSet(viewsets.ModelViewSet):
    """Certificates - Admin/HR can edit, others read only"""
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsHROrReadOnly]


class RankViewSet(viewsets.ModelViewSet):
    """Ranks - Admin/HR can edit, others read only"""
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    permission_classes = [IsAuthenticated, IsHROrReadOnly]


class UserCertificateViewSet(viewsets.ModelViewSet):
    """
    User Certificate/Course Instances - Role-based access:
    - Admin/HR: Full access to all certificates
    - Recruiter: Read only  
    - Employee: Own certificates only
    """
    queryset = UserCertificate.objects.select_related(
        'user', 'certificate_type', 'rank'
    ).all()
    serializer_class = UserCertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = UserCertificate.objects.select_related(
            'user', 'certificate_type', 'rank'
        )
        
        # Filter by user based on role
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(user=user)
        
        # Filter by category (Certificate or Course) if specified
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by user_id if specified (for HR/Admin viewing specific user)
        user_id = self.request.query_params.get('user_id', None)
        if user_id and user.role in ['Admin', 'HR Manager', 'Recruiter']:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the user when creating a certificate"""
        if self.request.user.role == 'Employee':
            # Employee can only create certificates for themselves
            serializer.save(user=self.request.user)
        else:
            # HR/Admin can specify the user
            serializer.save()
    
    def perform_update(self, serializer):
        """Permission check for updates"""
        instance = self.get_object()
        user = self.request.user
        
        # Employee can only update their own certificates
        if user.role == 'Employee' and instance.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own certificates")
        
        # Recruiter cannot edit
        if user.role == 'Recruiter':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Recruiters have read-only access")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Permission check for deletion"""
        user = self.request.user
        
        # Only Admin and HR can delete
        if user.role not in ['Admin', 'HR Manager']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only Admin and HR can delete certificates")
        
        instance.delete()
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Certificate statistics"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        return Response({
            'total_certificates': queryset.count(),
            'certificates': queryset.filter(category='Certificate').count(),
            'courses': queryset.filter(category='Course').count(),
            'expired': queryset.filter(expiry_date__lt=today).count(),
            'expiring_soon': queryset.filter(
                expiry_date__gte=today,
                expiry_date__lte=today + timedelta(days=30)
            ).count(),
        })





# --- User-specific endpoints ---

@api_view(['GET'])
def get_user_certificates(request, user_id):
    """Get user certificates - Owner or HR+"""
    if request.user.role not in ['Admin', 'HR Manager', 'Recruiter'] and request.user.id != user_id:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    certificates = user.certificates.all()
    serializer = CertificateSerializer(certificates, many=True)
    return Response({
        "user_id": user_id,
        "user_name": f"{user.first_name} {user.middle_name}",
        "certificates": serializer.data
    })


@api_view(['GET'])
def get_user_ranks(request, user_id):
    """Get user ranks - Owner or HR+"""
    if request.user.role not in ['Admin', 'HR Manager', 'Recruiter'] and request.user.id != user_id:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user_ranks = UserRank.objects.filter(user=user).select_related('rank')
    serializer = UserRankSerializer(user_ranks, many=True)
    return Response({
        "user_id": user_id,
        "user_name": f"{user.first_name} {user.middle_name}",
        "ranks": serializer.data
    })


@api_view(['POST'])
def add_user_certificate(request, user_id):
    """Add certificate to user - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    certificate_id = request.data.get('certificate_id')
    if not certificate_id:
        return Response({"error": "certificate_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        certificate = Certificate.objects.get(pk=certificate_id)
    except Certificate.DoesNotExist:
        return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user.certificates.add(certificate)
    return Response({
        "message": f"Certificate '{certificate.name}' added to user {user.first_name} {user.middle_name}",
        "certificate": CertificateSerializer(certificate).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_user_rank(request, user_id):
    """Add rank to user - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    rank_id = request.data.get('rank_id')
    if not rank_id:
        return Response({"error": "rank_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        rank = Rank.objects.get(pk=rank_id)
    except Rank.DoesNotExist:
        return Response({"error": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if UserRank.objects.filter(user=user, rank=rank).exists():
        return Response({"error": "User already has this rank"}, status=status.HTTP_400_BAD_REQUEST)
    
    user_rank = UserRank.objects.create(user=user, rank=rank)
    serializer = UserRankSerializer(user_rank)
    return Response({
        "message": f"Rank '{rank.name}' added to user {user.first_name} {user.middle_name}",
        "user_rank": serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_user_certificate(request, user_id, certificate_id):
    """Remove certificate from user - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
        certificate = Certificate.objects.get(pk=certificate_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Certificate.DoesNotExist:
        return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user.certificates.remove(certificate)
    return Response({
        "message": f"Certificate '{certificate.name}' removed from user {user.first_name} {user.middle_name}"
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_user_rank(request, user_id, rank_id):
    """Remove rank from user - Admin/HR only"""
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        user = Users.objects.get(pk=user_id)
        rank = Rank.objects.get(pk=rank_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Rank.DoesNotExist:
        return Response({"error": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        user_rank = UserRank.objects.get(user=user, rank=rank)
        user_rank.delete()
        return Response({
            "message": f"Rank '{rank.name}' removed from user {user.first_name} {user.middle_name}"
        }, status=status.HTTP_200_OK)
    except UserRank.DoesNotExist:
        return Response({"error": "User does not have this rank"}, status=status.HTTP_404_NOT_FOUND)
    


# =====================
# DECLARATION VIEWSET
# =====================

class DeclarationViewSet(viewsets.ModelViewSet):
    """
    Health Declaration Management - Role-based access:
    - Admin/HR Manager: Full access to all declarations
    - Recruiter: Read-only access to all declarations
    - Employee: Full access to their own declarations only
    """
    queryset = Declaration.objects.select_related('user').all()
    serializer_class = DeclarationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter declarations based on user role"""
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Declaration.objects.select_related('user').all()
        # Employee can only see their own declarations
        return Declaration.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Set the user when creating a declaration"""
        if self.request.user.role == 'Employee':
            # Employee can only create declarations for themselves
            serializer.save(user=self.request.user)
        else:
            # HR/Admin can specify the user
            serializer.save()
    
    def perform_update(self, serializer):
        """Permission check for updates"""
        instance = self.get_object()
        user = self.request.user
        
        # Employee can only update their own declarations
        if user.role == 'Employee' and instance.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own declarations")
        
        # Recruiter cannot edit
        if user.role == 'Recruiter':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Recruiters have read-only access")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Permission check for deletion - Admin/HR only"""
        user = self.request.user
        if user.role not in ['Admin', 'HR Manager']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only Admin and HR Manager can delete declarations")
        instance.delete()
