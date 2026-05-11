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
from core.models import Flag, VesselType, CompanyType

# For Verification Link
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from rest_framework.views import APIView


from .models import (
    Users, Rank, UserRank, Contract, Reference, SeaService, Certificate,
    #Company, Interview, CVSubmission, Document,
    Company, Interview, CVSubmission, Document,
    UserLanguage, PersonalDocument, Declaration, NextOfKin, LanguageProficiency
)
from .serializer import (
    UsersSerializer, UserRankSerializer, ContractSerializer, ContractListSerializer,
    ReferenceSerializer, SeaServiceSerializer, CertificateSerializer, NextOfKinSerializer,
    RankSerializer, RegisterSerializer, UserMeSerializer, DeclarationSerializer,
    CompanySerializer, CompanyListSerializer,
    InterviewSerializer, InterviewCalendarSerializer,
    FinanceRecordSerializer,
    CVSubmissionSerializer, CVSubmissionListSerializer, DocumentSerializer,
    UserLanguageSerializer, PersonalDocumentSerializer, LanguageProficiencySerializer
)
from .filters import (
    UsersFilter, InterviewFilter, FinanceRecordFilter, CVSubmissionFilter, 
    CompanyFilter, ContractFilter, FlightBookingFilter, VisaApplicationFilter,
    AuditFilter, IncidentReportFilter, ShipFilter
)
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


# ========================
# GOOGLE SIGN-IN / SIGN-UP
# ========================

