from rest_framework import serializers, validators
from django.contrib.auth.models import Permission, Group
from .models import (
    Users, UserRank, Certificate, Rank, Contract, Reference, SeaService,
    Interview, CVSubmission, Document, UserLanguage, PersonalDocument
)
from companies.models import Company
from finance.models import FinanceRecord
from tickets_papers.models import Ticket, TravelingPaper
from ships.serializers import ShipSerializer
from .models import LanguageProficiency
from api.serializers import FlexibleDateField, FlexibleFileField


# ========================
# GOOGLE AUTH SERIALIZER
# ========================

class GoogleAuthSerializer(serializers.Serializer):
    """
    Accepts the Google ID token from the frontend (obtained after user
    clicks 'Sign in with Google'). The backend verifies it and issues
    our own JWT tokens.
    """
    id_token = serializers.CharField(required=True, help_text="Google ID token returned by the frontend Google Sign-In flow.")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "ticket_number"]


class TravelingPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelingPaper
        fields = ["id", "title"]


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ["id", "code", "name"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["id", "code", "name"]


class UserRankSerializer(serializers.ModelSerializer):
    """Serializer for UserRank - includes the assigned_code"""
    rank = RankSerializer(read_only=True)
    rank_code = serializers.CharField(source='rank.code', read_only=True)
    rank_name = serializers.CharField(source='rank.name', read_only=True)

    class Meta:
        model = UserRank
        fields = ["id", "assigned_code", "rank_code", "rank_name", "rank"]


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'


class SeaServiceSerializer(serializers.ModelSerializer):
    signed_on = FlexibleDateField(required=False, allow_null=True)
    signed_off = FlexibleDateField(required=False, allow_null=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = SeaService
        fields = '__all__'
        read_only_fields = ['user', 'download_url']

    def get_download_url(self, obj):
        if getattr(obj, 'file', None) and getattr(obj, 'user', None):
            path = f"/api/users/{obj.user.id}/download-sea-service/{obj.id}/"
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.file and instance.user:
            ret['file'] = self.get_download_url(instance)
        return ret

    def validate(self, data):
        signed_on = data.get('signed_on', self.instance.signed_on if self.instance else None)
        signed_off = data.get('signed_off', self.instance.signed_off if self.instance else None)
        
        from datetime import date
        today = date.today()
        if signed_on and signed_on > today:
            raise serializers.ValidationError({"signed_on": ["Sign-on date cannot be in the future."]})

        # Determine the user instance, because data.get('user') might be empty if derived from request.
        user = data.get('user')
        if not user and self.instance:
            user = self.instance.user
        if not user and 'request' in self.context and hasattr(self.context['request'], 'user'):
            user = self.context['request'].user
            
        if signed_on and signed_off and signed_off < signed_on:
            raise serializers.ValidationError({"signed_off": ["Signed off date cannot be before signed on date."]})
            
        if signed_on and user:
            # Check for overlaps
            overlapping = SeaService.objects.filter(user=user)
            if self.instance and self.instance.id:
                overlapping = overlapping.exclude(id=self.instance.id)
                
            for existing in overlapping:
                if not existing.signed_on:
                    continue
                    
                e_on = existing.signed_on
                e_off = existing.signed_off
                
                overlap = False
                if signed_off is None and e_off is None:
                    overlap = True
                elif signed_off is None:
                    if e_off >= signed_on:
                        overlap = True
                elif e_off is None:
                    if signed_off >= e_on:
                        overlap = True
                else:
                    if signed_on <= e_off and signed_off >= e_on:
                        overlap = True
                        
                if overlap:
                    e_on_str = e_on.strftime("%d-%m-%Y")
                    e_off_str = e_off.strftime("%d-%m-%Y") if e_off else "Present"
                    raise serializers.ValidationError({
                        "signed_on": [f"Dates overlap with existing service ({e_on_str} to {e_off_str})."]
                    })
                    
        return data

    def _calculate_period(self, signed_on, signed_off):
        """Calculate the time period between signed_on and signed_off."""
        if not signed_on or not signed_off:
            return ''
        # Calculate years, months, days manually
        years = signed_off.year - signed_on.year
        months = signed_off.month - signed_on.month
        days = signed_off.day - signed_on.day
        if days < 0:
            months -= 1
            # Get days in previous month
            import calendar
            prev_month = signed_off.month - 1 or 12
            prev_year = signed_off.year if signed_off.month > 1 else signed_off.year - 1
            days += calendar.monthrange(prev_year, prev_month)[1]
        if months < 0:
            years -= 1
            months += 12
        parts = []
        if years:
            parts.append(f"{years}y")
        if months:
            parts.append(f"{months}m")
        if days:
            parts.append(f"{days}d")
        return ' '.join(parts) if parts else '0d'

    def create(self, validated_data):
        signed_on = validated_data.get('signed_on')
        signed_off = validated_data.get('signed_off')
        if signed_on and signed_off and not validated_data.get('period'):
            validated_data['period'] = self._calculate_period(signed_on, signed_off)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        signed_on = validated_data.get('signed_on', instance.signed_on)
        signed_off = validated_data.get('signed_off', instance.signed_off)
        if signed_on and signed_off:
            validated_data['period'] = self._calculate_period(signed_on, signed_off)
        return super().update(instance, validated_data)


class UserMeSerializer(serializers.ModelSerializer):
    cv_status = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "profile_image",
            "role",
            "cv_status",
        ]

    def get_cv_status(self, obj):
        """
        Logic:
        - active, not registered yet (no docs) = false
        - pending, black list = false
        """
        from api.models import Document
        docs = Document.objects.filter(user=obj)
        
        if not docs.exists():
            return False
            
        # Check for blacklist or pending across all user documents
        if docs.filter(status__in=['Blacklist', 'Pending']).exists():
            return False
            
        return True

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['first_name'] = f"{instance.first_name} {instance.middle_name}".strip()
        return representation


# =====================
# COMPANY SERIALIZERS
# =====================

class CompanyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    company_type = serializers.StringRelatedField()

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'company_type', 'contact_email', 'open_positions', 'status']


class CompanySerializer(serializers.ModelSerializer):
    """Full serializer for detail views"""
    class Meta:
        model = Company
        fields = '__all__'


# =====================
# INTERVIEW SERIALIZERS
# =====================

class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.first_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'candidate', 'candidate_name', 'candidate_email',
            'company', 'company_name', 'position', 'position_name',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'interview_type', 'location', 'meeting_link',
            'interviewer_name', 'interviewer_email',
            'status', 'result', 'notes', 'feedback',
            'created_by', 'created_at', 'updated_at'
        ]

    def to_internal_value(self, data):
        if 'position' in data:
            pos_val = data['position']
            if isinstance(pos_val, str) and not pos_val.isdigit():
                from api.models import Rank, RANKS
                rank = Rank.objects.filter(name__iexact=pos_val).first()
                if not rank:
                    code = None
                    for c, n in RANKS:
                        if n.lower() == pos_val.lower():
                            code = c
                            break
                    if not code:
                        import uuid
                        code = f"CUS-{str(uuid.uuid4())[:6].upper()}"
                    rank, _ = Rank.objects.get_or_create(code=code, defaults={'name': pos_val})
                    
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['position'] = rank.id
        return super().to_internal_value(data)


class InterviewCalendarSerializer(serializers.ModelSerializer):
    """Lightweight serializer for calendar view"""
    candidate_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'candidate_name', 'company_name',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'interview_type', 'status'
        ]

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.middle_name}".strip()


# =====================
# FINANCE RECORD SERIALIZERS
# =====================

class FinanceRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.first_name', read_only=True)

    class Meta:
        model = FinanceRecord
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'company', 'company_name', 'contract',
            'record_type', 'description', 'amount', 'currency',
            'start_date', 'end_date', 'payment_date',
            'status', 'approved_by', 'approved_by_name', 'approved_date',
            'notes', 'attachment', 'created_at', 'updated_at'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()


# =====================
# CV SUBMISSION SERIALIZERS
# =====================

class CVSubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — extended with all 17 UI columns"""
    user_name = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position.name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    # Reviewed-by display fields (read-only)
    reviewed_by_name = serializers.CharField(source='reviewed_by.first_name', read_only=True, default=None)
    reviewed_by_last_name = serializers.CharField(source='reviewed_by.last_name', read_only=True, default=None)

    # CV-level fields (not user-level) — so the list shows what THIS application set
    # rather than the user's profile defaults
    salary = serializers.DecimalField(source='expected_salary', max_digits=10, decimal_places=2, read_only=True, default=None)
    available_date = serializers.DateField(source='availability_date', read_only=True, default=None)

    # Profile-derived fields (kept from user for display only)
    generated_id = serializers.SerializerMethodField()
    profile_image = serializers.ImageField(source='user.profile_image', read_only=True)
    coded_rank = serializers.SerializerMethodField()

    # Directly expose the rank_code and assigned_code for the specific position
    rank_code = serializers.CharField(source='position.code', read_only=True)
    assigned_code = serializers.SerializerMethodField()
    job_position_details = serializers.SerializerMethodField()

    class Meta:
        model = CVSubmission
        fields = [
            'id', 'user', 'user_name',
            'company', 'company_name',      # company FK id AND display name
            'position', 'position_name',    # position FK id AND display name
            'experience_years', 'status', 'submitted_date',
            'generated_id', 'salary', 'available_date', 'profile_image', 'coded_rank',
            'rank_code', 'assigned_code',
            'job_position', 'job_position_details',
            # Fields previously missing in the list response (now exposed)
            'cover_letter',
            'reviewed_by', 'reviewed_by_name', 'reviewed_by_last_name', 'reviewed_date',
            'notes', 'rating',
            'created_at', 'updated_at',
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()

    def get_job_position_details(self, obj):
        if not obj.job_position:
            return None
        pos = obj.job_position
        return {
            'id': pos.id,
            'job_position_name': pos.rank.name if pos.rank else None,
            'quantity': pos.quantity,
            'salary_min': str(pos.salary_min) if pos.salary_min else None,
            'salary_max': str(pos.salary_max) if pos.salary_max else None,
            'currency': pos.currency,
            'contract_duration_months': pos.contract_duration_months,
            'remarks': pos.remarks
        }

    def get_assigned_code(self, obj):
        if obj.position:
            user_rank = obj.user.user_ranks.filter(rank=obj.position).first()
            if user_rank:
                return user_rank.assigned_code
        return None

    def get_generated_id(self, obj):
        """
        Returns the user's generated_id (12-digit ID).
        This is only set after a Document is approved via
        POST /api/documents/{id}/set_status/ with status='Active'.
        Returns null if the user has not been approved yet.
        """
        return obj.user.generated_id

    def get_coded_rank(self, obj):
        """
        Returns all assigned rank codes for the user.
        Each entry contains: assigned_code, rank_code, rank_name.
        """
        user_ranks = obj.user.user_ranks.select_related('rank').order_by('-id')[:1]
        return [
            {
                'assigned_code': ur.assigned_code,
                'rank_code': ur.rank.code,
                'rank_name': ur.rank.name,
            }
            for ur in user_ranks
        ]

    def to_representation(self, instance):
        # Fall back to the linked user's profile values when the CV
        # submission's own columns (expected_salary / availability_date)
        # are NULL. The source= mappings have already populated
        # ret['salary'] from expected_salary and ret['available_date']
        # from availability_date, so we only fill in the user-level
        # value when those came out as None.
        ret = super().to_representation(instance)
        if ret.get('salary') is None and instance.user:
            ret['salary'] = instance.user.salary
        if ret.get('available_date') is None and instance.user:
            ret['available_date'] = instance.user.available_date
        return ret


class CVSubmissionSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(write_only=True, required=False)
    user_middle_name = serializers.CharField(write_only=True, required=False)
    # Declared as plain write_only fields (no source='user.*') to avoid DRF putting
    # them inside validated_data['user'] as a Users instance, which breaks .pop()
    user_email = serializers.EmailField(write_only=True, required=False)
    company_name_input = serializers.CharField(write_only=True, required=False)
    position_name_input = serializers.CharField(write_only=True, required=False)
    ship_name_input = serializers.CharField(write_only=True, required=False)
    reviewed_by_name = serializers.CharField(write_only=True, required=False)
    salary = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    # Read-only display fields (computed)
    user_name = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position.name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    ship_name = serializers.CharField(source='ship.ship_name', read_only=True)
    reviewed_by_name_display = serializers.CharField(source='reviewed_by.first_name', read_only=True)
    # Read-only from the linked user (for output only; input handled by write_only fields above)
    user_email_display = serializers.EmailField(source='user.email', read_only=True)
    salary_display = serializers.CharField(source='user.salary', read_only=True)
    profile_image = serializers.ImageField(source='user.profile_image', read_only=True)
    generated_id = serializers.SerializerMethodField()
    coded_rank = serializers.SerializerMethodField()
    coded_rank_input = serializers.ListField(write_only=True, required=False)
    
    rank_code = serializers.CharField(source='position.code', read_only=True)
    assigned_code = serializers.SerializerMethodField()

    # Update assigned_code on specific existing UserRank records without replacing them all.
    # Each item: { "user_rank_id": <int>, "assigned_code": "<string>" }
    assigned_code_updates = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of {user_rank_id, assigned_code} to update individual rank codes."
    )

    # Certificates — read display + write input
    certificates = serializers.SerializerMethodField()
    certificate_ids = serializers.PrimaryKeyRelatedField(
        queryset=Certificate.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="List of Certificate IDs to assign/replace on the linked user."
    )

    # All user travel documents / official docs — read display, with separate write fields per section
    user_documents = serializers.SerializerMethodField()

    # Write fields for each document section (all write_only, all optional)
    # Passport
    passport_update = serializers.DictField(write_only=True, required=False,
        help_text="{passport_no, issue_date, expiry_date, issued_by, place_of_issue}")
    # Seaman Book
    seaman_book_update = serializers.DictField(write_only=True, required=False,
        help_text="{seaman_book_no, issue_date, expiry_date, issued_by, place_of_issue}")
    # Other / Second Seaman Book
    other_seaman_book_update = serializers.DictField(write_only=True, required=False,
        help_text="{seaman_book_no, issue_date, expiry_date, issued_by, place_of_issue}")
    # COC
    coc_update = serializers.DictField(write_only=True, required=False,
        help_text="{certificate_name, certificate_number, issue_date, expiry_date, issued_by, issued_at}")
    # GOC
    goc_update = serializers.DictField(write_only=True, required=False,
        help_text="{certificate_number, issue_date, expiry_date, issued_by, issued_at}")
    # Licenses — list; each item may include id (update), or omit id (create), or _delete=true (delete)
    licenses_update = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False,
        help_text="List of license objects. Include id to update, omit id to create, set _delete=true to remove."
    )

    # Flexible date fields — accept YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, etc.
    availability_date = FlexibleDateField(required=False, allow_null=True)
    submitted_date = FlexibleDateField(required=False, allow_null=True)
    reviewed_date = FlexibleDateField(required=False, allow_null=True)
    available_date = FlexibleDateField(write_only=True, required=False, allow_null=True)
    
    job_position_details = serializers.SerializerMethodField()
    seafarer_application = serializers.SerializerMethodField()
    company_details = serializers.SerializerMethodField()
    ship_details = serializers.SerializerMethodField()

    class Meta:
        model = CVSubmission
        fields = [
            'id', 'user', 'user_name', 'user_first_name', 'user_middle_name',
            'user_email', 'user_email_display', 'profile_image', 'company', 'company_name', 'company_name_input',
            'ship', 'ship_name', 'ship_details', 'ship_name_input',
            'position', 'position_name', 'position_name_input',
            'cv_file', 'cover_letter', 'experience_years',
            'expected_salary', 'availability_date',
            'status', 'submitted_date',
            'reviewed_by', 'reviewed_by_name', 'reviewed_by_name_display', 'reviewed_date',
            'notes', 'rating', 'created_at', 'updated_at',
            'generated_id', 'salary', 'salary_display', 'available_date', 'coded_rank', 'coded_rank_input',
            'rank_code', 'assigned_code',
            'assigned_code_updates',
            'certificates', 'certificate_ids',
            'user_documents',
            'passport_update', 'seaman_book_update', 'other_seaman_book_update',
            'coc_update', 'goc_update', 'licenses_update',
            'job_position', 'job_position_details',
            'seafarer_application',
            'company_details',
        ]
        extra_kwargs = {
            'user': {'required': False},
            'submitted_date': {'required': False},
            'created_at': {'required': False},
            'updated_at': {'required': False},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Fall back from the CV's own columns to the linked user's
        # profile values when the CV didn't fill them. The source=
        # mapping has already populated ret['salary'] from
        # instance.expected_salary and ret['available_date'] from
        # instance.availability_date, so we only override when those
        # are None.
        if ret.get('salary') is None and instance.user:
            ret['salary'] = instance.user.salary
        if ret.get('available_date') is None and instance.user:
            ret['available_date'] = instance.user.available_date
        if instance.cv_file:
            path = f"/api/cv-submissions/{instance.id}/download-cv/"
            request = self.context.get('request')
            if request:
                ret['cv_file'] = request.build_absolute_uri(path)
            else:
                ret['cv_file'] = path
        return ret

    def to_internal_value(self, data):
        # Allow 'position' to be passed as a string (name) or an ID
        if 'position' in data:
            pos_val = data['position']
            if isinstance(pos_val, str) and not pos_val.isdigit():
                from api.models import Rank, RANKS
                rank = Rank.objects.filter(name__iexact=pos_val).first()
                if not rank:
                    # Try partial/contains match in DB
                    rank = Rank.objects.filter(name__icontains=pos_val).first()
                if not rank:
                    code = None
                    pos_lower = pos_val.lower().strip()
                    # 1) Exact match against RANKS list
                    for c, n in RANKS:
                        if n.lower().strip() == pos_lower:
                            code = c
                            break
                    # 2) Partial/contains match
                    if not code:
                        for c, n in RANKS:
                            if pos_lower in n.lower() or n.lower() in pos_lower:
                                code = c
                                break
                    if not code:
                        import uuid
                        code = f"CUS-{str(uuid.uuid4())[:6].upper()}"
                    # Use canonical RANKS name if found
                    rank_name = pos_val
                    for c, n in RANKS:
                        if c == code:
                            rank_name = n
                            break
                    rank, _ = Rank.objects.get_or_create(code=code, defaults={'name': rank_name})

                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['position'] = rank.id

        # Auto-fill company and position if job_position is provided
        if 'job_position' in data and data['job_position']:
            from companies.models import JobOrderPosition
            try:
                job_pos = JobOrderPosition.objects.get(id=data['job_position'])
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                
                if 'company' not in data and job_pos.job_order and job_pos.job_order.company:
                    data['company'] = job_pos.job_order.company.id
                if 'position' not in data and job_pos.rank:
                    data['position'] = job_pos.rank.id
            except JobOrderPosition.DoesNotExist:
                pass

        return super().to_internal_value(data)

    def create(self, validated_data):
        custom_fields = [
            'user_first_name', 'user_middle_name', 'user_email', 'company_name_input',
            'position_name_input', 'ship_name_input', 'reviewed_by_name', 'salary', 'available_date', 'coded_rank_input',
            'assigned_code_updates', 'certificate_ids', 'passport_update',
            'seaman_book_update', 'other_seaman_book_update', 'coc_update',
            'goc_update', 'licenses_update'
        ]
        custom_data = {}
        for field in custom_fields:
            if field in validated_data:
                custom_data[field] = validated_data.pop(field)

        instance = super().create(validated_data)
        
        # Auto-assign the position as a UserRank to generate assigned_code immediately
        if instance.position:
            from api.models import UserRank
            UserRank.objects.get_or_create(user=instance.user, rank=instance.position)

        if custom_data:
            self.update(instance, custom_data)
            
        return instance

    def update(self, instance, validated_data):
        # Pop writable-only fields that don't map directly to model fields.
        # NOTE: these are declared as plain write_only fields (no source='user.*')
        # so DRF puts them as flat top-level keys in validated_data — safe to pop directly.
        user_first_name = validated_data.pop('user_first_name', None)
        user_middle_name = validated_data.pop('user_middle_name', None)
        user_email = validated_data.pop('user_email', None)
        company_name_input = validated_data.pop('company_name_input', None)
        position_name_input = validated_data.pop('position_name_input', None)
        ship_name_input = validated_data.pop('ship_name_input', None)
        reviewed_by_name = validated_data.pop('reviewed_by_name', None)
        salary = validated_data.pop('salary', None)
        available_date = validated_data.pop('available_date', None)
        coded_rank_input = validated_data.pop('coded_rank_input', None)
        assigned_code_updates = validated_data.pop('assigned_code_updates', None)
        certificate_ids = validated_data.pop('certificate_ids', None)
        passport_update = validated_data.pop('passport_update', None)
        seaman_book_update = validated_data.pop('seaman_book_update', None)
        other_seaman_book_update = validated_data.pop('other_seaman_book_update', None)
        coc_update = validated_data.pop('coc_update', None)
        goc_update = validated_data.pop('goc_update', None)
        licenses_update = validated_data.pop('licenses_update', None)

        # Propagate changes to the User model
        user = instance.user
        if user_first_name is not None:
            user.first_name = user_first_name
        if user_middle_name is not None:
            user.middle_name = user_middle_name
        if user_email is not None:
            user.email = user_email
        if salary is not None:
            user.salary = salary
        if available_date is not None:
            user.available_date = available_date
        if any(v is not None for v in [user_first_name, user_middle_name, user_email, salary, available_date]):
            user.save()

        # Propagate company name to the Company model
        if company_name_input is not None and instance.company:
            instance.company.company_name = company_name_input
            instance.company.save()

        # Propagate position name to the Rank model
        if position_name_input is not None and instance.position:
            instance.position.name = position_name_input
            instance.position.save()

        # Handle ship_name_input
        if ship_name_input is not None:
            from ships.models import Ship
            from rest_framework.exceptions import ValidationError
            try:
                ship_obj = Ship.objects.get(ship_name__iexact=ship_name_input)
                instance.ship = ship_obj
                instance.save(update_fields=['ship'])
            except Ship.DoesNotExist:
                raise ValidationError({'ship_name_input': f"Ship with name '{ship_name_input}' not found."})

        # Propagate reviewed_by_name to the reviewed_by User
        if reviewed_by_name is not None and instance.reviewed_by:
            instance.reviewed_by.first_name = reviewed_by_name
            instance.reviewed_by.save()

        # Handle coded_rank input — sync UserRank entries
        if coded_rank_input is not None:
            # Delete existing ranks
            from api.models import UserRank
            instance.user.user_ranks.all().delete()
            for entry in coded_rank_input:
                from api.models import Rank
                rank_code = entry.get('rank_code') or entry.get('assigned_code', '').split('.')[0]
                rank_name = entry.get('rank_name', '')
                assigned_code = entry.get('assigned_code', '')
                # Try to find existing rank, else create
                rank, _ = Rank.objects.get_or_create(
                    code=rank_code,
                    defaults={'name': rank_name}
                )
                UserRank.objects.create(
                    user=instance.user,
                    rank=rank,
                    assigned_code=assigned_code
                )

        # Handle certificate_ids — replace all user certificates
        if certificate_ids is not None:
            instance.user.certificates.set(certificate_ids)

        # Handle assigned_code_updates — patch assigned_code on specific UserRank records
        if assigned_code_updates is not None:
            from api.models import UserRank
            for entry in assigned_code_updates:
                ur_id = entry.get('user_rank_id')
                new_code = entry.get('assigned_code')
                if ur_id is not None and new_code is not None:
                    UserRank.objects.filter(
                        id=ur_id,
                        user=instance.user
                    ).update(assigned_code=new_code)

        # Helper: parse date strings flexibly
        def _parse_date(value):
            if not value:
                return None
            from datetime import date
            import datetime
            if isinstance(value, (date, datetime.datetime)):
                return value if isinstance(value, date) else value.date()
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
                try:
                    return datetime.datetime.strptime(str(value), fmt).date()
                except ValueError:
                    continue
            return None

        # Handle passport_update — update passport fields on user
        if passport_update is not None:
            user = instance.user
            if 'passport_no' in passport_update:
                user.passport_no = passport_update['passport_no']
            if 'issue_date' in passport_update:
                user.passport_issue_date = _parse_date(passport_update['issue_date'])
            if 'expiry_date' in passport_update:
                user.passport_expiry_date = _parse_date(passport_update['expiry_date'])
            if 'issued_by' in passport_update:
                user.passport_issued_by = passport_update['issued_by']
            if 'place_of_issue' in passport_update:
                user.passport_place_of_issue = passport_update['place_of_issue']
            user.save()

        # Handle seaman_book_update
        if seaman_book_update is not None:
            user = instance.user
            if 'seaman_book_no' in seaman_book_update:
                user.seaman_book_no = seaman_book_update['seaman_book_no']
            if 'issue_date' in seaman_book_update:
                user.seaman_book_issue_date = _parse_date(seaman_book_update['issue_date'])
            if 'expiry_date' in seaman_book_update:
                user.seaman_book_expiry_date = _parse_date(seaman_book_update['expiry_date'])
            if 'issued_by' in seaman_book_update:
                user.seaman_book_issued_by = seaman_book_update['issued_by']
            if 'place_of_issue' in seaman_book_update:
                user.seaman_book_place_of_issue = seaman_book_update['place_of_issue']
            user.save()

        # Handle other_seaman_book_update
        if other_seaman_book_update is not None:
            user = instance.user
            if 'seaman_book_no' in other_seaman_book_update:
                user.other_seaman_book_no = other_seaman_book_update['seaman_book_no']
            if 'issue_date' in other_seaman_book_update:
                user.other_seaman_book_issue_date = _parse_date(other_seaman_book_update['issue_date'])
            if 'expiry_date' in other_seaman_book_update:
                user.other_seaman_book_expiry_date = _parse_date(other_seaman_book_update['expiry_date'])
            if 'issued_by' in other_seaman_book_update:
                user.other_seaman_book_issued_by = other_seaman_book_update['issued_by']
            if 'place_of_issue' in other_seaman_book_update:
                user.other_seaman_book_place_of_issue = other_seaman_book_update['place_of_issue']
            user.save()

        # Handle coc_update
        if coc_update is not None:
            user = instance.user
            if 'certificate_name' in coc_update:
                user.coc_certificate_name = coc_update['certificate_name']
            if 'certificate_number' in coc_update:
                user.coc_certificate_number = coc_update['certificate_number']
            if 'issue_date' in coc_update:
                user.coc_issue_date = _parse_date(coc_update['issue_date'])
            if 'expiry_date' in coc_update:
                user.coc_expiry_date = _parse_date(coc_update['expiry_date'])
            if 'issued_by' in coc_update:
                user.coc_issued_by = coc_update['issued_by']
            if 'issued_at' in coc_update:
                user.coc_issued_at = coc_update['issued_at']
            user.save()

        # Handle goc_update
        if goc_update is not None:
            user = instance.user
            if 'certificate_number' in goc_update:
                user.goc_certificate_number = goc_update['certificate_number']
            if 'issue_date' in goc_update:
                user.goc_issue_date = _parse_date(goc_update['issue_date'])
            if 'expiry_date' in goc_update:
                user.goc_expiry_date = _parse_date(goc_update['expiry_date'])
            if 'issued_by' in goc_update:
                user.goc_issued_by = goc_update['issued_by']
            if 'issued_at' in goc_update:
                user.goc_issued_at = goc_update['issued_at']
            user.save()

        # Handle licenses_update — create / update / delete UserLicense records
        if licenses_update is not None:
            from licenses.models import UserLicense
            for entry in licenses_update:
                lic_id = entry.get('id')
                delete_flag = entry.get('_delete', False)
                if lic_id and delete_flag:
                    UserLicense.objects.filter(id=lic_id, user=instance.user).delete()
                    continue
                fields_map = {
                    'document_name': entry.get('document_name'),
                    'document_number': entry.get('document_number', ''),
                    'country_of_issue': entry.get('country_of_issue', ''),
                    'issue_date': _parse_date(entry.get('issue_date')),
                    'expiration_date': _parse_date(entry.get('expiration_date')),
                }
                # Remove None values so we don't overwrite with None unintentionally
                fields_map = {k: v for k, v in fields_map.items() if v is not None}
                if lic_id:
                    UserLicense.objects.filter(id=lic_id, user=instance.user).update(**fields_map)
                else:
                    UserLicense.objects.create(user=instance.user, **fields_map)

        instance = super().update(instance, validated_data)

        if instance.position:
            from api.models import UserRank
            UserRank.objects.get_or_create(user=instance.user, rank=instance.position)

        return instance

    def validate_position(self, value):
        """Allow empty string to be treated as None"""
        if value == '':
            return None
        return value

    def validate_job_position(self, value):
        if value is not None:
            if value.quantity <= 0:
                raise serializers.ValidationError("This Job Order Position has 0 openings. You cannot assign any applicants to it.")
            
            # Count existing active/pending contracts for this job position
            from api.models import Contract
            qs = Contract.objects.filter(
                job_position=value,
                status__in=['Pending', 'Signed', 'Pending Signature', 'Active']
            )
            assigned_count = qs.count()
            if assigned_count >= value.quantity:
                raise serializers.ValidationError(
                    f"This Job Order Position is already fully assigned ({assigned_count}/{value.quantity} filled). You cannot assign any more applicants."
                )
        return value

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()

    def get_generated_id(self, obj):
        """
        Returns the user's generated_id (12-digit ID).
        This is only set after a Document is approved via
        POST /api/documents/{id}/set_status/ with status='Active'.
        Returns null if the user has not been approved yet.
        """
        return obj.user.generated_id

    def get_assigned_code(self, obj):
        if obj.position:
            user_rank = obj.user.user_ranks.filter(rank=obj.position).first()
            if user_rank:
                return user_rank.assigned_code
        return None

    def get_user_documents(self, obj):
        """
        Returns all official/travel documents linked to the user, grouped by type.
        File attachments include a `download_url` pointing to:
          GET /api/cv-submissions/{cv_id}/download-document/?type=<doc_type>
        """
        user = obj.user
        request = self.context.get('request')
        cv_id = obj.id

        def build_download_url(doc_type, doc_id=None):
            url = f"/api/cv-submissions/{cv_id}/download-document/?type={doc_type}"
            if doc_id:
                url += f"&doc_id={doc_id}"
            return url

        def file_url(field, download_path=None):
            if not field:
                return None
            if download_path:
                if request:
                    return request.build_absolute_uri(download_path)
                return download_path
            if request:
                return request.build_absolute_uri(field.url)
            return field.url

        # Licenses (from licenses app)
        from licenses.models import UserLicense
        licenses_qs = UserLicense.objects.filter(user=user)
        licenses_data = [
            {
                'id': lic.id,
                'document_name': lic.document_name,
                'document_number': lic.document_number,
                'country_of_issue': lic.country_of_issue,
                'issue_date': str(lic.issue_date) if lic.issue_date else None,
                'expiration_date': str(lic.expiration_date) if lic.expiration_date else None,
                'file_url': file_url(lic.document_file, download_path=build_download_url('license', lic.id)) if lic.document_file else None,
                'download_url': build_download_url('license', lic.id) if lic.document_file else None,
            }
            for lic in licenses_qs
        ]

        # Sea Services
        sea_services_qs = user.sea_services.all()
        from api.models import Rank
        from core.models import VesselType, Flag
        ranks_dict = {str(r.id): r.name for r in Rank.objects.all()}
        vessels_dict = {str(v.id): v.name for v in VesselType.objects.all()}
        flags_dict = {str(f.id): f.name for f in Flag.objects.all()}

        sea_services_data = [
            {
                'id': ss.id,
                'vessel_name': ss.vessel_name,
                'rank': ranks_dict.get(str(ss.rank), ss.rank) if ss.rank else '',
                'vessel_type': vessels_dict.get(str(ss.vessel_type), ss.vessel_type) if getattr(ss, 'vessel_type', None) else '',
                'flag': flags_dict.get(str(ss.flag), ss.flag) if getattr(ss, 'flag', None) else '',
                'signed_on': str(ss.signed_on) if ss.signed_on else None,
                'signed_off': str(ss.signed_off) if ss.signed_off else None,
                'file_url': file_url(ss.file, download_path=build_download_url('sea_service', ss.id)) if ss.file else None,
                'download_url': build_download_url('sea_service', ss.id) if ss.file else None,
            }
            for ss in sea_services_qs
        ]

        # Marine Courses — same field shape as seafarer_application
        # `8_marine_courses` (api/seafarer_application_serializers.py)
        # so the frontend doesn't have to merge two different
        # representations of the same Course rows. We expose BOTH
        # `course_number` (the model field name) and `number` (the
        # legacy key the seafarer-application path uses, and the
        # frontend CVSubmissionViewModal reads).
        from courses.models import Course
        courses_qs = Course.objects.filter(user=user).order_by('-id')
        courses_data = [
            {
                'id': c.id,
                'course_name': c.course_name,
                # canonical model field
                'course_number': c.course_number,
                # legacy alias used by the seafarer-application path
                'number': c.course_number,
                'issue_date': str(c.issue_date) if c.issue_date else None,
                'expiry_date': str(c.expiry_date) if c.expiry_date else None,
                'issued_by': c.issued_by,
                'issued_at': c.issued_at,
                'country_of_issue': c.country_of_issue,
                'file_url': file_url(c.document, download_path=build_download_url('course', c.id)) if c.document else None,
                'download_url': build_download_url('course', c.id) if c.document else None,
            }
            for c in courses_qs
        ]

        # Medical / Vaccinations
        from vaccinations.models import Vaccination
        vaccinations_qs = Vaccination.objects.filter(user=user)
        vaccinations_data = [
            {
                'id': v.id,
                'vaccine_name': v.name,
                'issue_date': str(v.issue_date) if v.issue_date else None,
                'expiry_date': str(v.expiry_date) if v.expiry_date else None,
                'first_dose_date': str(v.first_date) if v.first_date else None,
                'second_dose_date': str(v.last_date) if v.last_date else None,
                'remarks': v.remarks,
                'file_url': file_url(v.document, download_path=build_download_url('vaccination', v.id)) if v.document else None,
                'download_url': build_download_url('vaccination', v.id) if v.document else None,
            }
            for v in vaccinations_qs
        ]

        # Personal Documents (Visas / other IDs)
        from api.models import PersonalDocument
        personal_docs_qs = PersonalDocument.objects.filter(user=user)
        personal_docs_data = [
            {
                'id': pd.id,
                'document_type': pd.document_type,
                'document_number': pd.document_number,
                'issuing_country': pd.issuing_country,
                'issue_date': str(pd.issue_date) if pd.issue_date else None,
                'expiry_date': str(pd.expiry_date) if pd.expiry_date else None,
                'file_url': file_url(pd.file, download_path=build_download_url('personal_document', pd.id)) if pd.file else None,
                'download_url': build_download_url('personal_document', pd.id) if pd.file else None,
            }
            for pd in personal_docs_qs
        ]

        # Find specific records for singleton attachments
        coc_lic = licenses_qs.filter(document_name__icontains='coc').first()
        goc_lic = licenses_qs.filter(document_name__icontains='goc').first()
        med_cert = vaccinations_qs.filter(name="Medical Certificate For Seafarers").first()
        passport_doc = personal_docs_qs.filter(document_type__iexact='Passport').first()
        seaman_book_doc = personal_docs_qs.filter(document_type__iexact="Seaman's Book").first()
        other_seaman_book_doc = personal_docs_qs.filter(document_type__icontains="Seaman's Book").exclude(id=getattr(seaman_book_doc, 'id', None)).first()

        passport_file = user.passport_attachment if user.passport_attachment else getattr(passport_doc, 'file', None)
        passport_download_url = build_download_url('passport') if user.passport_attachment else (build_download_url('personal_document', passport_doc.id) if passport_doc and passport_doc.file else None)

        seaman_book_file = user.seaman_book_attachment if user.seaman_book_attachment else getattr(seaman_book_doc, 'file', None)
        seaman_book_download_url = build_download_url('seaman_book') if user.seaman_book_attachment else (build_download_url('personal_document', seaman_book_doc.id) if seaman_book_doc and seaman_book_doc.file else None)

        other_seaman_book_file = user.other_seaman_book_attachment if user.other_seaman_book_attachment else getattr(other_seaman_book_doc, 'file', None)
        other_seaman_book_download_url = build_download_url('other_seaman_book') if user.other_seaman_book_attachment else (build_download_url('personal_document', other_seaman_book_doc.id) if other_seaman_book_doc and other_seaman_book_doc.file else None)

        return {
            'passport': {
                'passport_no': user.passport_no,
                'issue_date': str(user.passport_issue_date) if user.passport_issue_date else None,
                'expiry_date': str(user.passport_expiry_date) if user.passport_expiry_date else None,
                'issued_by': user.passport_issued_by,
                'place_of_issue': user.passport_place_of_issue,
                'file_url': file_url(passport_file, download_path=passport_download_url) if passport_file else None,
                'download_url': passport_download_url,
            },
            'seaman_book': {
                'seaman_book_no': user.seaman_book_no,
                'issue_date': str(user.seaman_book_issue_date) if user.seaman_book_issue_date else None,
                'expiry_date': str(user.seaman_book_expiry_date) if user.seaman_book_expiry_date else None,
                'issued_by': user.seaman_book_issued_by,
                'place_of_issue': user.seaman_book_place_of_issue,
                'file_url': file_url(seaman_book_file, download_path=seaman_book_download_url) if seaman_book_file else None,
                'download_url': seaman_book_download_url,
            },
            'other_seaman_book': {
                'seaman_book_no': user.other_seaman_book_no,
                'issue_date': str(user.other_seaman_book_issue_date) if user.other_seaman_book_issue_date else None,
                'expiry_date': str(user.other_seaman_book_expiry_date) if user.other_seaman_book_expiry_date else None,
                'issued_by': user.other_seaman_book_issued_by,
                'place_of_issue': user.other_seaman_book_place_of_issue,
                'file_url': file_url(other_seaman_book_file, download_path=other_seaman_book_download_url) if other_seaman_book_file else None,
                'download_url': other_seaman_book_download_url,
            },
            'coc': {
                'certificate_name': user.coc_certificate_name,
                'certificate_number': user.coc_certificate_number,
                'issue_date': str(user.coc_issue_date) if user.coc_issue_date else None,
                'expiry_date': str(user.coc_expiry_date) if user.coc_expiry_date else None,
                'issued_by': user.coc_issued_by,
                'issued_at': user.coc_issued_at,
                'file_url': file_url(coc_lic.document_file, download_path=build_download_url('coc')) if coc_lic and coc_lic.document_file else None,
                'download_url': build_download_url('coc') if coc_lic and coc_lic.document_file else None,
            },
            'goc': {
                'certificate_number': user.goc_certificate_number,
                'issue_date': str(user.goc_issue_date) if user.goc_issue_date else None,
                'expiry_date': str(user.goc_expiry_date) if user.goc_expiry_date else None,
                'issued_by': user.goc_issued_by,
                'issued_at': user.goc_issued_at,
                'file_url': file_url(goc_lic.document_file, download_path=build_download_url('goc')) if goc_lic and goc_lic.document_file else None,
                'download_url': build_download_url('goc') if goc_lic and goc_lic.document_file else None,
            },
            'health_certificate': {
                'flag_state': user.health_flag_state,
                'number': user.health_number,
                'issue_date': str(user.health_issue_date) if user.health_issue_date else None,
                'expiry_date': str(user.health_expiry_date) if user.health_expiry_date else None,
                'issued_by': user.health_issued_by,
                'issued_at': user.health_issued_at,
                'international_medical_number': user.international_medical_number,
                'international_medical_issue_date': str(user.international_medical_issue_date) if user.international_medical_issue_date else None,
                'international_medical_expiry_date': str(user.international_medical_expiry_date) if user.international_medical_expiry_date else None,
                'file_url': file_url(med_cert.document, download_path=build_download_url('health_certificate')) if med_cert and med_cert.document else None,
                'download_url': build_download_url('health_certificate') if med_cert and med_cert.document else None,
                'records': vaccinations_data,
            },
            'licenses': licenses_data,
            'sea_service': sea_services_data,
            'marine_courses': courses_data,
            'personal_documents': personal_docs_data,
        }

    def get_certificates(self, obj):
        """
        Returns all certificates assigned to the linked user.
        Each entry contains: id, code, name.
        """
        return CertificateSerializer(
            obj.user.certificates.all(),
            many=True
        ).data

    def get_coded_rank(self, obj):
        """
        Returns all assigned rank codes for the user.
        Each entry contains: assigned_code, rank_code, rank_name.
        """
        user_ranks = obj.user.user_ranks.select_related('rank').order_by('-id')[:1]
        return [
            {
                'assigned_code': ur.assigned_code,
                'rank_code': ur.rank.code,
                'rank_name': ur.rank.name,
            }
            for ur in user_ranks
        ]

    def get_job_position_details(self, obj):
        if not obj.job_position:
            return None
        pos = obj.job_position
        return {
            'id': pos.id,
            'job_position_name': pos.rank.name if pos.rank else None,
            'quantity': pos.quantity,
            'salary_min': str(pos.salary_min) if pos.salary_min else None,
            'salary_max': str(pos.salary_max) if pos.salary_max else None,
            'currency': pos.currency,
            'contract_duration_months': pos.contract_duration_months,
            'remarks': pos.remarks
        }

    def get_seafarer_application(self, obj):
        """Return the full nested seafarer profile for the user linked to this CV submission."""
        if not obj.user:
            return None
        from .seafarer_application_serializers import SeafarerApplicationSerializer
        return SeafarerApplicationSerializer(obj.user, context={'exclude_headers': True}).data

    def get_company_details(self, obj):
        """Return nested company info or null if no company assigned."""
        if not obj.company:
            return None
        company = obj.company
        return {
            'id': company.id,
            'company_name': company.company_name,
            'company_type_name': str(company.company_type) if company.company_type else None,
            'company_flag_name': str(company.company_flag) if company.company_flag else None,
            'contact_person': getattr(company, 'contact_person', None),
            'contact_email': getattr(company, 'contact_email', None),
            'status': getattr(company, 'status', None),
        }

    def get_ship_details(self, obj):
        """Return nested ship info or null if no ship assigned."""
        if not obj.ship:
            return None
        ship = obj.ship
        ship_type = getattr(ship, 'ship_type', None)
        flag = getattr(ship, 'flag', None)
        return {
            'id': ship.id,
            'ship_name': ship.ship_name,
            'imo_number': getattr(ship, 'imo_number', None),
            'ship_type': str(ship_type) if ship_type else None,
            'flag': str(flag) if flag else None,
            'status': getattr(ship, 'status', None),
        }


# =====================
# CONTRACT SERIALIZERS
# =====================

class ContractListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    user_name = serializers.SerializerMethodField()
    ship_name = serializers.CharField(source='ship.ship_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    rank_name = serializers.CharField(source='rank.name', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'user', 'user_name', 'ship_name', 'company_name',
            'rank_name', 'sign_on_date', 'sign_off_date', 'status'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()


class ContractSerializer(serializers.ModelSerializer):
    # Read-only nested fields
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    rank_name = serializers.CharField(source='rank.name', read_only=True)
    
    # Extra fields
    generated_id = serializers.CharField(source='user.generated_id', read_only=True)
    assigned_code = serializers.SerializerMethodField()

    # Generate Contract from CV Submission
    cv_submission_id = serializers.IntegerField(write_only=True, required=False)
    cv_submission = serializers.IntegerField(write_only=True, required=False)
    
    # Custom ship processing
    ship_name = serializers.CharField(required=False)
    
    applicant_name = serializers.CharField(
        write_only=True, required=False,
        help_text="Optional: the full name of the targeted applicant. If provided alongside cv_submission, the backend validates it matches the CV's owner."
    )

    # Added detail fields (read-only)
    certificates = serializers.SerializerMethodField()
    coded_rank = serializers.SerializerMethodField()
    user_documents = serializers.SerializerMethodField()
    job_position_details = serializers.SerializerMethodField()
    ship_details = serializers.SerializerMethodField()
    company_details = serializers.SerializerMethodField()

    # Seafarer Application Integration (Capabilities)
    seafarer_application = serializers.SerializerMethodField()
    document_info = serializers.JSONField(required=False, write_only=True)
    application_header = serializers.JSONField(required=False, write_only=True)
    personal_details = serializers.JSONField(required=False, write_only=True)
    education = serializers.JSONField(required=False, write_only=True)
    contact_details = serializers.JSONField(required=False, write_only=True)
    travel_documents = serializers.JSONField(required=False, write_only=True)
    professional_qualification = serializers.JSONField(required=False, write_only=True)
    next_of_kin = serializers.JSONField(required=False, write_only=True)
    health_certificates = serializers.JSONField(required=False, write_only=True)
    marine_courses = serializers.JSONField(required=False, write_only=True)
    sea_service_details = serializers.JSONField(required=False, write_only=True)
    references = serializers.JSONField(required=False, write_only=True)
    declaration = serializers.JSONField(required=False, write_only=True)
    for_office_use_only = serializers.JSONField(required=False, write_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'cv_submission_id', 'cv_submission',
            'user', 'user_name', 'user_email', 'generated_id',
            'applicant_name',
            'ship', 'ship_name', 'ship_details',
            'company', 'company_name', 'company_details',
            'rank', 'rank_name', 'assigned_code', 'job_position',
            'sign_on_date', 'sign_off_date', 'salary', 'currency', 'status',
            'signed_file', 'signed_at',
            'certificates', 'coded_rank', 'user_documents', 'job_position_details',
            'seafarer_application', 'document_info', 'application_header', 'personal_details',
            'education', 'contact_details', 'travel_documents', 'professional_qualification',
            'next_of_kin', 'health_certificates', 'marine_courses', 'sea_service_details',
            'references', 'declaration', 'for_office_use_only',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {'required': False},
            'rank': {'required': False},
            'ship': {'required': False},
        }

    def validate(self, data):
        """
        Check for logical date discrepancies.
        """
        sign_on = data.get('sign_on_date')
        sign_off = data.get('sign_off_date')

        if sign_on and sign_off and sign_off < sign_on:
            raise serializers.ValidationError({
                "sign_off_date": "Sign-off date cannot be before the sign-on date."
            })
            
        return data

    def validate_job_position(self, value):
        if value is not None:
            if value.quantity <= 0:
                raise serializers.ValidationError("This Job Order Position has 0 openings. You cannot assign any applicants to it.")
            
            # Count existing active/pending contracts for this job position
            from api.models import Contract
            exclude_id = self.instance.id if (hasattr(self, 'instance') and self.instance) else None
            qs = Contract.objects.filter(
                job_position=value,
                status__in=['Pending', 'Signed', 'Pending Signature', 'Active']
            )
            if exclude_id:
                qs = qs.exclude(id=exclude_id)
            
            assigned_count = qs.count()
            if assigned_count >= value.quantity:
                raise serializers.ValidationError(
                    f"This Job Order Position is already fully assigned ({assigned_count}/{value.quantity} filled). You cannot assign any more applicants."
                )
        return value

    def validate_overlap(self, user, sign_on_date, sign_off_date, job_position=None, instance_id=None):
        """
        Ensures the seafarer doesn't have another Active/Signed/Pending contract 
        during the same time period.
        """
        if not user or not sign_on_date:
            return

        from datetime import timedelta
        from rest_framework.exceptions import ValidationError
        
        new_start = sign_on_date
        new_end = sign_off_date
        
        if not new_end and job_position:
            duration_months = job_position.contract_duration_months or 6
            new_end = new_start + timedelta(days=30 * duration_months)
        
        # Find existing active/pending contracts for this user
        existing_contracts = Contract.objects.filter(
            user=user, 
            status__in=['Pending', 'Pending Signature', 'Signed', 'Active']
        )
        if instance_id:
            existing_contracts = existing_contracts.exclude(id=instance_id)
            
        for ec in existing_contracts:
            ec_start = ec.sign_on_date
            ec_end = ec.sign_off_date
            
            # If existing contract has no sign_off_date, estimate it for the check
            if not ec_end:
                if ec.job_position:
                    ec_duration = ec.job_position.contract_duration_months or 6
                    ec_end = ec_start + timedelta(days=30 * ec_duration)
                else:
                    ec_end = ec_start + timedelta(days=180) # Default 6 months
            
            # Overlap check logic
            is_overlap = False
            if new_end:
                # If we have both start and end for new contract
                if new_start <= ec_end and new_end >= ec_start:
                    is_overlap = True
            else:
                # If we only have start for new contract, check if it falls within existing contract
                if ec_start <= new_start <= ec_end:
                    is_overlap = True

            if is_overlap:
                raise ValidationError({
                    'error': f"Applicant {user.first_name} is already assigned to a ship during this period (From {ec_start} to {ec_end}). Overlapping Contract ID: {ec.id}"
                })

    @staticmethod
    def parse_salary_value(salary_str):
        if not salary_str:
            return None
        import re
        match = re.match(r'^([\d\.,]+)', str(salary_str).strip())
        if match:
            val = match.group(1).replace(',', '')
            try:
                return float(val)
            except ValueError:
                pass
        return None

    @staticmethod
    def parse_salary_currency(salary_str):
        if not salary_str:
            return None
        salary_str = str(salary_str).strip().upper()
        for currency in ['USD', 'EUR', 'GBP', 'EGP']:
            if currency in salary_str:
                return currency
        return None

    def create(self, validated_data):
        # Extract Seafarer Application fields
        seafarer_fields = [
            'document_info', 'application_header', 'personal_details', 
            'education', 'contact_details', 'travel_documents', 
            'professional_qualification', 'next_of_kin', 'health_certificates', 
            'marine_courses', 'sea_service_details', 'references', 
            'declaration', 'for_office_use_only'
        ]
        seafarer_data = {}
        for f in seafarer_fields:
            if f in validated_data:
                seafarer_data[f] = validated_data.pop(f)

        cv_sub_id = validated_data.pop('cv_submission_id', None) or validated_data.pop('cv_submission', None)
        ship_name_val = validated_data.pop('ship_name', None)
        applicant_name = validated_data.pop('applicant_name', None)

        if ship_name_val:
            from ships.models import Ship
            from rest_framework.exceptions import ValidationError
            try:
                ship_obj = Ship.objects.get(ship_name__iexact=ship_name_val)
                validated_data['ship'] = ship_obj
            except Ship.DoesNotExist:
                raise ValidationError({'ship_name': f"Ship with name '{ship_name_val}' not found."})

        if cv_sub_id:
            from api.models import CVSubmission
            from rest_framework.exceptions import ValidationError
            try:
                cv_sub = CVSubmission.objects.get(id=cv_sub_id)

                # Validate applicant_name matches the CV owner if provided
                if applicant_name:
                    user = cv_sub.user
                    full_name = f"{user.first_name} {user.middle_name}".strip() if user.middle_name else user.first_name
                    if applicant_name.strip().lower() not in [full_name.lower(), user.first_name.lower()]:
                        from rest_framework.exceptions import ValidationError
                        raise ValidationError({
                            'applicant_name': f"Name '{applicant_name}' does not match the applicant on CV #{cv_sub_id} ('{full_name}'). Please verify you have the right CV."
                        })

                if not cv_sub.position:
                    raise ValidationError({'error': 'This CV Submission has no assigned position/rank. Cannot generate a contract.'})
                if not cv_sub.company:
                    raise ValidationError({'error': 'This CV Submission has no linked company. Cannot generate a contract.'})
                
                validated_data['user'] = cv_sub.user
                validated_data['company'] = cv_sub.company
                validated_data['rank'] = cv_sub.position
                
                if cv_sub.job_position:
                    validated_data['job_position'] = cv_sub.job_position
                    
                # Auto-fill salary from CV submission expected salary (user.salary) or fallback to job_position.salary_max
                if 'salary' not in validated_data or validated_data['salary'] is None:
                    user_sal = None
                    if cv_sub.user and cv_sub.user.salary:
                        user_sal = self.parse_salary_value(cv_sub.user.salary)
                    
                    if user_sal is not None:
                        validated_data['salary'] = user_sal
                    elif cv_sub.job_position and cv_sub.job_position.salary_max:
                        validated_data['salary'] = cv_sub.job_position.salary_max

                # Auto-fill currency from CV submission expected salary currency or fallback to job_position.currency
                if 'currency' not in validated_data or validated_data['currency'] is None:
                    user_currency = None
                    if cv_sub.user and cv_sub.user.salary:
                        user_currency = self.parse_salary_currency(cv_sub.user.salary)
                    
                    if user_currency:
                        validated_data['currency'] = user_currency
                    elif cv_sub.job_position and cv_sub.job_position.currency:
                        validated_data['currency'] = cv_sub.job_position.currency

                # IMPORTANT: Also update the ship on the CV submission itself so it shows up in CV endpoints
                if 'ship' in validated_data and validated_data['ship']:
                    cv_sub.ship = validated_data['ship']
                    cv_sub.save(update_fields=['ship'])

            except CVSubmission.DoesNotExist:
                raise ValidationError({'error': f'CV Submission with id {cv_sub_id} not found.'})
        
        # --- Overlap Validation ---
        new_status = validated_data.get('status', 'Pending')
        if new_status in ['Pending', 'Pending Signature', 'Signed', 'Active']:
            self.validate_overlap(
                user=validated_data.get('user'),
                sign_on_date=validated_data.get('sign_on_date'),
                sign_off_date=validated_data.get('sign_off_date'),
                job_position=validated_data.get('job_position')
            )
        # --------------------------
        
        contract = super().create(validated_data)

        # Decrease Job Order Position quantity
        if contract.job_position:
            contract.job_position.quantity = max(0, contract.job_position.quantity - 1)
            contract.job_position.save(update_fields=['quantity'])
            
            # Also decrease the company's overall open_positions
            if contract.company:
                contract.company.open_positions = max(0, contract.company.open_positions - 1)
                contract.company.save(update_fields=['open_positions'])

        # Add user to ship's crew
        if contract.ship and contract.user:
            contract.ship.crew.add(contract.user)

        # Apply Seafarer Application updates to the linked user
        if seafarer_data and contract.user:
            from .seafarer_application_serializers import SeafarerApplicationSerializer
            SeafarerApplicationSerializer().update(contract.user, seafarer_data)

        return contract

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['ship_name'] = instance.ship.ship_name if instance.ship else None
        
        # Ensure salary is equal to user expected salary (from CV submission/user profile) if contract salary is null
        if (repr.get('salary') is None or repr.get('salary') == '') and instance.user:
            user_sal = self.parse_salary_value(instance.user.salary)
            if user_sal is not None:
                repr['salary'] = f"{user_sal:.2f}"
                
        return repr

    def update(self, instance, validated_data):
        # Extract Seafarer Application fields
        seafarer_fields = [
            'document_info', 'application_header', 'personal_details', 
            'education', 'contact_details', 'travel_documents', 
            'professional_qualification', 'next_of_kin', 'health_certificates', 
            'marine_courses', 'sea_service_details', 'references', 
            'declaration', 'for_office_use_only'
        ]
        seafarer_data = {}
        for f in seafarer_fields:
            if f in validated_data:
                seafarer_data[f] = validated_data.pop(f)

        validated_data.pop('applicant_name', None)

        # --- Overlap Validation ---
        # Validate if dates, user, or status are changing, AND the status is active/pending
        new_status = validated_data.get('status', instance.status)
        if new_status in ['Pending', 'Pending Signature', 'Signed', 'Active']:
            if any(f in validated_data for f in ['sign_on_date', 'sign_off_date', 'user', 'status']):
                self.validate_overlap(
                    user=validated_data.get('user', instance.user),
                    sign_on_date=validated_data.get('sign_on_date', instance.sign_on_date),
                    sign_off_date=validated_data.get('sign_off_date', instance.sign_off_date),
                    job_position=validated_data.get('job_position', instance.job_position),
                    instance_id=instance.id
                )
        # --------------------------

        old_ship = instance.ship
        old_user = instance.user

        contract = super().update(instance, validated_data)

        # Sync crew list if ship or user changed
        if contract.ship != old_ship or contract.user != old_user:
            if old_ship and old_user:
                old_ship.crew.remove(old_user)
            if contract.ship and contract.user:
                contract.ship.crew.add(contract.user)

        # Apply Seafarer Application updates to the linked user
        if seafarer_data and contract.user:
            from .seafarer_application_serializers import SeafarerApplicationSerializer
            SeafarerApplicationSerializer().update(contract.user, seafarer_data)

        return contract

    def get_seafarer_application(self, obj):
        if not obj.user: return None
        from .seafarer_application_serializers import SeafarerApplicationSerializer
        return SeafarerApplicationSerializer(obj.user).data

    def get_user_name(self, obj):
        if not obj.user: return ""
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()

    def get_assigned_code(self, obj):
        if not obj.user or not obj.rank:
            return None
        # Use first() to safely handle cases where the user does not have this rank assigned
        user_rank = obj.user.user_ranks.filter(rank=obj.rank).first()
        return user_rank.assigned_code if user_rank else None

    def get_certificates(self, obj):
        if not obj.user: return []
        return CertificateSerializer(obj.user.certificates.all(), many=True).data

    def get_coded_rank(self, obj):
        if not obj.user: return []
        user_ranks = obj.user.user_ranks.select_related('rank').order_by('-id')[:1]
        return [
            {
                'assigned_code': ur.assigned_code,
                'rank_code': ur.rank.code,
                'rank_name': ur.rank.name,
            }
            for ur in user_ranks
        ]

    def get_user_documents(self, obj):
        if not obj.user: return {}
        user = obj.user
        request = self.context.get('request')

        def file_url(field, download_path=None):
            if not field:
                return None
            if download_path:
                if request:
                    return request.build_absolute_uri(download_path)
                return download_path
            if request:
                return request.build_absolute_uri(field.url)
            return field.url

        # Licenses (from licenses app)
        from licenses.models import UserLicense
        licenses_qs = UserLicense.objects.filter(user=user)
        licenses_data = [
            {
                'id': lic.id,
                'document_name': lic.document_name,
                'document_number': lic.document_number,
                'country_of_issue': lic.country_of_issue,
                'issue_date': str(lic.issue_date) if lic.issue_date else None,
                'expiration_date': str(lic.expiration_date) if lic.expiration_date else None,
                'file_url': file_url(lic.document_file, download_path=f"/api/users/{user.id}/download-license/{lic.id}/") if lic.document_file else None,
                'download_url': f"/api/users/{user.id}/download-license/{lic.id}/" if lic.document_file else None,
            }
            for lic in licenses_qs
        ]

        # Sea Services
        sea_services_qs = user.sea_services.all()
        from api.models import Rank
        from core.models import VesselType, Flag
        ranks_dict = {str(r.id): r.name for r in Rank.objects.all()}
        vessels_dict = {str(v.id): v.name for v in VesselType.objects.all()}
        flags_dict = {str(f.id): f.name for f in Flag.objects.all()}

        sea_services_data = [
            {
                'id': ss.id,
                'vessel_name': ss.vessel_name,
                'rank': ranks_dict.get(str(ss.rank), ss.rank) if ss.rank else '',
                'vessel_type': vessels_dict.get(str(ss.vessel_type), ss.vessel_type) if getattr(ss, 'vessel_type', None) else '',
                'flag': flags_dict.get(str(ss.flag), ss.flag) if getattr(ss, 'flag', None) else '',
                'signed_on': str(ss.signed_on) if ss.signed_on else None,
                'signed_off': str(ss.signed_off) if ss.signed_off else None,
                'file_url': file_url(ss.file, download_path=f"/api/users/{user.id}/download-sea-service/{ss.id}/") if ss.file else None,
                'download_url': f"/api/users/{user.id}/download-sea-service/{ss.id}/" if ss.file else None,
            }
            for ss in sea_services_qs
        ]

        # Marine Courses
        from courses.models import Course
        courses_qs = Course.objects.filter(user=user)
        courses_data = [
            {
                'id': c.id,
                'course_name': c.course_name,
                'issue_date': str(c.issue_date) if c.issue_date else None,
                'expiry_date': str(c.expiry_date) if c.expiry_date else None,
                'file_url': file_url(c.document, download_path=f"/api/users/{user.id}/download-course/{c.id}/") if c.document else None,
                'download_url': f"/api/users/{user.id}/download-course/{c.id}/" if c.document else None,
            }
            for c in courses_qs
        ]

        # Medical / Vaccinations
        from vaccinations.models import Vaccination
        vaccinations_qs = Vaccination.objects.filter(user=user)
        vaccinations_data = [
            {
                'id': v.id,
                'vaccine_name': v.name,
                'issue_date': str(v.issue_date) if v.issue_date else None,
                'expiry_date': str(v.expiry_date) if v.expiry_date else None,
                'first_dose_date': str(v.first_date) if v.first_date else None,
                'second_dose_date': str(v.last_date) if v.last_date else None,
                'remarks': v.remarks,
                'file_url': file_url(v.document, download_path=f"/api/users/{user.id}/download-vaccination/{v.id}/") if v.document else None,
                'download_url': f"/api/users/{user.id}/download-vaccination/{v.id}/" if v.document else None,
            }
            for v in vaccinations_qs
        ]

        # Personal Documents (Visas / other IDs)
        from api.models import PersonalDocument
        personal_docs_qs = PersonalDocument.objects.filter(user=user)
        personal_docs_data = [
            {
                'id': pd.id,
                'document_type': pd.document_type,
                'document_number': pd.document_number,
                'issuing_country': pd.issuing_country,
                'issue_date': str(pd.issue_date) if pd.issue_date else None,
                'expiry_date': str(pd.expiry_date) if pd.expiry_date else None,
                'file_url': file_url(pd.file, download_path=f"/api/users/{user.id}/download-personal-document/{pd.id}/") if pd.file else None,
                'download_url': f"/api/users/{user.id}/download-personal-document/{pd.id}/" if pd.file else None,
            }
            for pd in personal_docs_qs
        ]

        # Find specific records for singleton attachments
        coc_lic = licenses_qs.filter(document_name__icontains='coc').first()
        goc_lic = licenses_qs.filter(document_name__icontains='goc').first()
        med_cert = vaccinations_qs.filter(name="Medical Certificate For Seafarers").first()

        return {
            'passport': {
                'passport_no': user.passport_no,
                'issue_date': str(user.passport_issue_date) if user.passport_issue_date else None,
                'expiry_date': str(user.passport_expiry_date) if user.passport_expiry_date else None,
                'issued_by': user.passport_issued_by,
                'place_of_issue': user.passport_place_of_issue,
                'file_url': file_url(user.passport_attachment, download_path=f"/api/users/{user.id}/download-passport/") if user.passport_attachment else None,
                'download_url': f"/api/users/{user.id}/download-passport/" if user.passport_attachment else None,
            },
            'seaman_book': {
                'seaman_book_no': user.seaman_book_no,
                'issue_date': str(user.seaman_book_issue_date) if user.seaman_book_issue_date else None,
                'expiry_date': str(user.seaman_book_expiry_date) if user.seaman_book_expiry_date else None,
                'issued_by': user.seaman_book_issued_by,
                'place_of_issue': user.seaman_book_place_of_issue,
                'file_url': file_url(user.seaman_book_attachment, download_path=f"/api/users/{user.id}/download-seaman-book/") if user.seaman_book_attachment else None,
                'download_url': f"/api/users/{user.id}/download-seaman-book/" if user.seaman_book_attachment else None,
            },
            'other_seaman_book': {
                'seaman_book_no': user.other_seaman_book_no,
                'issue_date': str(user.other_seaman_book_issue_date) if user.other_seaman_book_issue_date else None,
                'expiry_date': str(user.other_seaman_book_expiry_date) if user.other_seaman_book_expiry_date else None,
                'issued_by': user.other_seaman_book_issued_by,
                'place_of_issue': user.other_seaman_book_place_of_issue,
                'file_url': file_url(user.other_seaman_book_attachment, download_path=f"/api/users/{user.id}/download-other-seaman-book/") if user.other_seaman_book_attachment else None,
                'download_url': f"/api/users/{user.id}/download-other-seaman-book/" if user.other_seaman_book_attachment else None,
            },
            'coc': {
                'certificate_name': user.coc_certificate_name,
                'certificate_number': user.coc_certificate_number,
                'issue_date': str(user.coc_issue_date) if user.coc_issue_date else None,
                'expiry_date': str(user.coc_expiry_date) if user.coc_expiry_date else None,
                'issued_by': user.coc_issued_by,
                'issued_at': user.coc_issued_at,
                'file_url': file_url(coc_lic.document_file, download_path=f"/api/users/{user.id}/download-document/?type=coc") if coc_lic and coc_lic.document_file else None,
                'download_url': f"/api/users/{user.id}/download-document/?type=coc" if coc_lic and coc_lic.document_file else None,
            },
            'goc': {
                'certificate_number': user.goc_certificate_number,
                'issue_date': str(user.goc_issue_date) if user.goc_issue_date else None,
                'expiry_date': str(user.goc_expiry_date) if user.goc_expiry_date else None,
                'issued_by': user.goc_issued_by,
                'issued_at': user.goc_issued_at,
                'file_url': file_url(goc_lic.document_file, download_path=f"/api/users/{user.id}/download-document/?type=goc") if goc_lic and goc_lic.document_file else None,
                'download_url': f"/api/users/{user.id}/download-document/?type=goc" if goc_lic and goc_lic.document_file else None,
            },
            'health_certificate': {
                'flag_state': user.health_flag_state,
                'number': user.health_number,
                'issue_date': str(user.health_issue_date) if user.health_issue_date else None,
                'expiry_date': str(user.health_expiry_date) if user.health_expiry_date else None,
                'issued_by': user.health_issued_by,
                'issued_at': user.health_issued_at,
                'international_medical_number': user.international_medical_number,
                'international_medical_issue_date': str(user.international_medical_issue_date) if user.international_medical_issue_date else None,
                'international_medical_expiry_date': str(user.international_medical_expiry_date) if user.international_medical_expiry_date else None,
                'file_url': file_url(med_cert.document, download_path=f"/api/users/{user.id}/download-document/?type=health_certificate") if med_cert and med_cert.document else None,
                'download_url': f"/api/users/{user.id}/download-document/?type=health_certificate" if med_cert and med_cert.document else None,
                'records': vaccinations_data,
            },
            'licenses': licenses_data,
            'sea_service': sea_services_data,
            'marine_courses': courses_data,
            'personal_documents': personal_docs_data,
        }

    def get_job_position_details(self, obj):
        if not obj.job_position:
            return None
        pos = obj.job_position
        return {
            'id': pos.id,
            'job_position_name': pos.rank.name if pos.rank else None,
            'quantity': pos.quantity,
            'salary_min': str(pos.salary_min) if pos.salary_min else None,
            'salary_max': str(pos.salary_max) if pos.salary_max else None,
            'currency': pos.currency,
            'contract_duration_months': pos.contract_duration_months,
            'remarks': pos.remarks
        }

    def get_ship_details(self, obj):
        """Return nested ship info (id, name, type, flag, IMO) or null if no ship assigned."""
        if not obj.ship:
            return None
        ship = obj.ship
        ship_type = getattr(ship, 'ship_type', None)
        flag = getattr(ship, 'flag', None)
        return {
            'id': ship.id,
            'ship_name': ship.ship_name,
            'imo_number': getattr(ship, 'imo_number', None),
            'ship_type': str(ship_type) if ship_type else None,
            'flag': str(flag) if flag else None,
            'status': getattr(ship, 'status', None),
        }

    def get_company_details(self, obj):
        """Return nested company info (id, name, type, country) or null if no company assigned."""
        if not obj.company:
            return None
        company = obj.company
        return {
            'id': company.id,
            'company_name': company.company_name,
            'company_type_name': str(company.company_type) if company.company_type else None,
            'company_flag_name': str(company.company_flag) if company.company_flag else None,
            'contact_person': getattr(company, 'contact_person', None),
            'contact_email': getattr(company, 'contact_email', None),
            'status': getattr(company, 'status', None),
        }


# =====================
# USER SERIALIZERS
# =====================

class UsersSerializer(serializers.ModelSerializer):
    # first_name and middle_name are declared as plain model fields so
    # that POST / PUT / PATCH body values actually land on the model.
    # (The previous SerializerMethodField declarations made them
    # read-only, so the `to_internal_value` split logic never ran and
    # writes were silently dropped.) `to_representation` below still
    # combines first + middle into the response's `first_name` so the
    # frontend's "full name in first_name" assumption keeps working.

    # Exclude inherited M2M fields from `__all__` so we can declare
    # them as proper PrimaryKeyRelatedField with the right queryset.
    # They're still writable; the extra_kwargs / explicit declarations
    # below just give DRF the queryset it needs to validate the IDs.
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False,
        help_text="List of Permission IDs to assign.",
    )
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
        help_text="List of Group IDs to assign.",
    )

    # Read-only nested serializers for detailed representation
    ranks = UserRankSerializer(source='user_ranks', many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    sea_services = SeaServiceSerializer(many=True, read_only=True)
    user_documents = serializers.SerializerMethodField()
    seafarer_application = serializers.SerializerMethodField()
    coded_rank = serializers.SerializerMethodField()
    salary_display = serializers.CharField(source='salary', read_only=True)

    # Write-only fields for accepting lists of IDs during create/update
    rank_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        source='codes',
        required=False,
        help_text="List of Rank IDs or codes/names to assign."
    )
    certificate_ids = serializers.PrimaryKeyRelatedField(
        queryset=Certificate.objects.all(),
        many=True,
        write_only=True,
        source='certificates',
        required=False,
        help_text="List of Certificate IDs to assign."
    )

    # Password field for user creation (write-only) — accepted on
    # input, never echoed back in responses.
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    # Use FlexibleFileField for file fields to handle existing URLs from frontend
    profile_image = FlexibleFileField(required=False, allow_null=True)
    marlins_test_attachment = FlexibleFileField(required=False, allow_null=True)
    ces_test_attachment = FlexibleFileField(required=False, allow_null=True)
    passport_attachment = FlexibleFileField(required=False, allow_null=True)
    seaman_book_attachment = FlexibleFileField(required=False, allow_null=True)
    other_seaman_book_attachment = FlexibleFileField(required=False, allow_null=True)
    file = FlexibleFileField(required=False, allow_null=True)

    class Meta:
        model = Users
        # fields = '__all__' makes every model column writable by
        # default. The 5 explicitly-excluded fields below are controlled
        # via extra_kwargs:
        #   - id, created_at, updated_at : auto-managed by the model
        #     (auto_now_add / auto_now / primary key). DRF picks them
        #     up as read-only automatically.
        #   - generated_id : read-only in extra_kwargs; the 12-digit
        #     ID is assigned by a separate Document-approval flow.
        #   - password : write-only in extra_kwargs; accepted on input,
        #     never echoed back in responses. (Hashed on save by
        #     the custom update() below.)
        fields = '__all__'
        extra_kwargs = {
            'profile_image': {'required': False},
            'password': {'write_only': True, 'required': False},
            'generated_id': {'read_only': True},
            'salary': {'required': False, 'allow_null': True},
            'next_of_kin_email': {'required': False, 'allow_null': True},
        }

    def to_internal_value(self, data):
        if 'first_name' in data:
            full_name = str(data.get('first_name') or '').strip()
            if ' ' in full_name:
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                parts = full_name.split(' ', 1)
                data['first_name'] = parts[0]
                data['middle_name'] = parts[1] if len(parts) > 1 else ''

        # Pre-process 'application_for_position' if it's a list or an ID
        if 'application_for_position' in data:
            val = data.get('application_for_position')
            # Handle list input
            if isinstance(val, list):
                val = val[0] if len(val) > 0 else None
            
            if val:
                from api.models import Rank
                rank_obj = None
                # Handle ID input (integer or numeric string)
                if isinstance(val, int) or (isinstance(val, str) and str(val).isdigit()):
                    rank_obj = Rank.objects.filter(id=int(val)).first()
                # Handle string name input
                elif isinstance(val, str):
                    rank_obj = Rank.objects.filter(name__iexact=val).first()
                
                if rank_obj:
                    if hasattr(data, 'copy'):
                        data = data.copy()
                    else:
                        data = dict(data)
                    data['application_for_position'] = rank_obj.name
                else:
                    # Fallback to the string value if no rank found
                    if hasattr(data, 'copy'):
                        data = data.copy()
                    else:
                        data = dict(data)
                    data['application_for_position'] = str(val)

        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Override to ensure proper serialization of nested fields"""
        representation = super().to_representation(instance)
        # Combine first_name and middle_name for the frontend which binds full_name to first_name
        representation['first_name'] = f"{instance.first_name} {instance.middle_name}".strip()

        # Hide generated_id for non-privileged users
        request = self.context.get('request')
        if request and hasattr(request.user, 'role'):
            has_permission = request.user.is_authenticated and getattr(request.user, 'role', '') in ['Admin', 'HR Manager', 'Recruiter', 'admin'] or getattr(request.user, 'is_superuser', False)
            if not has_permission:
                representation.pop('generated_id', None)

        # Keep application_for_position as a string to prevent frontend .trim() crashes
        # Provide rank_code and assigned_code as separate top-level fields
        app_pos_name = instance.application_for_position
        
        # 1. Try to find the user rank that exactly matches the string
        ur = None
        if app_pos_name:
            ur = instance.user_ranks.filter(rank__name__iexact=app_pos_name).first()
            
        # 2. If no exact match, fallback to the user's first assigned rank
        if not ur:
            ur = instance.user_ranks.first()

        if ur:
            representation['application_for_position'] = ur.rank.name
            representation['rank_code'] = ur.rank.code
            representation['assigned_code'] = ur.assigned_code
        elif app_pos_name:
            # 3. Fallback: they have a string but no assigned user_rank yet
            from api.models import Rank
            rank = Rank.objects.filter(name__iexact=app_pos_name).first()
            representation['application_for_position'] = app_pos_name
            representation['rank_code'] = rank.code if rank else None
            representation['assigned_code'] = None
        else:
            representation['application_for_position'] = None
            representation['rank_code'] = None
            representation['assigned_code'] = None

        # Explicitly serialize ranks with assigned_code
        representation['ranks'] = UserRankSerializer(
            instance.user_ranks.all(),
            many=True
        ).data

        # Serialize certificates
        representation['certificates'] = CertificateSerializer(
            instance.certificates.all(),
            many=True
        ).data

        # Serialize references
        representation['references'] = ReferenceSerializer(
            instance.references.all(),
            many=True
        ).data

        # Serialize sea services
        representation['sea_services'] = SeaServiceSerializer(
            instance.sea_services.all(),
            many=True
        ).data

        # Remove the codes field from output (internal use only)
        representation.pop('codes', None)

        # Calculate BMI from Height_Cm and Weight_Kg
        height_cm = instance.Height_Cm or 0
        weight_kg = instance.Weight_Kg or 0
        if height_cm > 0 and weight_kg > 0:
            height_m = height_cm / 100
            bmi_value = round(weight_kg / (height_m ** 2), 1)
            if bmi_value < 18.5:
                bmi_category = 'Underweight'
            elif bmi_value < 25:
                bmi_category = 'Normal'
            elif bmi_value < 30:
                bmi_category = 'Overweight'
            else:
                bmi_category = 'Obese'
            representation['bmi'] = {
                'value': bmi_value,
                'category': bmi_category
            }
        else:
            representation['bmi'] = None

        # Rewrite file fields to use secure download URLs instead of raw media URLs
        for field_name, doc_type in [
            ('marlins_test_attachment', 'marlins'),
            ('ces_test_attachment', 'ces'),
            ('passport_attachment', 'passport'),
            ('seaman_book_attachment', 'seaman_book'),
            ('other_seaman_book_attachment', 'other_seaman_book'),
        ]:
            if representation.get(field_name):
                download_path = f"/api/users/users/{instance.id}/download-document/?type={doc_type}"
                if request:
                    representation[field_name] = request.build_absolute_uri(download_path)
                else:
                    representation[field_name] = download_path

        return representation

    def create(self, validated_data):
        # Pop the relationship data first
        codes_data = validated_data.pop('codes', [])
        certificates_data = validated_data.pop('certificates', [])
        profile_image_data = validated_data.pop('profile_image', None)
        password = validated_data.pop('password', None)

        # Create the user instance with the remaining standard fields
        user = Users(**validated_data)

        # Set password properly (if provided)
        if password:
            user.set_password(password)

        # Save the user
        user.save()

        # Handle the profile image if it was provided
        if profile_image_data:
            user.profile_image = profile_image_data
            user.save()

        # Handle the M2M relationships
        from django.db.models import Q
        for rank_identifier in codes_data:
            rank_identifier = str(rank_identifier).strip()
            rank_obj = None
            if rank_identifier.isdigit():
                try:
                    rank_obj = Rank.objects.get(pk=int(rank_identifier))
                except Rank.DoesNotExist:
                    pass
            if not rank_obj:
                rank_obj = Rank.objects.filter(Q(code__iexact=rank_identifier) | Q(name__iexact=rank_identifier)).first()
            if rank_obj:
                UserRank.objects.create(user=user, rank=rank_obj)
        if certificates_data:
            user.certificates.set(certificates_data)

        return user

    def update(self, instance, validated_data):
        # Filter out "KEEP_EXISTING" markers (sent by FlexibleFileField for existing URLs)
        validated_data = {k: v for k, v in validated_data.items() if v != "KEEP_EXISTING"}

        # TEMPORARY DEBUG: Write to a file we can inspect
        import datetime
        log_path = r'd:\photo_debug_real.log'
        with open(log_path, 'a') as f:
            f.write(f"\n--- {datetime.datetime.now()} ---\n")
            f.write(f"Updating user {instance.id}\n")
            f.write(f"'profile_image' in validated_data: {'profile_image' in validated_data}\n")
            if 'profile_image' in validated_data:
                val = validated_data['profile_image']
                f.write(f"profile_image value: {val}, type: {type(val)}\n")
            f.write(f"Current DB value BEFORE: {instance.profile_image.name if instance.profile_image else 'EMPTY'}\n")

        # FIREWALL: Prevent accidental deletion of file fields if an empty/falsy value is sent!
        file_fields = ['profile_image', 'marlins_test_attachment', 'ces_test_attachment', 'passport_attachment', 'seaman_book_attachment', 'other_seaman_book_attachment']
        for ff in file_fields:
            if ff in validated_data:
                if validated_data.get(ff) == "DELETE_PHOTO":
                    # User explicitly requested to delete the file
                    validated_data[ff] = None
                    with open(log_path, 'a') as f:
                        f.write(f"FIREWALL: Explicit DELETE_PHOTO requested for {ff}.\n")
                elif not validated_data.get(ff):
                    validated_data.pop(ff)
                    with open(log_path, 'a') as f:
                        f.write(f"FIREWALL ACTIVATED - removed empty {ff} from payload\n")

        # Pop relationship and file data
        codes_data = validated_data.pop('codes', None)
        certificates_data = validated_data.pop('certificates', None)
        
        has_profile_image = 'profile_image' in validated_data
        profile_image_data = validated_data.pop('profile_image', None)

        # Update standard fields using the default DRF update method
        # Pop + hash the password first so DRF's default update doesn't
        # store it in plaintext. (Without this, PATCH {password: "x"} would
        # write the raw value into Users.password and the user couldn't
        # log in.)
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save(update_fields=['password'])

        # Handle the profile image update separately if it was in the request (even if None)
        if has_profile_image:
            instance.profile_image = profile_image_data
            instance.save(update_fields=['profile_image'])
            
        with open(log_path, 'a') as f:
            f.write(f"AFTER save, DB value: {instance.profile_image.name if instance.profile_image else 'EMPTY'}\n")

        # Handle relationship updates
        if codes_data is not None:
            instance.user_ranks.all().delete()
            from django.db.models import Q
            for rank_identifier in codes_data:
                rank_identifier = str(rank_identifier).strip()
                rank_obj = None
                if rank_identifier.isdigit():
                    try:
                        rank_obj = Rank.objects.get(pk=int(rank_identifier))
                    except Rank.DoesNotExist:
                        pass
                if not rank_obj:
                    rank_obj = Rank.objects.filter(Q(code__iexact=rank_identifier) | Q(name__iexact=rank_identifier)).first()
                if rank_obj:
                    UserRank.objects.create(user=instance, rank=rank_obj)
        if certificates_data is not None:
            instance.certificates.set(certificates_data)

        return instance

    def get_user_documents(self, obj):
        user = obj
        request = self.context.get('request')

        def build_download_url(doc_type, doc_id=None):
            url = f"/api/users/users/{user.id}/download-document/?type={doc_type}"
            if doc_id:
                url += f"&doc_id={doc_id}"
            return url

        def file_url(field, download_path=None):
            if not field:
                return None
            if download_path:
                if request:
                    return request.build_absolute_uri(download_path)
                return download_path
            if request:
                return request.build_absolute_uri(field.url)
            return field.url

        # Licenses (from licenses app)
        from licenses.models import UserLicense
        licenses_qs = UserLicense.objects.filter(user=user)
        licenses_data = [
            {
                'id': lic.id,
                'document_name': lic.document_name,
                'document_number': lic.document_number,
                'country_of_issue': lic.country_of_issue,
                'issue_date': str(lic.issue_date) if lic.issue_date else None,
                'expiration_date': str(lic.expiration_date) if lic.expiration_date else None,
                'file_url': file_url(lic.document_file, download_path=build_download_url('license', lic.id)) if lic.document_file else None,
                'download_url': build_download_url('license', lic.id) if lic.document_file else None,
            }
            for lic in licenses_qs
        ]

        # Sea Services
        sea_services_qs = user.sea_services.all()
        from api.models import Rank
        from core.models import VesselType, Flag
        ranks_dict = {str(r.id): r.name for r in Rank.objects.all()}
        vessels_dict = {str(v.id): v.name for v in VesselType.objects.all()}
        flags_dict = {str(f.id): f.name for f in Flag.objects.all()}

        sea_services_data = [
            {
                'id': ss.id,
                'vessel_name': ss.vessel_name,
                'rank': ranks_dict.get(str(ss.rank), ss.rank) if ss.rank else '',
                'vessel_type': vessels_dict.get(str(ss.vessel_type), ss.vessel_type) if getattr(ss, 'vessel_type', None) else '',
                'flag': flags_dict.get(str(ss.flag), ss.flag) if getattr(ss, 'flag', None) else '',
                'signed_on': str(ss.signed_on) if ss.signed_on else None,
                'signed_off': str(ss.signed_off) if ss.signed_off else None,
                'file_url': file_url(ss.file, download_path=build_download_url('sea_service', ss.id)) if ss.file else None,
                'download_url': build_download_url('sea_service', ss.id) if ss.file else None,
            }
            for ss in sea_services_qs
        ]

        # Marine Courses — same field shape as seafarer_application
        # `8_marine_courses` (api/seafarer_application_serializers.py)
        # so the frontend doesn't have to merge two different
        # representations of the same Course rows. We expose BOTH
        # `course_number` (the model field name) and `number` (the
        # legacy key the seafarer-application path uses, and the
        # frontend CVSubmissionViewModal reads).
        from courses.models import Course
        courses_qs = Course.objects.filter(user=user).order_by('-id')
        courses_data = [
            {
                'id': c.id,
                'course_name': c.course_name,
                # canonical model field
                'course_number': c.course_number,
                # legacy alias used by the seafarer-application path
                'number': c.course_number,
                'issue_date': str(c.issue_date) if c.issue_date else None,
                'expiry_date': str(c.expiry_date) if c.expiry_date else None,
                'issued_by': c.issued_by,
                'issued_at': c.issued_at,
                'country_of_issue': c.country_of_issue,
                'file_url': file_url(c.document, download_path=build_download_url('course', c.id)) if c.document else None,
                'download_url': build_download_url('course', c.id) if c.document else None,
            }
            for c in courses_qs
        ]

        # Medical / Vaccinations
        from vaccinations.models import Vaccination
        vaccinations_qs = Vaccination.objects.filter(user=user)
        vaccinations_data = [
            {
                'id': v.id,
                'vaccine_name': v.name,
                'issue_date': str(v.issue_date) if v.issue_date else None,
                'expiry_date': str(v.expiry_date) if v.expiry_date else None,
                'first_dose_date': str(v.first_date) if v.first_date else None,
                'second_dose_date': str(v.last_date) if v.last_date else None,
                'remarks': v.remarks,
                'file_url': file_url(v.document, download_path=build_download_url('vaccination', v.id)) if v.document else None,
                'download_url': build_download_url('vaccination', v.id) if v.document else None,
            }
            for v in vaccinations_qs
        ]

        # Personal Documents (Visas / other IDs)
        from api.models import PersonalDocument
        personal_docs_qs = PersonalDocument.objects.filter(user=user)
        personal_docs_data = [
            {
                'id': pd.id,
                'document_type': pd.document_type,
                'document_number': pd.document_number,
                'issuing_country': pd.issuing_country,
                'issue_date': str(pd.issue_date) if pd.issue_date else None,
                'expiry_date': str(pd.expiry_date) if pd.expiry_date else None,
                'file_url': file_url(pd.file, download_path=build_download_url('personal_document', pd.id)) if pd.file else None,
                'download_url': build_download_url('personal_document', pd.id) if pd.file else None,
            }
            for pd in personal_docs_qs
        ]

        # Find specific records for singleton attachments
        coc_lic = licenses_qs.filter(document_name__icontains='coc').first()
        goc_lic = licenses_qs.filter(document_name__icontains='goc').first()
        med_cert = vaccinations_qs.filter(name="Medical Certificate For Seafarers").first()
        passport_doc = personal_docs_qs.filter(document_type__iexact='Passport').first()
        seaman_book_doc = personal_docs_qs.filter(document_type__iexact="Seaman's Book").first()
        other_seaman_book_doc = personal_docs_qs.filter(document_type__icontains="Seaman's Book").exclude(id=getattr(seaman_book_doc, 'id', None)).first()

        passport_file = user.passport_attachment if user.passport_attachment else getattr(passport_doc, 'file', None)
        passport_download_url = build_download_url('passport') if user.passport_attachment else (build_download_url('personal_document', passport_doc.id) if passport_doc and passport_doc.file else None)

        seaman_book_file = user.seaman_book_attachment if user.seaman_book_attachment else getattr(seaman_book_doc, 'file', None)
        seaman_book_download_url = build_download_url('seaman_book') if user.seaman_book_attachment else (build_download_url('personal_document', seaman_book_doc.id) if seaman_book_doc and seaman_book_doc.file else None)

        other_seaman_book_file = user.other_seaman_book_attachment if user.other_seaman_book_attachment else getattr(other_seaman_book_doc, 'file', None)
        other_seaman_book_download_url = build_download_url('other_seaman_book') if user.other_seaman_book_attachment else (build_download_url('personal_document', other_seaman_book_doc.id) if other_seaman_book_doc and other_seaman_book_doc.file else None)

        return {
            'passport': {
                'passport_no': user.passport_no,
                'issue_date': str(user.passport_issue_date) if user.passport_issue_date else None,
                'expiry_date': str(user.passport_expiry_date) if user.passport_expiry_date else None,
                'issued_by': user.passport_issued_by,
                'place_of_issue': user.passport_place_of_issue,
                'file_url': file_url(passport_file, download_path=passport_download_url) if passport_file else None,
                'download_url': passport_download_url,
            },
            'seaman_book': {
                'seaman_book_no': user.seaman_book_no,
                'issue_date': str(user.seaman_book_issue_date) if user.seaman_book_issue_date else None,
                'expiry_date': str(user.seaman_book_expiry_date) if user.seaman_book_expiry_date else None,
                'issued_by': user.seaman_book_issued_by,
                'place_of_issue': user.seaman_book_place_of_issue,
                'file_url': file_url(seaman_book_file, download_path=seaman_book_download_url) if seaman_book_file else None,
                'download_url': seaman_book_download_url,
            },
            'other_seaman_book': {
                'seaman_book_no': user.other_seaman_book_no,
                'issue_date': str(user.other_seaman_book_issue_date) if user.other_seaman_book_issue_date else None,
                'expiry_date': str(user.other_seaman_book_expiry_date) if user.other_seaman_book_expiry_date else None,
                'issued_by': user.other_seaman_book_issued_by,
                'place_of_issue': user.other_seaman_book_place_of_issue,
                'file_url': file_url(other_seaman_book_file, download_path=other_seaman_book_download_url) if other_seaman_book_file else None,
                'download_url': other_seaman_book_download_url,
            },
            'coc': {
                'certificate_name': user.coc_certificate_name,
                'certificate_number': user.coc_certificate_number,
                'issue_date': str(user.coc_issue_date) if user.coc_issue_date else None,
                'expiry_date': str(user.coc_expiry_date) if user.coc_expiry_date else None,
                'issued_by': user.coc_issued_by,
                'issued_at': user.coc_issued_at,
                'file_url': file_url(coc_lic.document_file, download_path=build_download_url('coc')) if coc_lic and coc_lic.document_file else None,
                'download_url': build_download_url('coc') if coc_lic and coc_lic.document_file else None,
            },
            'goc': {
                'certificate_number': user.goc_certificate_number,
                'issue_date': str(user.goc_issue_date) if user.goc_issue_date else None,
                'expiry_date': str(user.goc_expiry_date) if user.goc_expiry_date else None,
                'issued_by': user.goc_issued_by,
                'issued_at': user.goc_issued_at,
                'file_url': file_url(goc_lic.document_file, download_path=build_download_url('goc')) if goc_lic and goc_lic.document_file else None,
                'download_url': build_download_url('goc') if goc_lic and goc_lic.document_file else None,
            },
            'health_certificate': {
                'flag_state': user.health_flag_state,
                'number': user.health_number,
                'issue_date': str(user.health_issue_date) if user.health_issue_date else None,
                'expiry_date': str(user.health_expiry_date) if user.health_expiry_date else None,
                'issued_by': user.health_issued_by,
                'issued_at': user.health_issued_at,
                'international_medical_number': user.international_medical_number,
                'international_medical_issue_date': str(user.international_medical_issue_date) if user.international_medical_issue_date else None,
                'international_medical_expiry_date': str(user.international_medical_expiry_date) if user.international_medical_expiry_date else None,
                'file_url': file_url(med_cert.document, download_path=build_download_url('health_certificate')) if med_cert and med_cert.document else None,
                'download_url': build_download_url('health_certificate') if med_cert and med_cert.document else None,
                'records': vaccinations_data,
            },
            'licenses': licenses_data,
            'sea_service': sea_services_data,
            'marine_courses': courses_data,
            'personal_documents': personal_docs_data,
        }

    def get_seafarer_application(self, obj):
        """Return the full nested seafarer profile for the user."""
        from .seafarer_application_serializers import SeafarerApplicationSerializer
        return SeafarerApplicationSerializer(obj, context={'exclude_headers': True}).data

    def get_coded_rank(self, obj):
        """
        Returns all assigned rank codes for the user.
        Each entry contains: assigned_code, rank_code, rank_name.
        """
        user_ranks = obj.user_ranks.select_related('rank').order_by('-id')[:1]
        return [
            {
                'assigned_code': ur.assigned_code,
                'rank_code': ur.rank.code,
                'rank_name': ur.rank.name,
            }
            for ur in user_ranks
        ]

class LanguageProficiencySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageProficiency
        # We exclude 'user' because we will inject the logged-in user automatically in the view
        fields = [
            'id', 'language', 'general_marks', 'speaking_level', 
            'writing_level', 'reading_level', 'cefr_level', 'cefr_description',
            'attachment'
        ]

    def validate(self, attrs):
        lang = attrs.get('language')
        marks = attrs.get('general_marks')
        cefr = attrs.get('cefr_level')
        speaking = attrs.get('speaking_level')
        
        # The frontend automatically sends this exact test record upon creation 
        if lang == 'French' and marks == 90 and cefr == 'B2' and speaking == 'Advanced':
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Please provide your actual language proficiency details instead of the default test data.")
            
        return attrs

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            'email', 'password', 'first_name', 'middle_name', 'role',
            'profile_image', 'date_of_birth', 'age', 'nationality',
            'Place_Of_Birth', 'Nearest_Port', 'marital_status',
            'blood_type', 'smoker', 'Height_Cm', 'Weight_Kg',
            'college_or_school', 'address', 'phone_number', 'tel_number',
            'country', 'city', 'salary',
            'us_visa_status', 'schengen_visa_status',
            'marlins_test_result', 'marlins_test_issued_date',
            'marlins_test_issued_by', 'marlins_test_issued_at',
            # Position Information
            'application_for_position', 'other_position', 'available_date',
            'register_code', 'register_date',
            # Travel Documents
            'passport_no', 'passport_issue_date', 'passport_expiry_date',
            'passport_issued_by', 'passport_place_of_issue',
            'seaman_book_no', 'seaman_book_issue_date', 'seaman_book_expiry_date',
            'seaman_book_issued_by', 'seaman_book_place_of_issue',
        )

        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        Users.objects.all(),
                        message="This email is already registered."
                    )
                ]
            }
        }

    def to_internal_value(self, data):
        if 'first_name' in data:
            full_name = str(data.get('first_name') or '').strip()
            if ' ' in full_name:
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                parts = full_name.split(' ', 1)
                data['first_name'] = parts[0]
                data['middle_name'] = parts[1] if len(parts) > 1 else ''

        # Pre-process 'application_for_position' if it's a list or an ID
        if 'application_for_position' in data:
            val = data.get('application_for_position')
            # Handle list input
            if isinstance(val, list):
                val = val[0] if len(val) > 0 else None
            
            if val:
                from api.models import Rank
                rank_obj = None
                # Handle ID input (integer or numeric string)
                if isinstance(val, int) or (isinstance(val, str) and str(val).isdigit()):
                    rank_obj = Rank.objects.filter(id=int(val)).first()
                # Handle string name input
                elif isinstance(val, str):
                    rank_obj = Rank.objects.filter(name__iexact=val).first()
                
                if rank_obj:
                    if hasattr(data, 'copy'):
                        data = data.copy()
                    else:
                        data = dict(data)
                    data['application_for_position'] = rank_obj.name
                else:
                    # Fallback to the string value if no rank found
                    if hasattr(data, 'copy'):
                        data = data.copy()
                    else:
                        data = dict(data)
                    data['application_for_position'] = str(val)

        return super().to_internal_value(data)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DocumentSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    file = serializers.FileField(required=False, allow_null=True)
    generated_id = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    job_position_details = serializers.SerializerMethodField()
    job_position_name = serializers.CharField(source='job_position.rank.name', read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'user', 'title', 'file', 'created_at', 'updated_at', 'name', 'email', 'phone_number', 'position', 'position_id', 'status', 'generated_id', 'company', 'company_name', 'job_position', 'job_position_name', 'job_position_details']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        pos_value = instance.position
        pos_id = instance.position_id
        
        # Keep 'position' as a string for the UI to prevent React rendering errors
        # Provide 'position_id' as a separate field for logic/IDs
        if pos_value or pos_id:
            from api.models import Rank
            # Sync name/ID if one is missing
            rank = Rank.objects.filter(name__iexact=pos_value).first() if pos_value else None
            
            representation['position'] = pos_value or (rank.name if rank else None)
            representation['position_id'] = pos_id or (rank.id if rank else None)
        
        return representation
    
    def to_internal_value(self, data):
        # Make data mutable for field aliasing below.
        # Avoid QueryDict.copy() which deep-copies and crashes on file uploads
        # (BufferedRandom objects cannot be pickled).
        if hasattr(data, 'lists'):
            new_data = {}
            for key in data:
                values = data.getlist(key)
                new_data[key] = values if len(values) > 1 else values[0]
            data = new_data
        elif hasattr(data, 'copy'):
            data = data.copy()
        else:
            data = dict(data)

        if 'rank_ids' in data and 'position' not in data:
            data['position'] = data['rank_ids']
        
        if 'first_name' in data and 'name' not in data:
            data['name'] = data['first_name']

        if 'phone' in data and 'phone_number' not in data:
            data['phone_number'] = data['phone']

        # Pre-process 'position' if it's a list or an ID
        if 'position' in data:
            pos_val = data.get('position')
            from api.models import Rank
            rank_obj = None

            # Handle list input (try each item until a valid Rank is found)
            if isinstance(pos_val, list):
                for item in pos_val:
                    if isinstance(item, int) or (isinstance(item, str) and str(item).isdigit()):
                        data['position_id'] = int(item)
                        rank_obj = Rank.objects.filter(id=int(item)).first()
                    elif isinstance(item, str):
                        rank_obj = Rank.objects.filter(name__iexact=item).first()
                    if rank_obj:
                        break
                
                if rank_obj:
                    data['position'] = rank_obj.name
                    data['position_id'] = rank_obj.id
                elif len(pos_val) > 0:
                    # Fallback: find the first string that isn't just a number (the label)
                    label = None
                    for item in pos_val:
                        if isinstance(item, str) and not str(item).isdigit():
                            label = item
                            break
                    data['position'] = label if label else str(pos_val[0])
            
            else:
                # Handle single ID or Name input
                if isinstance(pos_val, int) or (isinstance(pos_val, str) and str(pos_val).isdigit()):
                    data['position_id'] = int(pos_val)
                    rank_obj = Rank.objects.filter(id=int(pos_val)).first()
                elif isinstance(pos_val, str):
                    rank_obj = Rank.objects.filter(name__iexact=pos_val).first()
                
                if rank_obj:
                    data['position'] = rank_obj.name
                    data['position_id'] = rank_obj.id
                else:
                    data['position'] = str(pos_val)

        # Auto-fill company and position if job_position is provided
        if 'job_position' in data and data['job_position']:
            try:
                # Handle both integer IDs and potential string inputs
                jp_id = data.get('job_position')
                if isinstance(jp_id, str) and not jp_id.isdigit():
                    # If it's a string name, try to find a matching rank position
                    from companies.models import JobOrderPosition
                    job_pos = JobOrderPosition.objects.filter(rank__name__iexact=jp_id).first()
                else:
                    from companies.models import JobOrderPosition
                    job_pos = JobOrderPosition.objects.get(id=jp_id)

                if job_pos:
                    if hasattr(data, 'copy'):
                        data = data.copy()
                    else:
                        data = dict(data)
                    
                    if 'company' not in data and job_pos.job_order and job_pos.job_order.company:
                        data['company'] = job_pos.job_order.company.id
                    if 'position' not in data and job_pos.rank:
                        data['position'] = job_pos.rank.name
                    if not data.get('title'):
                        company_name = job_pos.job_order.company.company_name if job_pos.job_order and job_pos.job_order.company else "Unknown Company"
                        rank_name = job_pos.rank.name if job_pos.rank else "Unknown Position"
                        data['title'] = f"Application for {rank_name} at {company_name}"
            except (JobOrderPosition.DoesNotExist, ValueError, TypeError):
                pass

        return super().to_internal_value(data)

    def validate(self, attrs):
        # If title is not provided, use the filename
        if not attrs.get('title') and attrs.get('file'):
            attrs['title'] = attrs['file'].name
            
        request = self.context.get('request')
        
        # 1. Security for Authenticated Employees: Enforce their own registered name and email
        if request and request.user and request.user.is_authenticated and request.user.role == 'Employee':
            registered_full_name = f"{request.user.first_name or ''} {request.user.middle_name or ''}".strip()
            registered_email = (request.user.email or '').strip().lower()
            
            # Reject if the submitted email does not match the registered email
            submitted_email = attrs.get('email', '').strip().lower()
            if submitted_email and submitted_email != registered_email:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'email': f"You must use your registered email address ({request.user.email}). Quick Apply only accepts the email you registered with."
                })
            
            # Reject if the submitted name does not match the registered name
            submitted_name = attrs.get('name', '').strip().lower()
            if submitted_name and submitted_name != registered_full_name.lower():
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'name': f"You must use your registered name ({registered_full_name}). Quick Apply only accepts the name you registered with."
                })
            
            # Always enforce the registered profile data
            attrs['name'] = registered_full_name
            attrs['email'] = request.user.email
                
        # 2. Security for Unauthenticated Users (Quick Apply): Reject if email belongs to a registered user
        # Skip this check for authenticated admins/HR/recruiters doing updates
        elif not request or not request.user or not request.user.is_authenticated:
            email = attrs.get('email')
            
            if email:
                from api.models import Users
                existing_user = Users.objects.filter(email__iexact=email).first()
                if existing_user:
                    # If the email is already registered, the user must log in first
                    # They cannot submit a Quick Apply as a guest with a registered email
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({
                        'email': f"The email '{email}' is already registered. Please log in first and then submit your application using your registered account."
                    })
        return attrs

    def get_generated_id(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        
        # Check Role of the viewer
        has_permission = request.user.is_authenticated and getattr(request.user, 'role', '') in ['Admin', 'HR Manager', 'Recruiter', 'admin'] or getattr(request.user, 'is_superuser', False)
        if not request.user.is_authenticated or not has_permission:
            return None
            
        # Check Status of the document
        if obj.status == 'Active':
            return obj.user.generated_id
            
        return None

    def get_job_position_details(self, obj):
        if not obj.job_position:
            return None
        pos = obj.job_position
        return {
            'id': pos.id,
            'job_position_name': pos.rank.name if pos.rank else None,
            'quantity': pos.quantity,
            'salary_min': str(pos.salary_min) if pos.salary_min else None,
            'salary_max': str(pos.salary_max) if pos.salary_max else None,
            'currency': pos.currency,
            'contract_duration_months': pos.contract_duration_months,
            'remarks': pos.remarks
        }


class UserLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLanguage
        fields = [
            'id', 'user', 'language', 'general_remarks',
            'speaking_level', 'writing_level', 'reading_level',
            'cefr_level', 'cefr_description', 'attachment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_language(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Language field cannot be empty.")
        return value


class PersonalDocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = PersonalDocument
        fields = [
            'id', 'user', 'document_type', 'document_number',
            'issue_date', 'expiry_date', 'issuing_country', 'issued_by',
            'place_of_issue', 'file', 'download_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'download_url']
        extra_kwargs = {'user': {'required': False}}

    def get_download_url(self, obj):
        if getattr(obj, 'file', None) and getattr(obj, 'user', None):
            path = f"/api/users/{obj.user.id}/download-personal-document/{obj.id}/"
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.file and instance.user:
            ret['file'] = self.get_download_url(instance)
        return ret


from .models import NextOfKin

class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = [
            'id', 'user', 'full_name', 'relationship',
            'address_country', 'phone', 'phone2', 'email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'required': False}
        }


# =====================
# DECLARATION SERIALIZERS
# =====================
from .models import Declaration

class DeclarationSerializer(serializers.ModelSerializer):
    """
    Serializer for Declaration model.
    Includes user information for display purposes.
    """
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Declaration
        fields = [
            'id',
            'user',
            'user_name',
            'user_email',
            # Question 1: Disease
            'has_disease',
            'disease_details',
            # Question 2: Accident
            'has_accident',
            'accident_details',
            # Question 3: Psychiatric Treatment
            'has_psychiatric_treatment',
            'psychiatric_treatment_details',
            # Question 4: Addiction
            'has_addiction',
            'addiction_details',
            # Consent and Signature
            'consent_given',
            'declaration_place',
            'declaration_date',
            'signature',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'required': False}  # Will be set automatically for employees
        }
    
    def get_user_email(self, obj):
        """Return user email safely"""
        return obj.user.email if obj.user else ""
    
    def get_user_name(self, obj):
        """Return full name of the user"""
        if not obj.user:
            return ""
        first = obj.user.first_name or ""
        middle = obj.user.middle_name or ""
        last = getattr(obj.user, 'last_name', '') or ""
        return f"{first} {middle} {last}".strip()