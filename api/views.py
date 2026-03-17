import os
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes, action, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.http import FileResponse, HttpResponseRedirect
from rest_framework import status, viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from finance.models import FinanceRecord
from .models import Company, Interview, CVSubmission
from .serializer import CompanySerializer, InterviewSerializer, CVSubmissionSerializer
from .filters import CompanyFilter, InterviewFilter, CVSubmissionFilter
from .models import (
    Users, Rank, UserRank, Contract, Reference, SeaService, Certificate,
    Company, Interview, CVSubmission, Document,
    UserLanguage, PersonalDocument, Declaration, NextOfKin
)

# For Verification Link
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from rest_framework.views import APIView


from .models import (
    Users, Rank, UserRank, Contract, Reference, SeaService, Certificate,
    #Company, Interview, CVSubmission, Document,
    UserLanguage, PersonalDocument, Declaration, NextOfKin
)
from .serializer import (
    UsersSerializer, UserRankSerializer, ContractSerializer, ContractListSerializer,
    ReferenceSerializer, SeaServiceSerializer, CertificateSerializer, NextOfKinSerializer,
    RankSerializer, RegisterSerializer, UserMeSerializer, DeclarationSerializer,
    CompanySerializer, CompanyListSerializer,
    InterviewSerializer, InterviewCalendarSerializer,
    FinanceRecordSerializer,
    CVSubmissionSerializer, CVSubmissionListSerializer, DocumentSerializer,
    UserLanguageSerializer, PersonalDocumentSerializer
)
from .filters import UsersFilter, InterviewFilter, FinanceRecordFilter, CVSubmissionFilter, CompanyFilter
from .permissions import (
    IsAdmin, IsHRManager, IsRecruiter, IsEmployee,
    IsHROrReadOnly, IsOwnerOrHR, UserPermission,
    CVPermission, InterviewPermission, FinancePermission,
    CompanyPermission, ContractPermission
)

from rest_framework import viewsets, permissions
from django.core.cache import cache
from rest_framework.views import APIView