class GoogleAuthView(APIView):
    """
    POST /api/auth/google/
    Body: { "id_token": "<Google ID token from frontend>" }

    Flow:
      1. Frontend uses Google Sign-In SDK to get an id_token.
      2. Frontend sends that token here.
      3. We verify it against Google's public keys.
      4. We find or create the matching Users account.
      5. We return our own Simple JWT access + refresh tokens.

    New users are created with role='Employee' and an unusable password
    (Google is their only login method unless an admin sets a password).
    Existing users whose email already exists will simply get new tokens.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        from django.conf import settings
        from rest_framework_simplejwt.tokens import RefreshToken
        from .serializer import GoogleAuthSerializer

        # 1. Validate request body
        serializer = GoogleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_token = serializer.validated_data['id_token']

        # 2. Verify the Google ID token
        try:
            client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
            if not client_id or client_id == 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com':
                return Response(
                    {"error": "Google OAuth2 is not configured on this server. Please set GOOGLE_OAUTH2_CLIENT_ID in settings."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            idinfo = google_id_token.verify_oauth2_token(
                raw_token,
                google_requests.Request(),
                client_id
            )
        except ValueError as e:
            # Token is invalid or expired
            return Response(
                {"error": f"Invalid Google token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Google token verification failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Extract user info from the verified payload
        google_email = idinfo.get('email')
        google_first_name = idinfo.get('given_name') or idinfo.get('name', '').split(' ')[0] or 'User'
        google_middle_name = idinfo.get('family_name', '')
        google_picture = idinfo.get('picture', '')
        email_verified = idinfo.get('email_verified', False)

        if not google_email:
            return Response(
                {"error": "Google account does not have a verified email address."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not email_verified:
            return Response(
                {"error": "Google email address is not verified. Please verify your Google account email first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Get or create the user
        user, created = Users.objects.get_or_create(
            email=google_email,
            defaults={
                'first_name': google_first_name,
                'middle_name': google_middle_name,
                'role': 'Employee',
                'is_active': True,
            }
        )

        if created:
            # New user — set an unusable password (Google is the auth method)
            user.set_unusable_password()
            # Optionally fetch and save the profile picture
            if google_picture:
                import urllib.request
                import os
                from django.core.files.base import ContentFile
                try:
                    with urllib.request.urlopen(google_picture) as resp:
                        image_data = resp.read()
                        ext = 'jpg'
                        filename = f"google_{user.id}.{ext}"
                        user.profile_image.save(filename, ContentFile(image_data), save=False)
                except Exception:
                    pass  # Don't block sign-in if the picture download fails
            user.save()

        elif not user.is_active:
            return Response(
                {"error": "Your account has been deactivated. Please contact the administrator."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 5. Issue our own JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "created": created,  # True = new account, False = existing account
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "middle_name": user.middle_name,
                "role": user.role,
                "profile_image": request.build_absolute_uri(user.profile_image.url) if user.profile_image else None,
            }
        }, status=status.HTTP_200_OK)


class LanguageProficiencyViewSet(viewsets.ModelViewSet):
    serializer_class = LanguageProficiencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This ensures users can ONLY see, edit, or delete 
        their own language records.
        """
        return LanguageProficiency.objects.filter(user=self.request.user)

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
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        if not user.marlins_test_attachment:
            return Response({'error': 'No Marlins test file uploaded'}, status=404)
        file_path = user.marlins_test_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-ces')
    def download_ces(self, request, pk=None):
        """Download CES test attachment"""
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        if not user.ces_test_attachment:
            return Response({'error': 'No CES test file uploaded'}, status=404)
        file_path = user.ces_test_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found'}, status=404)

    # ============================
    # HELPER: Owner or Admin check
    # ============================

    def _check_download_permission(self, request, pk):
        """
        Returns the target User object if the caller is the owner or an Admin.
        Otherwise returns a 403 Response.
        """
        user = self.get_object()  # triggers DRF object-level perm check
        if request.user.role != 'Admin' and user != request.user:
            return Response({'error': 'Permission denied. Only the profile owner or Admin can download.'}, status=403)
        return user

    # ============================
    # TRAVEL DOCUMENT DOWNLOADS
    # ============================

    @action(detail=True, methods=['get'], url_path='download-passport')
    def download_passport(self, request, pk=None):
        """
        Download passport attachment.
        GET /api/users/{id}/download-passport/
        Permission: Own profile or Admin only.
        """
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        if not user.passport_attachment:
            return Response({'error': 'No passport file uploaded'}, status=404)
        file_path = user.passport_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-seaman-book')
    def download_seaman_book(self, request, pk=None):
        """
        Download seaman book attachment.
        GET /api/users/{id}/download-seaman-book/
        Permission: Own profile or Admin only.
        """
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        if not user.seaman_book_attachment:
            return Response({'error': 'No seaman book file uploaded'}, status=404)
        file_path = user.seaman_book_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-other-seaman-book')
    def download_other_seaman_book(self, request, pk=None):
        """
        Download other/second seaman book attachment.
        GET /api/users/{id}/download-other-seaman-book/
        Permission: Own profile or Admin only.
        """
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        if not user.other_seaman_book_attachment:
            return Response({'error': 'No other seaman book file uploaded'}, status=404)
        file_path = user.other_seaman_book_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-personal-document/(?P<doc_id>[^/.]+)')
    def download_personal_document(self, request, pk=None, doc_id=None):
        """
        Download a specific PersonalDocument (travel/ID document) by its ID.
        GET /api/users/{user_id}/download-personal-document/{doc_id}/
        Permission: Own profile or Admin only.
        """
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        doc = user.personal_documents.filter(id=doc_id).first()
        if not doc:
            return Response({'error': f'Personal document #{doc_id} not found for this user'}, status=404)
        if not doc.file:
            return Response({'error': 'No file attached to this document'}, status=404)
        file_path = doc.file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    # ============================
    # CERTIFICATE DOWNLOADS
    # ============================

    @action(detail=True, methods=['get'], url_path='download-license/(?P<license_id>[^/.]+)')
    def download_license(self, request, pk=None, license_id=None):
        """
        Download a specific license/certificate document by its ID.
        GET /api/users/{user_id}/download-license/{license_id}/
        Permission: Own profile or Admin only.
        Covers: COC, GOC, and all STCW license documents.
        """
        from licenses.models import UserLicense
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        lic = UserLicense.objects.filter(id=license_id, user=user).first()
        if not lic:
            return Response({'error': f'License #{license_id} not found for this user'}, status=404)
        if not lic.document_file:
            return Response({'error': 'No file attached to this license'}, status=404)
        file_path = lic.document_file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    # ============================
    # MEDICAL / HEALTH DOWNLOADS
    # ============================

    @action(detail=True, methods=['get'], url_path='download-vaccination/(?P<vaccination_id>[^/.]+)')
    def download_vaccination(self, request, pk=None, vaccination_id=None):
        """
        Download a specific vaccination/medical document by its ID.
        GET /api/users/{user_id}/download-vaccination/{vaccination_id}/
        Permission: Own profile or Admin only.
        Covers: Yellow Fever, COVID, Medical Certificate for Seafarers, etc.
        """
        from vaccinations.models import Vaccination
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        vac = Vaccination.objects.filter(id=vaccination_id, user=user).first()
        if not vac:
            return Response({'error': f'Vaccination #{vaccination_id} not found for this user'}, status=404)
        if not vac.document:
            return Response({'error': 'No file attached to this vaccination record'}, status=404)
        file_path = vac.document.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    # ============================
    # MARINE COURSE DOWNLOADS
    # ============================

    @action(detail=True, methods=['get'], url_path='download-course/(?P<course_id>[^/.]+)')
    def download_course(self, request, pk=None, course_id=None):
        """
        Download a specific marine course document by its ID.
        GET /api/users/{user_id}/download-course/{course_id}/
        Permission: Own profile or Admin only.
        """
        from courses.models import Course
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        course = Course.objects.filter(id=course_id, user=user).first()
        if not course:
            return Response({'error': f'Course #{course_id} not found for this user'}, status=404)
        if not course.document:
            return Response({'error': 'No document attached to this course'}, status=404)
        file_path = course.document.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    # ============================
    # SEA-SERVICE DOWNLOADS
    # ============================

    @action(detail=True, methods=['get'], url_path='download-sea-service/(?P<service_id>[^/.]+)')
    def download_sea_service(self, request, pk=None, service_id=None):
        """
        Download a specific sea service record file by its ID.
        GET /api/users/{user_id}/download-sea-service/{service_id}/
        Permission: Own profile or Admin only.
        """
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user
        service = user.sea_services.filter(id=service_id).first()
        if not service:
            return Response({'error': f'Sea service #{service_id} not found for this user'}, status=404)
        if not service.file:
            return Response({'error': 'No file attached to this sea service record'}, status=404)
        file_path = service.file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    # ============================
    # GENERIC DOWNLOAD (all user-level attachments)
    # ============================

    @action(detail=True, methods=['get'], url_path='download-document')
    def download_user_document(self, request, pk=None):
        """
        Download any user-level file attachment by type.
        GET /api/users/{id}/download-document/?type=<doc_type>

        Supported types:
          passport, seaman_book, other_seaman_book, marlins, ces, profile_image, file
        Permission: Own profile or Admin only.
        """
        user = self._check_download_permission(request, pk)
        if isinstance(user, Response):
            return user

        FILE_MAP = {
            'passport': user.passport_attachment,
            'seaman_book': user.seaman_book_attachment,
            'other_seaman_book': user.other_seaman_book_attachment,
            'marlins': user.marlins_test_attachment,
            'ces': user.ces_test_attachment,
            'profile_image': user.profile_image,
            'file': user.file,
        }

        doc_type = request.query_params.get('type', '').strip()
        if not doc_type:
            return Response(
                {'error': f'Missing ?type= parameter. Choices: {list(FILE_MAP.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if doc_type not in FILE_MAP:
            return Response(
                {'error': f'Unknown type "{doc_type}". Choices: {list(FILE_MAP.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_field = FILE_MAP[doc_type]
        if not file_field:
            return Response(
                {'error': f'No file uploaded for document type "{doc_type}"'},
                status=status.HTTP_404_NOT_FOUND
            )

        file_path = file_field.path
        if not os.path.exists(file_path):
            return Response(
                {'error': 'File record exists but the file was not found on the server'},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(file_path)
        )


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
    filterset_class = ContractFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        return ContractSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Contract.objects.select_related('user', 'ship', 'company', 'rank').all()
        return Contract.objects.filter(user=user)

    def perform_destroy(self, instance):
        if instance.job_position:
            instance.job_position.quantity += 1
            instance.job_position.save(update_fields=['quantity'])
            
        # If the applicant was assigned to the ship's crew for this contract, remove them
        if instance.ship and instance.user:
            instance.ship.crew.remove(instance.user)
            
        # Also clean up related CV Submissions
        if instance.user:
            from api.models import CVSubmission
            cvs = CVSubmission.objects.filter(user=instance.user)
            
            for cv in cvs:
                update_fields = []
                if instance.ship and cv.ship == instance.ship:
                    cv.ship = None
                    update_fields.append('ship')
                if instance.company and cv.company == instance.company:
                    cv.company = None
                    update_fields.append('company')
                
                if update_fields:
                    cv.save(update_fields=update_fields)
            
        super().perform_destroy(instance)

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

    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        """Get contract counts by status"""
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            contracts = Contract.objects.all()
        else:
            contracts = Contract.objects.filter(user=request.user)
        
        return Response({
            'active': contracts.filter(status='Active').count(),
            'completed': contracts.filter(status='Completed').count(),
            'pending': contracts.filter(status='Pending').count(),
            'signed': contracts.filter(status='Signed').count(),
            'pending_signature': contracts.filter(status='Pending Signature').count(),
            'draft': contracts.filter(status='Draft').count(),
            'cancelled': contracts.filter(status='Cancelled').count(),
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
        # Employee can only submit CV for themselves
        if self.request.user.role == 'Employee':
            serializer.save(user=self.request.user)
        else:
            if 'user' not in serializer.validated_data:
                serializer.save(user=self.request.user)
            else:
                serializer.save()

    def perform_destroy(self, instance):
        # If the applicant was assigned to the ship's crew for this CV submission, remove them
        if instance.ship and instance.user:
            instance.ship.crew.remove(instance.user)
        super().perform_destroy(instance)

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

    @action(detail=True, methods=['get'], url_path='download-document')
    def download_document(self, request, pk=None):
        """
        Download a file attachment from the user linked to this CV submission.

        GET /api/cv-submissions/{id}/download-document/?type=<doc_type>

        Supported types:
          passport          → user.passport_attachment
          seaman_book       → user.seaman_book_attachment
          other_seaman_book → user.other_seaman_book_attachment
          marlins           → user.marlins_test_attachment
          ces               → user.ces_test_attachment
        """
        cv = self.get_object()
        user = cv.user

        FILE_MAP = {
            'passport':          user.passport_attachment,
            'seaman_book':        user.seaman_book_attachment,
            'other_seaman_book':  user.other_seaman_book_attachment,
            'marlins':            user.marlins_test_attachment,
            'ces':                user.ces_test_attachment,
        }

        doc_type = request.query_params.get('type', '').strip()
        if not doc_type:
            return Response(
                {'error': f'Missing ?type= parameter. Choices: {list(FILE_MAP.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if doc_type not in FILE_MAP:
            return Response(
                {'error': f'Unknown type "{doc_type}". Choices: {list(FILE_MAP.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_field = FILE_MAP[doc_type]
        if not file_field:
            return Response(
                {'error': f'No file uploaded for document type "{doc_type}"'},
                status=status.HTTP_404_NOT_FOUND
            )

        file_path = file_field.path
        if not os.path.exists(file_path):
            return Response(
                {'error': 'File record exists but the file was not found on the server'},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(file_path)
        )


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

            # Auto-create CVSubmission so the approved employee appears in the CV Submissions board
            if document.position:
                from .models import Rank, CVSubmission, RANKS
                # Ensure rank exists
                rank = Rank.objects.filter(name__iexact=document.position).first()
                if not rank:
                    code = None
                    for c, n in RANKS:
                        if n.lower() == document.position.lower():
                            code = c
                            break
                    if not code:
                        import uuid
                        code = f"CUS-{str(uuid.uuid4())[:6].upper()}"
                    rank = Rank.objects.create(code=code, name=document.position)
                
                # Create the submission if it doesn't exist
                # Include the company from the document so it links to the right job order company
                submission, created = CVSubmission.objects.get_or_create(
                    user=user,
                    position=rank,
                    company=getattr(document, 'company', None),
                    job_position=getattr(document, 'job_position', None),
                    defaults={
                        'cv_file': document.file,
                        'status': 'Approved',
                        'notes': 'Auto-created from Approved Document'
                    }
                )
                
                # Auto-assign UserRank (from our previous logic)
                from api.models import UserRank
                UserRank.objects.get_or_create(user=user, rank=rank)            # Send acceptance email
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

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Document statistics for Quick Appliers dashboard"""
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            docs = Document.objects.all()
        else:
            docs = Document.objects.filter(user=request.user)
        
        total = docs.count()
        return Response({
            'total_applications': total,
            'pending_applications': docs.filter(status='Pending').count(),
            'active_applications': docs.filter(status='Active').count(),
            'blacklist_applications': docs.filter(status='Blacklist').count(),
        })

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

    @action(detail=False, methods=['get'], url_path='all', permission_classes=[IsAuthenticated])
    def all_ranks(self, request):
        """
        GET /api/ranks/all/
        Returns a flat, unpaginated list of all ranks.
        Intended for populating position dropdowns in forms.
        Response: [ {id, code, name}, ... ]
        """
        ranks = Rank.objects.all().order_by('name')
        serializer = RankSerializer(ranks, many=True)
        return Response(serializer.data)


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
# POSITION → CODED RANK BRIDGE
# =====================

# Maps human-readable position names (from Document.POSITION_CHOICES)
# to short rank codes used to auto-generate assigned_code (e.g. 'MST.001')
POSITION_CODE_MAP = {
    'Master':                                              'MST',
    '1st. Officer – Chief Off.':                           '1ST_OFF',
    '2nd. Officer':                                        '2ND_OFF',
    '3rd. Officer':                                        '3RD_OFF',
    'Tug Master':                                          'TUG_MST',
    'Boson':                                               'BSN',
    'A.B – O.S':                                           'AB_OS',
    'Steward / Galley Boy':                                'STW',
    'Cook / 2nd. Cook / Ass. Cook / Baker / Pastry':       'COOK',
    'Carpenter':                                           'CARP',
    'Waiter':                                              'WTR',
    'Purser':                                              'PUR',
    'Doctor':                                              'DOC',
    '1st. Engineer':                                       '1ST_ENG',
    '2nd. Engineer':                                       '2ND_ENG',
    '3rd. Engineer':                                       '3RD_ENG',
    'Electrical Engineer – E/E – ETO':                     'ETO',
    'Assistant Electrician':                               'ASS_ELC',
    '4th. Engineer':                                       '4TH_ENG',
    'Electrician':                                         'ELC',
    'Motor Man / Mechanic':                                'MTR_MAN',
    'Oiler':                                               'OLR',
    'Fitter – Welder':                                     'FTR',
    'Wiper':                                               'WPR',
    'Other':                                               'OTH',
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_rank_by_position(request, user_id):
    """
    Assign a coded rank to a user based on a position name from /api/positions/.

    Admin/HR Manager only.

    POST /api/users/{user_id}/assign-by-position/
    Body: { "position": "Master" }

    Flow:
      1. Validates position is a known POSITION_CHOICES value.
      2. Maps it to a short rank code (e.g. 'Master' → 'MST').
      3. Gets or creates the Rank object in the DB.
      4. Creates a UserRank → assigned_code is AUTO-GENERATED (e.g. 'MST.001').
      5. Returns the full UserRank data.
    """
    if request.user.role not in ['Admin', 'HR Manager']:
        return Response({'error': 'Permission denied. Admin or HR Manager only.'}, status=status.HTTP_403_FORBIDDEN)

    # Validate user exists
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate position in request body
    position_name = request.data.get('position', '').strip()
    if not position_name:
        return Response(
            {'error': 'position is required.', 'hint': 'Use GET /api/positions/ to see all valid choices.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check position is a valid choice
    valid_positions = [choice[0] for choice in Document.POSITION_CHOICES]
    if position_name not in valid_positions:
        return Response(
            {
                'error': f'"{position_name}" is not a valid position.',
                'valid_positions': valid_positions,
                'hint': 'Use GET /api/positions/ to get the full list.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Map position name → short rank code
    rank_code = POSITION_CODE_MAP.get(position_name, position_name[:6].upper().replace(' ', '_'))

    # Get or create the Rank object
    rank, created = Rank.objects.get_or_create(
        code=rank_code,
        defaults={'name': position_name}
    )

    # Prevent duplicate assignment
    if UserRank.objects.filter(user=user, rank=rank).exists():
        existing = UserRank.objects.get(user=user, rank=rank)
        return Response(
            {
                'error': f'User already has the rank "{position_name}".',
                'existing_assigned_code': existing.assigned_code
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create UserRank — assigned_code is auto-generated in UserRank.save()
    user_rank = UserRank.objects.create(user=user, rank=rank)

    from .serializer import UserRankSerializer
    serializer = UserRankSerializer(user_rank)

    return Response(
        {
            'message': f"Rank '{position_name}' successfully assigned to {user.first_name} {user.middle_name}.",
            'rank_created_in_db': created,
            'user_rank': serializer.data
        },
        status=status.HTTP_201_CREATED
    )
    

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
        user = self.request.user
        if user.role in ['Admin', 'HR Manager']:
            return UserLanguage.objects.all()
        return UserLanguage.objects.filter(user=user)

    # def get_queryset(self):
    #     return UserLanguage.objects.all()

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
    Return all available positions (Ranks).
    Accessible by any authenticated user.
    GET /api/positions/
    """
    ranks = Rank.objects.all().order_by('name')
    if ranks.exists():
        seen_names = set()
        positions = []
        for r in ranks:
            # Strip whitespace to handle hidden duplicates
            name_key = r.name.strip() if r.name else ""
            if name_key and name_key not in seen_names:
                positions.append({"value": r.id, "label": r.name, "code": r.code})
                seen_names.add(name_key)
    else:
        # Fallback to hardcoded choices if Rank table is empty
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
    Return all available maritime flag states from dynamic core.models.Flag.
    Accessible by any authenticated user.
    GET /api/flags/
    """
    db_flags = Flag.objects.all().order_by('name')
    if db_flags.exists():
        return Response([
            {"value": f.id, "label": f.name, "icon": f.icon.url if f.icon else None}
            for f in db_flags
        ])

    # Legacy fallback if DB is empty
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
    return Response([{"value": val, "label": lab} for val, lab in FLAGS])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vessel_types(request):
    """Return all available vessel types from dynamic core.models.VesselType."""
    types = VesselType.objects.all().order_by('name')
    return Response([{"value": t.id, "label": t.name} for t in types])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company_types(request):
    """Return all available company types from dynamic core.models.CompanyType."""
    types = CompanyType.objects.all().order_by('name')
    return Response([{"value": t.id, "label": t.name} for t in types])


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


