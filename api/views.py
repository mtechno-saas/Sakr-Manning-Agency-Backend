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
from django.http import FileResponse, HttpResponseRedirect, HttpResponse
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
            # Redirect to user form
            return HttpResponseRedirect("https://test.sakrshipping.com/form")
        else:
            return HttpResponseRedirect("https://test.sakrshipping.com/auth?error=invalid_token")


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
      3. GoogleTokenSerializer verifies it against Google's public keys.
      4. GoogleUserService finds or creates the matching Users account.
      5. JWTTokenService issues our own Simple JWT access + refresh tokens.

    New users are created with role='Employee' and an unusable password
    (Google is their only login method unless an admin sets a password).
    Existing users whose email already exists are returned as-is.

    Responses
    ---------
    200 OK  â€” { access, refresh, user: { id, email, first_name, middle_name, role } }
    400 BAD REQUEST â€” invalid / unverified / missing token
    403 FORBIDDEN   â€” account is deactivated
    503 UNAVAILABLE â€” OAuth not configured on this server
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from .google_auth_serializer import GoogleTokenSerializer
        from .google_user_service import GoogleUserService
        from .jwt_token_service import JWTTokenService

        # Step 1 â€” Validate & verify the Google ID token
        serializer = GoogleTokenSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors.get("id_token", serializer.errors)
            # Distinguish between a configuration error and a bad token
            error_str = str(errors)
            if "not configured" in error_str:
                return Response(
                    {"error": error_str},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            return Response(
                {"error": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_payload: dict = serializer.google_payload

        # Step 2 â€” Resolve (or create) the local user
        user, created = GoogleUserService.get_or_create_user_from_google(google_payload)

        if not user.is_active:
            return Response(
                {"error": "Your account has been deactivated. Please contact the administrator."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Step 3 â€” Issue JWT tokens
        tokens: dict = JWTTokenService.get_tokens_for_user(user)

        return Response(
            {
                **tokens,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "middle_name": user.middle_name,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


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
        if not user or not user.is_authenticated:
            return Users.objects.none()
        if user.is_superuser or user.role in ['Admin', 'HR Manager', 'Recruiter', 'admin']:
            return Users.objects.all()
        # Employee can only see themselves
        return Users.objects.filter(id=user.id)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        user_ids = request.data.get('ids', [])
        if not user_ids:
            return Response({'error': 'No ids provided'}, status=400)
        
        if request.user.role not in ['Admin', 'HR Manager']:
            return Response({'error': 'Permission denied'}, status=403)
            
        Users.objects.filter(id__in=user_ids).delete()
        return Response({'message': f'Successfully deleted {len(user_ids)} users'})

    @action(detail=False, methods=['post'], url_path='bulk-edit')
    def bulk_edit(self, request):
        user_ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})
        if not user_ids:
            return Response({'error': 'No ids provided'}, status=400)
            
        if request.user.role not in ['Admin', 'HR Manager']:
            return Response({'error': 'Permission denied'}, status=403)

        allowed_fields = ['user_status', 'role', 'status', 'is_active', 'is_blacklisted']
        clean_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        # Handle rank assignment separately if provided
        rank_position = update_data.get('rank')
        
        if not clean_data and not rank_position:
            return Response({'error': 'No valid fields provided for update'}, status=400)

        users_to_update = Users.objects.filter(id__in=user_ids)
        
        if clean_data:
            users_to_update.update(**clean_data)
            
        if rank_position:
            # Replicate the logic from assign_rank_by_position
            from companies.models import JobOrderPosition
            try:
                # In assign_rank_by_position we look up Rank or create it
                # The user provides a position name like "Master"
                from api.models import Rank, UserRank
                
                # Fetch position short code from JobOrderPosition if possible, else use first 3 chars
                position_obj = JobOrderPosition.objects.filter(title__iexact=rank_position).first()
                if position_obj and position_obj.rank_code:
                    short_code = position_obj.rank_code
                else:
                    short_code = rank_position[:3].upper()
                
                rank, created = Rank.objects.get_or_create(
                    name=rank_position,
                    defaults={'code': short_code}
                )
                
                for user in users_to_update:
                    prefix = rank.code.split('.')[0] if '.' in rank.code else rank.code
                    last_ur = UserRank.objects.filter(rank__code__startswith=prefix).order_by('-assigned_code').first()
                    
                    next_num = 1
                    if last_ur and last_ur.assigned_code:
                        try:
                            last_num = int(last_ur.assigned_code.split('.')[-1])
                            next_num = last_num + 1
                        except (ValueError, IndexError):
                            pass
                    
                    new_assigned_code = f"{prefix}.{next_num:03d}"
                    UserRank.objects.create(
                        user=user,
                        rank=rank,
                        assigned_code=new_assigned_code
                    )
            except Exception as e:
                # Log error but don't fail the whole bulk edit if basic fields were updated
                print("Bulk Rank Update Error:", e)

        return Response({'message': f'Successfully updated {len(user_ids)} users'})

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
            'crew': users.filter(role='Crew').count(),
            'active_users': users.filter(is_active=True).count(),
        })

    @action(detail=True, methods=['get'], url_path='full-profile')
    def full_profile(self, request, pk=None):
        """
        Get the applicant's complete profile including documents, sea service, and all signed contracts.
        Combines the UsersSerializer response with the ContractListSerializer response.
        """
        user = self.get_object()
        
        # Get base user profile (includes sea_services and user_documents)
        user_data = self.get_serializer(user).data
        
        # Get all contracts for this user
        contracts = Contract.objects.filter(user=user).select_related('ship', 'company', 'rank')
        contracts_data = ContractListSerializer(contracts, many=True, context={'request': request}).data
        
        # Combine the data
        user_data['contracts'] = contracts_data
        
        return Response(user_data)

    @action(detail=True, methods=['get'], url_path='download-full-profile-pdf',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_full_profile_pdf(self, request, pk=None):
        """
        Download the full profile (with sea services, documents, and contracts) as a structured PDF.
        GET /api/users/{id}/download-full-profile-pdf/
        NOTE: AllowAny because the frontend opens this in a new tab without auth headers.
        """
        import traceback
        try:
            user = get_object_or_404(Users, pk=pk)
            
            # Get base user profile
            user_data = UsersSerializer(user, context={'request': request}).data
            
            # Get all contracts
            contracts = Contract.objects.filter(user=user).select_related('ship', 'company', 'rank')
            user_data['contracts'] = ContractListSerializer(contracts, many=True, context={'request': request}).data
            
            # Generate PDF
            from api.pdf_generator import generate_full_profile_pdf
            logo_path = os.path.join(settings.BASE_DIR, 'logo.png') 
            
            pdf_bytes = generate_full_profile_pdf(user_data, logo_path=logo_path)
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="applicant_profile_{user.id}.pdf"'
            return response
        except Exception as e:
            tb = traceback.format_exc()
            return Response({'error': str(e), 'traceback': tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='download-marlins',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_marlins(self, request, pk=None):
        """Download Marlins test attachment"""
        user = get_object_or_404(Users, pk=pk)
        if not user.marlins_test_attachment:
            return Response({'error': 'No Marlins test file uploaded'}, status=404)
        file_path = user.marlins_test_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-ces',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_ces(self, request, pk=None):
        """Download CES test attachment"""
        user = get_object_or_404(Users, pk=pk)
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
        Returns the target User object if the caller is the owner or an Admin/HR/Recruiter.
        Otherwise returns a 403 Response.
        """
        user = self.get_object()  # triggers DRF object-level perm check
        has_permission = request.user.is_authenticated and (
            getattr(request.user, 'role', '') in ['Admin', 'HR Manager', 'Recruiter', 'admin'] or 
            getattr(request.user, 'is_superuser', False)
        )
        if not has_permission and user != request.user:
            return Response({'error': 'Permission denied. Only the profile owner or privileged users can download.'}, status=403)
        return user

    # ============================
    # TRAVEL DOCUMENT DOWNLOADS
    # ============================

    @action(detail=True, methods=['get'], url_path='download-passport',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_passport(self, request, pk=None):
        """
        Download passport attachment.
        GET /api/users/{id}/download-passport/
        Permission: Own profile or Admin only.
        """
        user = get_object_or_404(Users, pk=pk)
        if not user.passport_attachment:
            return Response({'error': 'No passport file uploaded'}, status=404)
        file_path = user.passport_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-seaman-book',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_seaman_book(self, request, pk=None):
        """
        Download seaman book attachment.
        GET /api/users/{id}/download-seaman-book/
        Permission: Own profile or Admin only.
        """
        user = get_object_or_404(Users, pk=pk)
        if not user.seaman_book_attachment:
            return Response({'error': 'No seaman book file uploaded'}, status=404)
        file_path = user.seaman_book_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-other-seaman-book',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_other_seaman_book(self, request, pk=None):
        """
        Download other/second seaman book attachment.
        GET /api/users/{id}/download-other-seaman-book/
        Permission: Own profile or Admin only.
        """
        user = get_object_or_404(Users, pk=pk)
        if not user.other_seaman_book_attachment:
            return Response({'error': 'No other seaman book file uploaded'}, status=404)
        file_path = user.other_seaman_book_attachment.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-personal-document/(?P<doc_id>[^/.]+)',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_personal_document(self, request, pk=None, doc_id=None):
        """
        Download a specific PersonalDocument (travel/ID document) by its ID.
        GET /api/users/{user_id}/download-personal-document/{doc_id}/
        Permission: Own profile or Admin only.
        """
        user = get_object_or_404(Users, pk=pk)
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

    @action(detail=True, methods=['get'], url_path='download-license/(?P<license_id>[^/.]+)',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_license(self, request, pk=None, license_id=None):
        """
        Download a specific license/certificate document by its ID.
        GET /api/users/{user_id}/download-license/{license_id}/
        Permission: Own profile or Admin only.
        Covers: COC, GOC, and all STCW license documents.
        """
        from licenses.models import UserLicense
        user = get_object_or_404(Users, pk=pk)
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

    @action(detail=True, methods=['get'], url_path='download-vaccination/(?P<vaccination_id>[^/.]+)',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_vaccination(self, request, pk=None, vaccination_id=None):
        """
        Download a specific vaccination/medical document by its ID.
        GET /api/users/{user_id}/download-vaccination/{vaccination_id}/
        Permission: Own profile or Admin only.
        Covers: Yellow Fever, COVID, Medical Certificate for Seafarers, etc.
        """
        from vaccinations.models import Vaccination
        user = get_object_or_404(Users, pk=pk)
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

    @action(detail=True, methods=['get'], url_path='download-course/(?P<course_id>[^/.]+)',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_course(self, request, pk=None, course_id=None):
        """
        Download a specific marine course document by its ID.
        GET /api/users/{user_id}/download-course/{course_id}/
        Permission: Own profile or Admin only.
        """
        from courses.models import Course
        user = get_object_or_404(Users, pk=pk)
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

    @action(detail=True, methods=['get'], url_path='download-sea-service/(?P<service_id>[^/.]+)',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_sea_service(self, request, pk=None, service_id=None):
        """
        Download a specific sea service record file by its ID.
        GET /api/users/{user_id}/download-sea-service/{service_id}/
        Permission: Own profile or Admin only.
        """
        user = get_object_or_404(Users, pk=pk)
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

    @action(detail=True, methods=['get'], url_path='download-document',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_user_document(self, request, pk=None):
        """
        Download any user-level file attachment by type.
        GET /api/users/users/{id}/download-document/?type=<doc_type>&doc_id=<id>

        Supported types:
          Singleton (no doc_id needed):
            passport, seaman_book, other_seaman_book, marlins, ces, profile_image, file, coc, goc, health_certificate
          Related (doc_id required):
            license, sea_service, course, vaccination, personal_document

        NOTE: AllowAny because the frontend renders these as plain <a href> links
        that open in a new tab without auth headers. Media files are already public.
        """
        user = get_object_or_404(Users, pk=pk)

        doc_type = request.query_params.get('type', '').strip()
        doc_id = request.query_params.get('doc_id')
        if not doc_type:
            return Response(
                {'error': 'Missing ?type= parameter.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_path = None

        # 1. User-level singleton attachments
        USER_FILE_MAP = {
            'passport': user.passport_attachment,
            'seaman_book': user.seaman_book_attachment,
            'other_seaman_book': user.other_seaman_book_attachment,
            'marlins': user.marlins_test_attachment,
            'ces': user.ces_test_attachment,
            'profile_image': user.profile_image,
            'file': user.file,
        }

        if doc_type in USER_FILE_MAP:
            file_field = USER_FILE_MAP[doc_type]
            if not file_field:
                return Response({'error': f'No file uploaded for document type "{doc_type}"'}, status=404)
            file_path = file_field.path

        elif doc_type == 'coc':
            from licenses.models import UserLicense
            lic = UserLicense.objects.filter(user=user, document_name__icontains='coc').first()
            if not lic or not lic.document_file:
                return Response({'error': 'No COC file uploaded'}, status=404)
            file_path = lic.document_file.path

        elif doc_type == 'goc':
            from licenses.models import UserLicense
            lic = UserLicense.objects.filter(user=user, document_name__icontains='goc').first()
            if not lic or not lic.document_file:
                return Response({'error': 'No GOC file uploaded'}, status=404)
            file_path = lic.document_file.path

        elif doc_type == 'health_certificate':
            from vaccinations.models import Vaccination
            vac = Vaccination.objects.filter(user=user, name="Medical Certificate For Seafarers").first()
            if not vac or not vac.document:
                return Response({'error': 'No Medical Certificate file uploaded'}, status=404)
            file_path = vac.document.path

        # 2. Related model attachments (require doc_id)
        elif doc_type in ['sea_service', 'vaccination', 'course', 'personal_document', 'license']:
            if not doc_id:
                return Response({'error': f'doc_id is required for type "{doc_type}"'}, status=400)

            if doc_type == 'sea_service':
                doc = user.sea_services.filter(id=doc_id).first()
                file_field = getattr(doc, 'file', None)
            elif doc_type == 'vaccination':
                from vaccinations.models import Vaccination
                doc = Vaccination.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'document', None)
            elif doc_type == 'course':
                from courses.models import Course
                doc = Course.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'document', None)
            elif doc_type == 'personal_document':
                from api.models import PersonalDocument
                doc = PersonalDocument.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'file', None)
            elif doc_type == 'license':
                from licenses.models import UserLicense
                doc = UserLicense.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'document_file', None)

            if not doc:
                return Response({'error': f'Document #{doc_id} of type "{doc_type}" not found for this user'}, status=404)
            if not file_field:
                return Response({'error': f'No file attached to this {doc_type} record'}, status=404)

            file_path = file_field.path

        else:
            all_choices = list(USER_FILE_MAP.keys()) + ['coc', 'goc', 'health_certificate', 'sea_service', 'vaccination', 'course', 'personal_document', 'license']
            return Response(
                {'error': f'Unknown type "{doc_type}". Choices: {all_choices}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Serve the file
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
        # Automatically transition expired contracts to 'Draft' status
        today = timezone.now().date()
        
        # Performance Guard: Only run the update query once per day
        last_update_date = cache.get('last_contract_expiry_check')
        
        if last_update_date != today:
            # Find all contracts that have passed their sign-off date but are still in active states
            expired_contracts = Contract.objects.filter(
                sign_off_date__lt=today,
                status__in=['Active', 'Signed', 'Pending Signature', 'Pending']
            )
            
            # Bulk update to Draft
            if expired_contracts.exists():
                expired_contracts.update(status='Draft')
            
            # Cache the check for 24 hours
            cache.set('last_contract_expiry_check', today, 86400)

        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return Contract.objects.select_related('user', 'ship', 'company', 'rank').all()
        return Contract.objects.filter(user=user)

    def perform_destroy(self, instance):
        if instance.job_position:
            instance.job_position.quantity += 1
            instance.job_position.save(update_fields=['quantity'])
            
            # Restore company's open_positions
            if instance.company:
                instance.company.open_positions += 1
                instance.company.save(update_fields=['open_positions'])
            
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
    queryset = CVSubmission.objects.select_related('user', 'position', 'company', 'ship', 'ship__ship_type', 'ship__flag').all()
    permission_classes = [IsAuthenticated, CVPermission]
    filterset_class = CVSubmissionFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return CVSubmissionListSerializer
        return CVSubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return CVSubmission.objects.select_related('user', 'position', 'company', 'ship', 'ship__ship_type', 'ship__flag').all()
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

    @action(detail=True, methods=['get'], url_path='download-cv',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_cv(self, request, pk=None):
        """
        Download the CV file associated with this submission.
        GET /api/cv-submissions/{id}/download-cv/
        """
        cv = get_object_or_404(CVSubmission, pk=pk)
        if not cv.cv_file:
            return Response({'error': 'No CV file attached to this submission'}, status=404)
        file_path = cv.cv_file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return Response({'error': 'File not found on server'}, status=404)

    @action(detail=True, methods=['get'], url_path='download-document',
            permission_classes=[AllowAny], authentication_classes=[])
    def download_document(self, request, pk=None):
        """
        Download a file attachment from the user linked to this CV submission.

        GET /api/cv-submissions/{id}/download-document/?type=<doc_type>&doc_id=<id>

        Supported types:
          passport          â†’ user.passport_attachment
          seaman_book       â†’ user.seaman_book_attachment
          other_seaman_book â†’ user.other_seaman_book_attachment
          marlins           â†’ user.marlins_test_attachment
          ces               â†’ user.ces_test_attachment
          sea_service       â†’ SeaService.objects.get(id=doc_id)
          vaccination       â†’ Vaccination.objects.get(id=doc_id)
          course            â†’ Course.objects.get(id=doc_id)
          personal_document â†’ PersonalDocument.objects.get(id=doc_id)

        NOTE: AllowAny because the frontend renders these as plain <a href> links
        that open in a new tab without auth headers. Media files are already public.
        """
        cv = get_object_or_404(CVSubmission, pk=pk)
        user = cv.user
        doc_type = request.query_params.get('type', '').strip()
        doc_id = request.query_params.get('doc_id')

        # 1. Handle user-level attachments (one-to-one with User)
        USER_FILE_MAP = {
            'passport':          user.passport_attachment,
            'seaman_book':        user.seaman_book_attachment,
            'other_seaman_book':  user.other_seaman_book_attachment,
            'marlins':            user.marlins_test_attachment,
            'ces':                user.ces_test_attachment,
        }

        if doc_type in USER_FILE_MAP:
            file_field = USER_FILE_MAP[doc_type]
            if not file_field:
                return Response({'error': f'No file uploaded for document type "{doc_type}"'}, status=404)
            file_path = file_field.path
        
        elif doc_type == 'coc':
            from licenses.models import UserLicense
            lic = UserLicense.objects.filter(user=user, document_name__icontains='coc').first()
            if not lic or not lic.document_file:
                return Response({'error': 'No COC file uploaded'}, status=404)
            file_path = lic.document_file.path
            
        elif doc_type == 'goc':
            from licenses.models import UserLicense
            lic = UserLicense.objects.filter(user=user, document_name__icontains='goc').first()
            if not lic or not lic.document_file:
                return Response({'error': 'No GOC file uploaded'}, status=404)
            file_path = lic.document_file.path
            
        elif doc_type == 'health_certificate':
            from vaccinations.models import Vaccination
            vac = Vaccination.objects.filter(user=user, name="Medical Certificate For Seafarers").first()
            if not vac or not vac.document:
                return Response({'error': 'No Medical Certificate file uploaded'}, status=404)
            file_path = vac.document.path

        # 2. Handle related model attachments (one-to-many)
        elif doc_type in ['sea_service', 'vaccination', 'course', 'personal_document', 'license']:
            if not doc_id:
                return Response({'error': f'doc_id is required for type "{doc_type}"'}, status=400)
            
            if doc_type == 'sea_service':
                doc = user.sea_services.filter(id=doc_id).first()
                file_field = getattr(doc, 'file', None)
            elif doc_type == 'vaccination':
                from vaccinations.models import Vaccination
                doc = Vaccination.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'document', None)
            elif doc_type == 'course':
                from courses.models import Course
                doc = Course.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'document', None)
            elif doc_type == 'personal_document':
                from api.models import PersonalDocument
                doc = PersonalDocument.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'file', None)
            elif doc_type == 'license':
                from licenses.models import UserLicense
                doc = UserLicense.objects.filter(id=doc_id, user=user).first()
                file_field = getattr(doc, 'document_file', None)
            
            if not doc:
                return Response({'error': f'Document #{doc_id} of type "{doc_type}" not found for this user'}, status=404)
            if not file_field:
                return Response({'error': f'No file attached to this {doc_type} record'}, status=404)
            
            file_path = file_field.path
        
        else:
            choices = list(USER_FILE_MAP.keys()) + ['coc', 'goc', 'health_certificate', 'sea_service', 'vaccination', 'course', 'personal_document', 'license']
            return Response({'error': f'Unknown or missing type. Choices: {choices}'}, status=400)

        # 3. Serve the file
        if not os.path.exists(file_path):
            return Response({'error': 'File record exists but the file was not found on the server'}, status=404)

        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))


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

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Document.objects.all()
        
        # Handle query parameters for filtering
        status = self.request.query_params.getlist('status')
        name = self.request.query_params.get('name')
        email = self.request.query_params.get('email')
        position = self.request.query_params.get('position')
        search = self.request.query_params.get('search')
        
        if status:
            queryset = queryset.filter(status__in=status)
            
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        if email:
            queryset = queryset.filter(email__icontains=email)
            
        if position:
            queryset = queryset.filter(position__icontains=position)
            
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=search) | Q(email__icontains=search))
            
        return queryset

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        if user_id:
            serializer.save(user_id=user_id)
            return

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
                
                # Server-side fallback: extract name from filename if missing
                if not name and 'file' in self.request.FILES:
                    import re
                    filename = self.request.FILES['file'].name
                    clean_name = re.sub(r'\.pdf$|\.docx$', '', filename, flags=re.IGNORECASE)
                    clean_name = re.sub(r'_Application|_CV|\d+', '', clean_name, flags=re.IGNORECASE)
                    clean_name = clean_name.replace('_', ' ').strip()
                    if clean_name:
                        name = clean_name
                        serializer.validated_data['name'] = clean_name
                
                if email:
                    # Check if user exists
                    existing_user = Users.objects.filter(email=email).first()
                    if existing_user:
                        # Update user's name if it was empty or defaulted to "Applicant"
                        if name and (not existing_user.first_name or existing_user.first_name == 'Applicant'):
                            parts = name.split(' ', 1)
                            existing_user.first_name = parts[0]
                            existing_user.middle_name = parts[1] if len(parts) > 1 else ""
                            existing_user.save()
                        
                        # Auto-fill document fields from user if they are missing
                        if not name and existing_user.first_name and existing_user.first_name != 'Applicant':
                            serializer.validated_data['name'] = f"{existing_user.first_name} {existing_user.middle_name}".strip()
                        if not serializer.validated_data.get('phone_number') and existing_user.phone_number:
                            serializer.validated_data['phone_number'] = existing_user.phone_number

                        serializer.save(user=existing_user)
                    else:
                        # Create new user for this applicant
                        print(f"DEBUG: Creating new user for Quick Applier: {email}")
                        parts = name.split(' ', 1) if name else ["Applicant"]
                        first_name = parts[0]
                        middle_name = parts[1] if len(parts) > 1 else ""
                        
                        new_user = Users.objects.create_user(
                            email=email,
                            first_name=first_name,
                            middle_name=middle_name,
                            role='Employee', # Default role for applicants
                            password=None, # Unusable password until they set it
                            # user_status='Active' # Removed invalid choice
                        )
                        serializer.save(user=new_user)
                else:
                    # No email provided
                    if self.request.user and self.request.user.is_authenticated and self.request.user.role == 'Employee' and not self.request.user.is_superuser:
                        # If an employee uploads their own document without an email, attach to them
                        serializer.save(user=self.request.user)
                    elif self.request.user and self.request.user.is_authenticated:
                        # If Admin/HR uploads a CV and AI failed to extract email, create a new applicant profile
                        # with a placeholder email so it doesn't get attached to the Admin's profile.
                        import uuid
                        placeholder_email = f"applicant_{uuid.uuid4().hex[:8]}@placeholder.sakrshipping.com"
                        print(f"DEBUG: Creating new user with placeholder email: {placeholder_email}")
                        
                        parts = name.split(' ', 1) if name else ["Applicant"]
                        first_name = parts[0]
                        middle_name = parts[1] if len(parts) > 1 else ""
                        
                        new_user = Users.objects.create_user(
                            email=placeholder_email,
                            first_name=first_name,
                            middle_name=middle_name,
                            role='Employee',
                            password=None,
                        )
                        serializer.validated_data['email'] = placeholder_email
                        serializer.save(user=new_user)
                    else:
                        from rest_framework.exceptions import ValidationError
                        raise ValidationError({"email": "Email is required for unregistered users to process application."})

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
            
        # Only sync position/title/file for Employee users (not admins)
        if user.role == 'Employee':
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
                # Generate 6-digit random number
                new_id = ''.join(random.choices(string.digits, k=6))
                
                # Check uniqueness loop
                while Users.objects.filter(generated_id=new_id).exists():
                    new_id = ''.join(random.choices(string.digits, k=6))
                
                user.generated_id = new_id
                user.save()
            
            # Sync data to user profile
            self._sync_user_data(document)

            # Auto-create CVSubmission so the approved employee appears in the CV Submissions board
            if document.position:
                from .models import Rank, CVSubmission, RANKS
                # Ensure rank exists â€” try flexible matching
                pos = document.position.strip()
                rank = Rank.objects.filter(name__iexact=pos).first()
                if not rank:
                    # Also try partial/contains match in existing DB ranks
                    rank = Rank.objects.filter(name__icontains=pos).first()
                    if not rank and len(pos) > 3:
                        # Try the reverse: see if the position contains a known rank name
                        for r in Rank.objects.all():
                            if r.name.lower() in pos.lower() or pos.lower() in r.name.lower():
                                rank = r
                                break
                
                if not rank:
                    # Look up code from the RANKS constant list with flexible matching
                    code = None
                    pos_lower = pos.lower().strip()
                    
                    # 1) Exact match
                    for c, n in RANKS:
                        if n.lower().strip() == pos_lower:
                            code = c
                            break
                    
                    # 2) Partial/contains match (e.g. "Oiler" matches "Oiler")
                    if not code:
                        for c, n in RANKS:
                            if pos_lower in n.lower() or n.lower() in pos_lower:
                                code = c
                                break
                    
                    if not code:
                        import uuid
                        code = f"CUS-{str(uuid.uuid4())[:6].upper()}"
                        print(f"WARNING: No matching rank code found for position '{pos}', using fallback: {code}")
                    
                    # Use the canonical RANKS name if we found a match, otherwise use the document position
                    rank_name = pos
                    for c, n in RANKS:
                        if c == code:
                            rank_name = n
                            break
                    rank, _ = Rank.objects.get_or_create(code=code, defaults={"name": rank_name})
                
                # Create or update the submission so it doesn't duplicate
                # Include the company from the document so it links to the right job order company
                submission = CVSubmission.objects.filter(user=user).first()
                if submission:
                    submission.position = rank
                    submission.company = getattr(document, 'company', None)
                    submission.job_position = getattr(document, 'job_position', None)
                    if document.file:
                        submission.cv_file = document.file
                    if submission.status not in ['Approved', 'Hired']:
                        submission.status = 'Approved'
                    submission.save()
                else:
                    submission = CVSubmission.objects.create(
                        user=user,
                        position=rank,
                        company=getattr(document, 'company', None),
                        job_position=getattr(document, 'job_position', None),
                        cv_file=document.file,
                        status='Approved',
                        notes='Auto-created from Approved Document'
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
# POSITION â†’ CODED RANK BRIDGE
# =====================

# Maps human-readable position names (from Document.POSITION_CHOICES)
# to short rank codes used to auto-generate assigned_code (e.g. 'MST.001')
POSITION_CODE_MAP = {
    'Master / Captain': 'DO-1.000',
    'Staff Captain': 'DO-2.000',
    'Chief Officer / Chief Mate': 'DO-3.000',
    'Second Officer': 'DO-4.000',
    'Third Officer': 'DO-5.000',
    'Dynamic Positioning Operator (DPO)': 'DO-7.000',
    'ROV Supervisor': 'DO-8.000',
    'Offshore Installation Manager': 'DO-9.000',
    'Deck Cadet': 'DO-10.000',
    'Bosun': 'DR-1.000',
    'ABLE SEAFARER DECK': 'DR-2.000',
    'Able Seaman (AB)': 'DR-3.000',
    'Ordinary Seaman (OS)': 'DR-4.000',
    'Carpenter': 'DR-5.000',
    'Pumpman': 'DR-6.000',
    'Crane Operator': 'DR-7.000',
    'Water and Pool': 'DR-8.000',
    'Security Guard': 'DR-9.000',
    'Life Guard': 'DR-10.000',
    'Upholsterer': 'DR-11.000',
    'Doctor': 'DR-12.000',
    'Hotel Director': 'DR-13.000',
    'Assistant Hotel Director': 'DR-14.000',
    'Purser': 'DR-15.000',
    'Assistant Purser': 'DR-16.000',
    'Food & Beverage Manager': 'DR-17.000',
    'Executive Chef': 'DR-18.000',
    'Chief Housekeeper': 'DR-19.000',
    'Guest Services Manager': 'DR-20.000',
    'Restaurant Manager': 'DR-21.000',
    'Head Waiter': 'DR-22.000',
    'Waiter': 'DR-23.000',
    'F&B attendant': 'DR-24.000',
    'Bartender': 'DR-25.000',
    'Cabin Steward': 'DR-26.000',
    'Laundryman': 'DR-27.000',
    'Cook': 'DR-28.000',
    '2nd Cook': 'DR-29.000',
    '3rd Cook': 'DR-30.000',
    'Assistant Cook': 'DR-31.000',
    'Baker': 'DR-32.000',
    'Assistant Baker': 'DR-33.000',
    'Pastry': 'DR-34.000',
    'Assistant pastry': 'DR-35.000',
    'Butcher': 'DR-36.000',
    'Steward': 'DR-37.000',
    'Utility Galley': 'DR-38.000',
    'Tour Expert': 'DR-39.000',
    'Photographer': 'DR-40.000',
    'Chief Engineer': 'EO-1.000',
    'Second Engineer': 'EO-2.000',
    'Third Engineer': 'EO-3.000',
    'Fourth Engineer': 'EO-4.000',
    'ETO': 'EO-5.000',
    '2ND ETO': 'EO-6.000',
    '3RD ETO': 'EO-7.000',
    'ELECTRICAL ENGINEER': 'EO-8.000',
    'Refrigeration Engineer': 'EO-9.000',
    'HVAC Engineer': 'EO-10.000',
    'Engine Cadet': 'EO-11.000',
    'Gas Engineer': 'EO-12.000',
    'Cargo Engineer': 'EO-13.000',
    'Reliquefaction Engineer': 'EO-14.000',
    'Motorman': 'ER-1.000',
    'Mechanic': 'ER-2.000',
    'Assistant Mechanic': 'ER-3.000',
    'Oiler': 'ER-4.000',
    'Wiper': 'ER-5.000',
    'Fitter': 'ER-6.000',
    'Welder': 'ER-7.000',
    'Plumber': 'ER-8.000',
    'Assistant Plumber': 'ER-9.000',
    'Electrician': 'ER-11.000',
    '2nd Electrician': 'ER-12.000',
    '3rd Electrician': 'ER-13.000',
    'Assistant Electrician': 'ER-14.000',
    'Trainee Electrician': 'ER-15.000',
    'AC Technician': 'ER-16.000',
    'Senior Accommodation Repairman': 'ER-17.000',
    'junior Accommodation Repairman': 'ER-18.000',
    'Other': 'OTH.000',
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
      2. Maps it to a short rank code (e.g. 'Master' â†’ 'MST').
      3. Gets or creates the Rank object in the DB.
      4. Creates a UserRank â†’ assigned_code is AUTO-GENERATED (e.g. 'MST.001').
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
    position_input = request.data.get('position', '')
    if isinstance(position_input, int):
        position_input = str(position_input)
    
    position_name = position_input.strip()
    
    if not position_name:
        return Response(
            {'error': 'position is required.', 'hint': 'Use GET /api/positions/ to see all valid choices.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1. Try to see if it's an existing Rank ID
    rank = None
    if position_name.isdigit():
        rank = Rank.objects.filter(pk=int(position_name)).first()
        if rank:
            position_name = rank.name

    # 2. If not found by ID, try finding by exact name in Rank table
    if not rank:
        rank = Rank.objects.filter(name__iexact=position_name).first()

    # 3. If still not found, validate against hardcoded choices
    if not rank:
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

    # Map position name â†’ short rank code (only if we didn't find it by ID)
    created = False
    if not rank:
        rank_code = POSITION_CODE_MAP.get(position_name, position_name[:6].upper().replace(' ', '_'))

        # Get or create the Rank object
        rank, created = Rank.objects.get_or_create(
            code=rank_code,
            defaults={'name': position_name}
        )

    # Prevent duplicate assignment
    if UserRank.objects.filter(user=user, rank=rank).exists():
        existing = UserRank.objects.filter(user=user, rank=rank).first()
        return Response(
            {
                'error': f'User already has the rank "{position_name}".',
                'existing_assigned_code': existing.assigned_code
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create UserRank â€” assigned_code is auto-generated in UserRank.save()
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
        """Filter declarations based on user role and query params"""
        user = self.request.user
        queryset = Declaration.objects.select_related('user')
        if user.role in ['Admin', 'HR Manager', 'Recruiter']:
            user_id = self.request.query_params.get('user')
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            return queryset.all()
        # Employee can only see their own declarations
        return queryset.filter(user=user)
    
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
def get_document_types(request):
    """
    Return all available personal/travel document type choices.
    GET /api/document-types/
    """
    choices = [
        {"value": value, "label": label}
        for value, label in PersonalDocument.DOCUMENT_TYPE_CHOICES
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


class GlobalSearchView(APIView):
    """
    Unified search endpoint to query across multiple sections:
    Users, Ships, Companies, CV Submissions, and Contracts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({
                'users': [],
                'ships': [],
                'companies': [],
                'cvs': [],
                'contracts': []
            })

        results = {}

        # 1. Search Users (Seafarers)
        users = Users.objects.filter(
            Q(first_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(nationality__icontains=query)
        ).distinct()[:10]
        # Using a simplified representation for global search results
        results['users'] = [{
            'id': u.id,
            'name': f"{u.first_name} {u.middle_name}".strip(),
            'email': u.email,
            'phone': u.phone_number,
            'role': u.role
        } for u in users]

        # 2. Search Ships
        from ships.models import Ship
        from ships.serializers import ShipSerializer
        ships = Ship.objects.filter(
            Q(ship_name__icontains=query) |
            Q(imo_number__icontains=query)
        ).distinct()[:10]
        results['ships'] = ShipSerializer(ships, many=True).data

        # 3. Search Companies
        from companies.models import Company as MainCompany
        companies = MainCompany.objects.filter(
            Q(company_name__icontains=query) |
            Q(contact_email__icontains=query)
        ).distinct()[:10]
        results['companies'] = CompanyListSerializer(companies, many=True).data

        # 4. Search CV Submissions
        cvs = CVSubmission.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__middle_name__icontains=query) |
            Q(notes__icontains=query)
        ).distinct()[:10]
        results['cvs'] = CVSubmissionListSerializer(cvs, many=True).data

        # 5. Search Contracts
        contracts = Contract.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(status__icontains=query)
        ).distinct()[:10]
        results['contracts'] = ContractListSerializer(contracts, many=True).data

        return Response(results)



# =============================================================
# Expiring Documents - Aggregated endpoint
# =============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expiring_documents(request):
    """
    Aggregate all expiring documents across users in a single response.
    Combines:
      - 9 expiry date fields on the Users model (passport, seaman book, COC, GOC, health, etc.)
      - All rows in PersonalDocument (passport, visas, seaman books, etc.)
    Returns a unified list with daysToExpiry and category per item.

    Query params:
      days (int, default 30): how far ahead to look
      category (str, optional): filter - expired / critical / warning / notice / all
    """
    try:
        # ---- parse query params ----
        try:
            days = int(request.query_params.get('days', 30))
        except (TypeError, ValueError):
            days = 30
        if days < 1:
            days = 30
        if days > 365:
            days = 365

        category_filter = request.query_params.get('category', None)

        # ---- role check ----
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if getattr(request.user, 'role', None) not in ['Admin', 'HR Manager']:
            return Response(
                {'error': 'Only Admin and HR Manager can view expiring documents.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        today = timezone.localdate()
        soon = today + timedelta(days=days)

        def categorize(days_to_expiry):
            if days_to_expiry is None:
                return 'unknown'
            if days_to_expiry < 0:
                return 'expired'
            if days_to_expiry <= 14:
                return 'critical'
            if days_to_expiry <= 30:
                return 'warning'
            if days_to_expiry <= 90:
                return 'notice'
            return 'active'

        all_items = []

        # =============================================================
        # Source 1: Users profile expiry fields (9 fields)
        # =============================================================
        from .models import Users, PersonalDocument

        user_expiry_fields = [
            ('passport_expiry_date',              'Passport',                          'passport_no'),
            ('seaman_book_expiry_date',           "Seaman's Book",                      'seaman_book_no'),
            ('other_seaman_book_expiry_date',     "Other Seaman's Book",                'other_seaman_book_no'),
            ('coc_expiry_date',                   'Certificate of Competency (COC)',   'coc_certificate_number'),
            ('goc_expiry_date',                   'General Operator Certificate (GOC)', 'goc_certificate_number'),
            ('health_expiry_date',                'Health Certificate',                'health_number'),
            ('international_medical_expiry_date', 'International Medical',              'international_medical_number'),
            ('yellow_fever_expiry_date',          'Yellow Fever Vaccination',          'yellow_fever_number'),
            ('cholera_expiry_date',               'Cholera Vaccination',               None),
        ]

        # Build Q for users with at least one field in range or expired
        user_q = Q()
        for field, _, _ in user_expiry_fields:
            user_q |= Q(**{f'{field}__lt': today})
            user_q |= Q(**{f'{field}__gte': today, f'{field}__lte': soon})

        users_with_expiring = Users.objects.filter(user_q).distinct()

        for user in users_with_expiring:
            user_name = (
                f"{getattr(user, 'first_name', '')} {getattr(user, 'middle_name', '')}"
                .strip() or getattr(user, 'email', '')
            )
            for field, doc_type, number_field in user_expiry_fields:
                expiry = getattr(user, field, None)
                if not expiry:
                    continue
                if not (expiry < today or today <= expiry <= soon):
                    continue

                days_to_expiry = (expiry - today).days
                cat = categorize(days_to_expiry)
                if category_filter and category_filter != 'all' and cat != category_filter:
                    continue

                doc_number = getattr(user, number_field, None) if number_field else None
                all_items.append({
                    'id': f"user_{user.id}_{field}",
                    'type': doc_type,
                    'name': f"{doc_type} - {doc_number or 'N/A'}",
                    'number': doc_number or 'N/A',
                    'user': user_name,
                    'userId': user.id,
                    'userEmail': user.email,
                    'expiryDate': expiry.isoformat(),
                    'daysToExpiry': days_to_expiry,
                    'category': cat,
                    'source': 'user_profile',
                })

        # =============================================================
        # Source 2: PersonalDocument table
        # =============================================================
        personal_docs = PersonalDocument.objects.select_related('user').filter(
            expiry_date__lte=soon
        )

        for doc in personal_docs:
            if not doc.expiry_date:
                continue
            days_to_expiry = (doc.expiry_date - today).days
            cat = categorize(days_to_expiry)
            if category_filter and category_filter != 'all' and cat != category_filter:
                continue

            user_name = (
                f"{getattr(doc.user, 'first_name', '')} {getattr(doc.user, 'middle_name', '')}"
                .strip() or getattr(doc.user, 'email', 'Unknown')
            ) if doc.user else 'Unknown'
            all_items.append({
                'id': f"pd_{doc.id}",
                'type': doc.document_type or 'Personal Document',
                'name': f"{doc.document_type or 'Document'} - {doc.document_number or 'N/A'}",
                'number': doc.document_number or 'N/A',
                'user': user_name,
                'userId': doc.user_id,
                'userEmail': doc.user.email if doc.user else None,
                'expiryDate': doc.expiry_date.isoformat(),
                'daysToExpiry': days_to_expiry,
                'category': cat,
                'source': 'personal_document',
            })

        # ---- sort by urgency (most overdue first, then earliest expiry) ----
        all_items.sort(key=lambda x: x['daysToExpiry'])

        counts = {
            'expired': sum(1 for x in all_items if x['category'] == 'expired'),
            'critical': sum(1 for x in all_items if x['category'] == 'critical'),
            'warning': sum(1 for x in all_items if x['category'] == 'warning'),
            'notice': sum(1 for x in all_items if x['category'] == 'notice'),
            'active': sum(1 for x in all_items if x['category'] == 'active'),
            'total': len(all_items),
        }

        return Response({
            'counts': counts,
            'days_window': days,
            'today': today.isoformat(),
            'category_filter': category_filter or 'all',
            'results': all_items,
        })
    except Exception as e:
        import traceback
        return Response(
            {'error': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