class RegisterView(generics.CreateAPIView):
    queryset = Users.objects.all()
    authentication_classes = []
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class VerifyEmailView(APIView):
    """
    Verify email via token sent in welcome email.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Activate user if needed, or just return success
            # user.is_active = True # Depending on requirements
            # user.save()
            # Redirect to user form/profile
            return HttpResponseRedirect("https://test.sakrshipping.com/profile")
        else:
            return HttpResponseRedirect("https://test.sakrshipping.com/login?error=invalid_token")


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete online status cache immediately
            cache.delete(f'online_user_{request.user.id}')
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class LanguageProficiencyViewSet(viewsets.ModelViewSet):
#     serializer_class = LanguageProficiencySerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         """
#         This ensures users can ONLY see, edit, or delete 
#         their own language records.
#         """
#         return LanguageProficiency.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        When a user adds a new language, this automatically 
        links it to the person currently logged in.
        """
        serializer.save(user=self.request.user)
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

    @action(detail=True, methods=['get'], url_path='download-marlins')
    def download_marlins(self, request, pk=None):
        """Download Marlins test attachment"""
        user = self.get_object()
        if not user.marlins_test_attachment:
            return Response({'error': 'No Marlins test file uploaded'}, status=404)
        file_path = user.marlins_test_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-ces')
    def download_ces(self, request, pk=None):
        """Download CES test attachment"""
        user = self.get_object()
        if not user.ces_test_attachment:
            return Response({'error': 'No CES test file uploaded'}, status=404)
        file_path = user.ces_test_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found'}, status=404)


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

    @action(detail=False, methods=['post'], url_path='upload', parser_classes=[MultiPartParser, FormParser])
    def upload_cv(self, request):
        """
        Upload a CV document (PDF/Word).
        POST /api/cv-submissions/upload/
        Body: cv_file, position_id (optional-ish)
        """
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        file_obj = request.FILES.get('cv_file')
        if not file_obj:
            return Response({'error': 'No file provided (key: cv_file)'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine position if provided
        position_id = request.data.get('position')
        position = None
        if position_id:
            from .models import Rank
            position = get_object_or_404(Rank, id=position_id)
            
        # Create submission
        submission = CVSubmission.objects.create(
            user=request.user,
            cv_file=file_obj,
            position=position,
            status='Pending',
            notes=request.data.get('notes', '')
        )
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return Reference.objects.filter(user_id=user_id)
        return Reference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        if user_id:
            serializer.save(user_id=user_id)
        else:
            serializer.save(user=self.request.user)


class SeaServiceViewSet(viewsets.ModelViewSet):
    """
    Sea Service Management - Role-based access:
    - Admin/HR Manager/Employee: Full access to all records
    """
    queryset = SeaService.objects.all()
    serializer_class = SeaServiceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return SeaService.objects.filter(user_id=user_id)
        return SeaService.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user') or self.request.query_params.get('user')
        if user_id:
            serializer.save(user_id=user_id)
        elif self.request.user.role == 'Employee':
            serializer.save(user=self.request.user)
        else:
            if 'user' not in serializer.validated_data:
                serializer.save(user=self.request.user)
            else:
                serializer.save()


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Document Management - Role-based access:
    - Admin/HR: Full access
    - Employee: Own documents only
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_authenticators(self):
        if self.request.method == 'POST':
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Document.objects.all()

    def perform_create(self, serializer):
        # Assign current user if not Admin/HR or if they want to
        # Generally for this endpoint, we assume the uploader is the owner unless specified otherwise
        # But if employee, they can only upload for themselves
        if self.request.user.is_authenticated and self.request.user.role == 'Employee' and not self.request.user.is_superuser:
            serializer.save(user=self.request.user)
        else:
            # For Admin/HR/Recruiter/Superuser:
            # If 'user' is explicitly provided, use it.
            if 'user' in serializer.validated_data:
                serializer.save()
            else:
                # If no user specified, try to link via email
                email = serializer.validated_data.get('email')
                name = serializer.validated_data.get('name')
                
                if email:
                    # Check if user exists
                    existing_user = Users.objects.filter(email=email).first()
                    if existing_user:
                        serializer.save(user=existing_user)
                    else:
                        # Create new user for this applicant
                        print(f"DEBUG: Creating new user for Quick Applier: {email}")
                        first_name = name.split(' ')[0] if name else "Applicant"
                        new_user = Users.objects.create_user(
                            email=email,
                            first_name=first_name,
                            role='Employee', # Default role for applicants
                            password=None, # Unusable password until they set it
                            # user_status='Active' # Removed invalid choice
                        )
                        serializer.save(user=new_user)
                else:
                    # Fallback to uploader if no email provided (though rare for applications)
                    serializer.save(user=self.request.user)

    def _sync_user_data(self, document):
        """Helper to sync Document data to User profile when Active"""
        print(f"DEBUG: Syncing user data for document {document.id} to user {document.user.id}")
        user = document.user
        
        # Update name if provided
        if document.name:
            parts = document.name.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.middle_name = parts[1]
                
        # Update contact info
        if document.email:
             # Check if email is already taken by another user
            if not Users.objects.filter(email=document.email).exclude(id=user.id).exists():
                user.email = document.email
            else:
                print(f"DEBUG: Skipping email update, {document.email} is already taken.")
        if document.phone_number:
            user.phone_number = document.phone_number
            
        # Update new fields
        if document.title:
            user.title = document.title
        if document.file:
            user.file = document.file
        if document.position:
            user.position = document.position
            
        user.save()

    def _check_id_generation(self, document, new_status):
        """Helper to generate User ID if status becomes Active"""
        print(f"DEBUG: Checking ID generation for doc {document.id}, status {new_status}")
        if new_status == 'Active':
            user = document.user
            if not user.generated_id:
                # Generate 12-digit random number
                new_id = ''.join(random.choices(string.digits, k=12))
                
                # Check uniqueness loop
                while Users.objects.filter(generated_id=new_id).exists():
                    new_id = ''.join(random.choices(string.digits, k=12))
                
                user.generated_id = new_id
                user.save()
            
            # Sync data to user profile
            self._sync_user_data(document)

            # Send acceptance email
            try:
                if user.email:
                    # Generate verification token
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # Build verification link
                    # Since this call likely comes from perform_update in the same ViewSet, 
                    # self.request should be available
                    if hasattr(self, 'request') and self.request:
                        # base_url = self.request.build_absolute_uri('/')[:-1] 
                        # Force domain as per user request
                        base_url = "https://test.sakrshipping.com"
                        verification_link = f"{base_url}/api/verify-email/{uid}/{token}/"
                    else:
                        # Fallback
                        verification_link = f"https://test.sakrshipping.com/api/verify-email/{uid}/{token}/"

                    send_mail(
                        subject='Welcome to Sakr Manning Agency - Verification Required',
                        message=f"Dear {user.first_name},\n\nYou have been accepted to the Sakr Manning Agency website.\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nYou can now log in and complete your information in the form.\n\nBest regards,\nSakr Manning Agency",
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@sakrmanning.com',
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
            except Exception as e:
                print(f"Failed to send email: {e}")

    def perform_update(self, serializer):
        # Check if status is being updated
        if 'status' in serializer.validated_data:
            self._check_id_generation(serializer.instance, serializer.validated_data['status'])
        
        serializer.save()

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """
        Manually set status for a document.
        POST /api/documents/{id}/set_status/
        Body: {"status": "Active"}
        """
        # Permission Check: Only Admin/HR/Recruiter or Superuser can change status
        if request.user.role not in ['Admin', 'HR Manager', 'Recruiter'] and not request.user.is_superuser:
            return Response(
                {"error": "Permission denied. You cannot change document status."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        print(f"DEBUG: set_status called for doc {pk} with data {request.data}")
        document = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = dict(Document.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Choices are: {list(valid_statuses)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Merge Logic: Check if email exists on another user
        if document.email:
            existing_user = Users.objects.filter(email=document.email).exclude(id=document.user.id).first()
            if existing_user:
                print(f"DEBUG: Merging document {document.id} from user {document.user.id} to existing user {existing_user.id}")
                document.user = existing_user
            
        document.status = new_status
        document.save()
        print("DEBUG: Document saved")
        
        # Trigger side effects
        try:
            self._check_id_generation(document, new_status)
        except Exception as e:
            print(f"DEBUG: Error in side effects: {e}")
            import traceback
            traceback.print_exc()
            # We might want to re-raise or handle it, but for 500 debugging let's print it
            raise e
        
        # Refresh the user object to ensure generated_id is picked up by serializer
        document.user.refresh_from_db()
        
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download/View the document file.
        """
        document = self.get_object()
        if not document.file:
            return Response({"error": "No file attached to this document"}, status=status.HTTP_404_NOT_FOUND)
        
        # FileResponse automatically handles streaming and content type
        response = FileResponse(document.file.open(), as_attachment=False)
        return response



