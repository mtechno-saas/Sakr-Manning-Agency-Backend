from rest_framework import serializers, validators
from .models import (
    Users, UserRank, Certificate, Rank, Contract, Reference, SeaService,
    Interview, CVSubmission, Document, UserLanguage, PersonalDocument
)
from companies.models import Company
from finance.models import FinanceRecord
from tickets_papers.models import Ticket, TravelingPaper
from ships.serializers import ShipSerializer
from .models import LanguageProficiency

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
    class Meta:
        model = SeaService
        fields = '__all__'

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
    class Meta:
        model = Users
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "profile_image",
            "role",
        ]


# =====================
# COMPANY SERIALIZERS
# =====================

class CompanyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Company
        fields = ['id', 'name', 'company_type', 'email', 'open_positions', 'status']


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
    company_name = serializers.CharField(source='company.name', read_only=True)
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


class InterviewCalendarSerializer(serializers.ModelSerializer):
    """Lightweight serializer for calendar view"""
    candidate_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)

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
    company_name = serializers.CharField(source='company.name', read_only=True)
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
    """Lightweight serializer for list views"""
    user_name = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = CVSubmission
        fields = [
            'id', 'user', 'user_name', 'position_name', 'company_name',
            'experience_years', 'status', 'submitted_date'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()


class CVSubmissionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.first_name', read_only=True)

    class Meta:
        model = CVSubmission
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'company', 'company_name', 'position', 'position_name',
            'cv_file', 'cover_letter', 'experience_years',
            'expected_salary', 'availability_date',
            'status', 'submitted_date',
            'reviewed_by', 'reviewed_by_name', 'reviewed_date',
            'notes', 'rating', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {'required': False}
        }

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()


# =====================
# CONTRACT SERIALIZERS
# =====================

class ContractListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    user_name = serializers.SerializerMethodField()
    ship_name = serializers.CharField(source='ship.ship_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
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
    ship_name = serializers.CharField(source='ship.ship_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    rank_name = serializers.CharField(source='rank.name', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id',
            'user', 'user_name', 'user_email',
            'ship', 'ship_name',
            'company', 'company_name',
            'rank', 'rank_name',
            'sign_on_date', 'sign_off_date', 'salary', 'currency', 'status',
            'signed_file', 'signed_at',
            'created_at', 'updated_at'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.middle_name}".strip()


# =====================
# USER SERIALIZERS
# =====================

class UsersSerializer(serializers.ModelSerializer):
    # Read-only nested serializers for detailed representation
    ranks = UserRankSerializer(source='user_ranks', many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    sea_services = SeaServiceSerializer(many=True, read_only=True)

    # Write-only fields for accepting lists of IDs during create/update
    rank_ids = serializers.PrimaryKeyRelatedField(
        queryset=Rank.objects.all(),
        many=True,
        write_only=True,
        source='codes',
        required=False,
        help_text="List of Rank IDs to assign."
    )
    certificate_ids = serializers.PrimaryKeyRelatedField(
        queryset=Certificate.objects.all(),
        many=True,
        write_only=True,
        source='certificates',
        required=False,
        help_text="List of Certificate IDs to assign."
    )

    # Password field for user creation (write-only)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Users
        fields = [
            'id', 'email', 'first_name', 'middle_name', 'password','country', 'city',
            'profile_image', 'age', 'blood_type', 'smoker', 'us_visa_status',
            'schengen_visa_status', 'date_of_birth', 'marital_status', 'user_status',
            'nationality', 'Place_Of_Birth', 'Nearest_Port', 'Height_Cm', 'Weight_Kg',
            'college_or_school', 'marlins_test_issued_date', 'marlins_test_result',
            'marlins_test_issued_by', 'marlins_test_issued_at', 'marlins_test_attachment',
            'ces_test_result', 'ces_test_issued_date', 'ces_test_issued_at', 'ces_test_issued_by',
            'ces_test_attachment', 'salary', 'address',
            'phone_number', 'tel_number', 'created_at', 'updated_at', 'role', "register_code",
            'register_date',
            'last_updated_date',
            'application_for_position', 'other_position', 'available_date',
            # Travel Documents
            'passport_no', 'passport_issue_date', 'passport_expiry_date',
            'passport_issued_by', 'passport_place_of_issue',
            'seaman_book_no', 'seaman_book_issue_date', 'seaman_book_expiry_date',
            'seaman_book_issued_by', 'seaman_book_place_of_issue',
            'other_seaman_book_no', 'other_seaman_book_issue_date', 'other_seaman_book_expiry_date',
            'other_seaman_book_issued_by', 'other_seaman_book_place_of_issue',
            # Professional Qualifications
            'coc_certificate_name', 'coc_certificate_number', 'coc_issue_date',
            'coc_expiry_date', 'coc_issued_by', 'coc_issued_at',
            'goc_certificate_number', 'goc_issue_date', 'goc_expiry_date',
            'goc_issued_by', 'goc_issued_at',
            # Next of Kin
            'next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_address_country',
            'next_of_kin_phone', 'next_of_kin_phone2', 'next_of_kin_email',
            # Health Certificates
            'health_flag_state', 'health_number', 'health_issue_date', 'health_expiry_date',
            'health_issued_by', 'health_issued_at', 'international_medical_number',
            'international_medical_issue_date', 'international_medical_expiry_date',
            'yellow_fever_number', 'yellow_fever_issue_date', 'yellow_fever_expiry_date',
            'cholera_number', 'cholera_issue_date', 'cholera_expiry_date',
            'covid_vaccine_name', 'covid_first_dose', 'covid_second_dose',
            'covid_other_doses_or_remarks',
            # New fields from Word document
            'overall_size', 'shirt_size', 'trouser_size', 'shoes_size',
            'english_language_level', 'other_language', 'other_language_level',
            'disease_history', 'accident_history', 'psychiatric_treatment_history', 'addiction_history',
            'declaration_consent', 'declaration_date', 'declaration_place',
            'initial_assessment_comments', 'responsible_person_name', 'assessment_date',
            # Relationships
            'ranks', 'certificates', 'rank_ids', 'certificate_ids', 'references', 'sea_services',
            'generated_id'
        ]
        extra_kwargs = {
            'profile_image': {'required': False},
            'password': {'write_only': True, 'required': False},
            'generated_id': {'read_only': True}
        }

    def to_representation(self, instance):
        """Override to ensure proper serialization of nested fields"""
        representation = super().to_representation(instance)

        # Hide generated_id for non-privileged users
        request = self.context.get('request')
        if request and hasattr(request.user, 'role') and request.user.role not in ['Admin', 'HR Manager', 'Recruiter']:
            representation.pop('generated_id', None)

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
        for rank in codes_data:
            UserRank.objects.create(user=user, rank=rank)
        if certificates_data:
            user.certificates.set(certificates_data)

        return user

    def update(self, instance, validated_data):
        # Pop relationship and file data
        codes_data = validated_data.pop('codes', None)
        certificates_data = validated_data.pop('certificates', None)
        profile_image_data = validated_data.pop('profile_image', None)

        # Update standard fields using the default DRF update method
        instance = super().update(instance, validated_data)

        # Handle the profile image update separately if a new image was provided
        if profile_image_data is not None:
            instance.profile_image = profile_image_data
            instance.save()

        # Handle relationship updates
        if codes_data is not None:
            instance.user_ranks.all().delete()
            for rank in codes_data:
                UserRank.objects.create(user=instance, rank=rank)
        if certificates_data is not None:
            instance.certificates.set(certificates_data)

        return instance
class LanguageProficiencySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageProficiency
        # We exclude 'user' because we will inject the logged-in user automatically in the view
        fields = [
            'id', 'language', 'general_marks', 'speaking_level', 
            'writing_level', 'reading_level', 'cefr_level', 'cefr_description',
            'attachment'
        ]

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

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DocumentSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    generated_id = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'user', 'title', 'file', 'created_at', 'updated_at', 'name', 'email', 'phone_number', 'position', 'status', 'generated_id']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        # If title is not provided, use the filename
        if not attrs.get('title') and attrs.get('file'):
            attrs['title'] = attrs['file'].name
        return attrs

    def get_generated_id(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        
        # Check Role of the viewer
        if not request.user.is_authenticated or request.user.role not in ['Admin', 'HR Manager', 'Recruiter']:
            return None
            
        # Check Status of the document
        if obj.status == 'Active':
            return obj.user.generated_id
            
        return None


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


class PersonalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDocument
        fields = [
            'id', 'user', 'document_type', 'document_number',
            'issue_date', 'expiry_date', 'issuing_country', 'issued_by',
            'place_of_issue', 'file',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'user': {'required': False}}



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