class CertificateViewSet(viewsets.ModelViewSet):
    """Certificates - Admin/HR can edit, others read only"""
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsHROrReadOnly]


class RankViewSet(viewsets.ModelViewSet):
    """Ranks - All authenticated users can access"""
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    permission_classes = [IsAuthenticated]


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
    

class UserLanguageViewSet(viewsets.ModelViewSet):
    """
    User Languages - Role-based access:
    - Admin/HR Manager: Full access to all records
    - Employee: Full access to all records
    """
    queryset = UserLanguage.objects.all()
    serializer_class = UserLanguageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.user.role not in ['Admin', 'HR Manager', 'Employee']:
            self.permission_denied(request, message="Only Admin, HR Manager, and Employee roles can access this endpoint.")

    def get_queryset(self):
        return UserLanguage.objects.all()

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        if self.request.user.role == 'Employee':
            serializer.save(user=self.request.user)
        else:
            if 'user' not in serializer.validated_data:
                raise ValidationError({"user": ["This field is required when creating a language record for another user."]})
            serializer.save()


class PersonalDocumentViewSet(viewsets.ModelViewSet):
    """
    Personal/Travel Documents - Role-based access:
    - Admin/HR/Recruiter: Full access
    - Employee: Own documents only
    """
    queryset = PersonalDocument.objects.all()
    serializer_class = PersonalDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return PersonalDocument.objects.all()
        return PersonalDocument.objects.filter(user=user)

    def perform_create(self, serializer):
        if self.request.user.role == 'Employee':
            serializer.save(user=self.request.user)
        else:
            if 'user' not in serializer.validated_data:
                serializer.save(user=self.request.user)
            else:
                serializer.save()


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_positions(request):
    """
    Return all available positions.
    Accessible by any authenticated user.
    GET /api/positions/
    """
    positions = [
        {"value": value, "label": label}
        for value, label in Document.POSITION_CHOICES
    ]
    return Response(positions)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coc_choices(request):
    """
    Return all available COC certificate name choices.
    GET /api/coc-choices/
    """
    choices = [
        {"value": value, "label": label}
        for value, label in Users.COC_CERTIFICATE_CHOICES
    ]
    return Response(choices)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_flags(request):
    """
    Return all available maritime flag states.
    Accessible by any authenticated user.
    GET /api/flags/
    """

    FLAGS = [
        ("Algeria", "Algeria"),
        ("Angola", "Angola"),
        ("Antigua and Barbuda", "Antigua and Barbuda"),
        ("Argentina", "Argentina"),
        ("Australia", "Australia"),
        ("Bahamas", "Bahamas"),
        ("Bahrain", "Bahrain"),
        ("Bangladesh", "Bangladesh"),
        ("Barbados", "Barbados"),
        ("Belgium", "Belgium"),
        ("Belize", "Belize"),
        ("Bermuda", "Bermuda"),
        ("Brazil", "Brazil"),
        ("Brunei", "Brunei"),
        ("Bulgaria", "Bulgaria"),
        ("Cambodia", "Cambodia"),
        ("Cameroon", "Cameroon"),
        ("Canada", "Canada"),
        ("Cayman Islands", "Cayman Islands"),
        ("Chile", "Chile"),
        ("China", "China"),
        ("Colombia", "Colombia"),
        ("Comoros", "Comoros"),
        ("Cook Islands", "Cook Islands"),
        ("Croatia", "Croatia"),
        ("Cuba", "Cuba"),
        ("Curacao", "Curacao"),
        ("Cyprus", "Cyprus"),
        ("Denmark", "Denmark"),
        ("Djibouti", "Djibouti"),
        ("Dominica", "Dominica"),
        ("Dominican Republic", "Dominican Republic"),
        ("Ecuador", "Ecuador"),
        ("Egypt", "Egypt"),
        ("Equatorial Guinea", "Equatorial Guinea"),
        ("Estonia", "Estonia"),
        ("Ethiopia", "Ethiopia"),
        ("Faroe Islands", "Faroe Islands"),
        ("Finland", "Finland"),
        ("France", "France"),
        ("Gabon", "Gabon"),
        ("Georgia", "Georgia"),
        ("Germany", "Germany"),
        ("Ghana", "Ghana"),
        ("Gibraltar", "Gibraltar"),
        ("Greece", "Greece"),
        ("Grenada", "Grenada"),
        ("Guatemala", "Guatemala"),
        ("Guinea", "Guinea"),
        ("Guyana", "Guyana"),
        ("Honduras", "Honduras"),
        ("Hong Kong", "Hong Kong"),
        ("Iceland", "Iceland"),
        ("India", "India"),
        ("Indonesia", "Indonesia"),
        ("Iran", "Iran"),
        ("Iraq", "Iraq"),
        ("Ireland", "Ireland"),
        ("Isle of Man", "Isle of Man"),
        ("Israel", "Israel"),
        ("Italy", "Italy"),
        ("Ivory Coast", "Ivory Coast"),
        ("Jamaica", "Jamaica"),
        ("Japan", "Japan"),
        ("Jordan", "Jordan"),
        ("Kazakhstan", "Kazakhstan"),
        ("Kenya", "Kenya"),
        ("Kiribati", "Kiribati"),
        ("Kuwait", "Kuwait"),
        ("Latvia", "Latvia"),
        ("Lebanon", "Lebanon"),
        ("Liberia", "Liberia"),
        ("Libya", "Libya"),
        ("Lithuania", "Lithuania"),
        ("Luxembourg", "Luxembourg"),
        ("Madagascar", "Madagascar"),
        ("Malaysia", "Malaysia"),
        ("Maldives", "Maldives"),
        ("Malta", "Malta"),
        ("Marshall Islands", "Marshall Islands"),
        ("Mauritania", "Mauritania"),
        ("Mauritius", "Mauritius"),
        ("Mexico", "Mexico"),
        ("Micronesia", "Micronesia"),
        ("Moldova", "Moldova"),
        ("Monaco", "Monaco"),
        ("Mongolia", "Mongolia"),
        ("Montenegro", "Montenegro"),
        ("Morocco", "Morocco"),
        ("Mozambique", "Mozambique"),
        ("Myanmar", "Myanmar"),
        ("Namibia", "Namibia"),
        ("Netherlands", "Netherlands"),
        ("New Zealand", "New Zealand"),
        ("Nicaragua", "Nicaragua"),
        ("Nigeria", "Nigeria"),
        ("North Korea", "North Korea"),
        ("Norway", "Norway"),
        ("Oman", "Oman"),
        ("Pakistan", "Pakistan"),
        ("Palau", "Palau"),
        ("Panama", "Panama"),
        ("Papua New Guinea", "Papua New Guinea"),
        ("Peru", "Peru"),
        ("Philippines", "Philippines"),
        ("Poland", "Poland"),
        ("Portugal", "Portugal"),
        ("Qatar", "Qatar"),
        ("Romania", "Romania"),
        ("Russia", "Russia"),
        ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
        ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"),
        ("Samoa", "Samoa"),
        ("Sao Tome and Principe", "Sao Tome and Principe"),
        ("Saudi Arabia", "Saudi Arabia"),
        ("Senegal", "Senegal"),
        ("Serbia", "Serbia"),
        ("Sierra Leone", "Sierra Leone"),
        ("Singapore", "Singapore"),
        ("Slovenia", "Slovenia"),
        ("Solomon Islands", "Solomon Islands"),
        ("Somalia", "Somalia"),
        ("South Africa", "South Africa"),
        ("South Korea", "South Korea"),
        ("Spain", "Spain"),
        ("Sri Lanka", "Sri Lanka"),
        ("Sudan", "Sudan"),
        ("Suriname", "Suriname"),
        ("Sweden", "Sweden"),
        ("Switzerland", "Switzerland"),
        ("Syria", "Syria"),
        ("Taiwan", "Taiwan"),
        ("Tanzania", "Tanzania"),
        ("Thailand", "Thailand"),
        ("Togo", "Togo"),
        ("Tonga", "Tonga"),
        ("Trinidad and Tobago", "Trinidad and Tobago"),
        ("Tunisia", "Tunisia"),
        ("Turkey", "Turkey"),
        ("Turkmenistan", "Turkmenistan"),
        ("Tuvalu", "Tuvalu"),
        ("Ukraine", "Ukraine"),
        ("United Arab Emirates", "United Arab Emirates"),
        ("United Kingdom", "United Kingdom"),
        ("United States", "United States"),
        ("Uruguay", "Uruguay"),
        ("Vanuatu", "Vanuatu"),
        ("Venezuela", "Venezuela"),
        ("Vietnam", "Vietnam"),
        ("Yemen", "Yemen"),
        ("Zanzibar", "Zanzibar"),
    ]

    flags = [
        {"value": value, "label": label}
        for value, label in FLAGS
    ]
    return Response(flags)


class NextOfKinViewSet(viewsets.ModelViewSet):
    """
    Next of Kin / Emergency Contact - Role-based access:
    - Admin/HR Manager: Full access to all records
    - Recruiter: Read-only access
    - Employee: Full access to their own records only
    """
    queryset = NextOfKin.objects.all()
    serializer_class = NextOfKinSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return NextOfKin.objects.all()
        return NextOfKin.objects.filter(user=user)

    def perform_create(self, serializer):
        if self.request.user.role == 'Employee':
            serializer.save(user=self.request.user)
        else:
            if 'user' not in serializer.validated_data:
                serializer.save(user=self.request.user)
            else:
                serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user.role == 'Employee' and instance.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own emergency contacts")
        if user.role == 'Recruiter':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Recruiters have read-only access")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == 'Recruiter':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Recruiters have read-only access")
        if user.role == 'Employee' and instance.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own emergency contacts")
        instance.delete()


