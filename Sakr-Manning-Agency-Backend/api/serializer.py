# from rest_framework import serializers
# from .models import Users, UserRank, Certificate, Rank, Contract, Reference, SeaService
# from tickets_papers.models import Ticket, TravelingPaper
# from django.contrib.auth.models import User
# from rest_framework import serializers, validators
# from ships.serializers import ShipSerializer


# class TicketSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ticket
#         fields = ["id", "ticket_number"]


# class TravelingPaperSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TravelingPaper
#         fields = ["id", "title"]


# class RankSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rank
#         fields = ["id", "code", "name"]


# class CertificateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Certificate
#         fields = ["id", "code", "name"]


# class UserRankSerializer(serializers.ModelSerializer):
#     """Serializer for UserRank - includes the assigned_code"""
#     rank = RankSerializer(read_only=True)
#     rank_code = serializers.CharField(source='rank.code', read_only=True)
#     rank_name = serializers.CharField(source='rank.name', read_only=True)

#     class Meta:
#         model = UserRank
#         fields = ["id", "assigned_code", "rank_code", "rank_name", "rank"]


# class ReferenceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Reference
#         fields = '__all__'


# class SeaServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SeaService
#         fields = '__all__'

# class UserMeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Users
#         fields = [
#             "id",
#             "email",
#             "first_name",
#             "middle_name",
#             "profile_image",
#             # Any extra non-sensitive fields you want
#         ]

# class UsersSerializer(serializers.ModelSerializer):
#     # Read-only nested serializers for detailed representation
#     ranks = UserRankSerializer(source='user_ranks', many=True, read_only=True)
#     certificates = CertificateSerializer(many=True, read_only=True)
#     references = ReferenceSerializer(many=True, read_only=True)
#     sea_services = SeaServiceSerializer(many=True, read_only=True)

#     # Write-only fields for accepting lists of IDs during create/update
#     rank_ids = serializers.PrimaryKeyRelatedField(
#         queryset=Rank.objects.all(),
#         many=True,
#         write_only=True,
#         source='codes',
#         required=False,
#         help_text="List of Rank IDs to assign."
#     )
#     certificate_ids = serializers.PrimaryKeyRelatedField(
#         queryset=Certificate.objects.all(),
#         many=True,
#         write_only=True,
#         source='certificates',
#         required=False,
#         help_text="List of Certificate IDs to assign."
#     )

#     # Password field for user creation (write-only)
#     password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

#     class Meta:
#         model = Users
#         fields = [
#             'id', 'email', 'first_name', 'middle_name', 'password',
#             'profile_image', 'age', 'blood_type', 'smoker', 'us_visa_status', 
#             'schengen_visa_status', 'date_of_birth', 'marital_status', 'user_status',
#             'nationality', 'Place_Of_Birth', 'Nearest_Port', 'Height_Cm', 'Weight_Kg',
#             'college_or_school', 'marlins_test_issued_date', 'marlins_test_result',
#             'marlins_test_issued_by', 'marlins_test_issued_at', 'salary', 'address',
#             'phone_number', 'tel_number', 'created_at', 'updated_at', 'role',
#             # Travel Documents
#             'passport_no', 'passport_issue_date', 'passport_expiry_date',
#             'passport_issued_by', 'passport_place_of_issue',
#             'seaman_book_no', 'seaman_book_issue_date', 'seaman_book_expiry_date',
#             'seaman_book_issued_by', 'seaman_book_place_of_issue',
#             'other_seaman_book_no', 'other_seaman_book_issue_date', 'other_seaman_book_expiry_date',
#             'other_seaman_book_issued_by', 'other_seaman_book_place_of_issue',
#             # Professional Qualifications
#             'coc_certificate_name', 'coc_certificate_number', 'coc_issue_date',
#             'coc_expiry_date', 'coc_issued_by', 'coc_issued_at',
#             'goc_certificate_number', 'goc_issue_date', 'goc_expiry_date',
#             'goc_issued_by', 'goc_issued_at',
#             # Next of Kin
#             'next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_address_country',
#             'next_of_kin_phone', 'next_of_kin_email',
#             # Health Certificates
#             'health_flag_state', 'health_number', 'health_issue_date', 'health_expiry_date',
#             'health_issued_by', 'health_issued_at', 'international_medical_number',
#             'international_medical_issue_date', 'international_medical_expiry_date',
#             'yellow_fever_number', 'yellow_fever_issue_date', 'yellow_fever_expiry_date',
#             'cholera_number', 'cholera_issue_date', 'cholera_expiry_date',
#             'covid_vaccine_name', 'covid_first_dose', 'covid_second_dose',
#             'covid_other_doses_or_remarks',
#             # New fields from Word document
#             'overall_size', 'shirt_size', 'trouser_size', 'shoes_size',
#             'english_language_level', 'other_language', 'other_language_level',
#             'disease_history', 'accident_history', 'psychiatric_treatment_history', 'addiction_history',
#             'declaration_consent', 'declaration_date', 'declaration_place',
#             'initial_assessment_comments', 'responsible_person_name', 'assessment_date',
#             # Relationships
#             'ranks', 'certificates', 'rank_ids', 'certificate_ids', 'references', 'sea_services'
#         ]
#         extra_kwargs = {
#             'profile_image': {'required': False},
#             'password': {'write_only': True, 'required': False}
#         }

#     def to_representation(self, instance):
#         """Override to ensure proper serialization of nested fields"""
#         representation = super().to_representation(instance)
        
#         # Explicitly serialize ranks with assigned_code
#         representation['ranks'] = UserRankSerializer(
#             instance.user_ranks.all(), 
#             many=True
#         ).data
        
#         # Serialize certificates
#         representation['certificates'] = CertificateSerializer(
#             instance.certificates.all(), 
#             many=True
#         ).data
        
#         # Serialize references
#         representation['references'] = ReferenceSerializer(
#             instance.references.all(), 
#             many=True
#         ).data
        
#         # Serialize sea services
#         representation['sea_services'] = SeaServiceSerializer(
#             instance.sea_services.all(), 
#             many=True
#         ).data
        
#         # Remove the codes field from output (internal use only)
#         representation.pop('codes', None)
        
#         return representation

#     def create(self, validated_data):
#         # Pop the relationship data first
#         codes_data = validated_data.pop('codes', [])
#         certificates_data = validated_data.pop('certificates', [])
#         profile_image_data = validated_data.pop('profile_image', None)
#         password = validated_data.pop('password', None)

#         # Create the user instance with the remaining standard fields
#         user = Users(**validated_data)
        
#         # Set password properly (if provided)
#         if password:
#             user.set_password(password)
        
#         # Save the user
#         user.save()

#         # Handle the profile image if it was provided
#         if profile_image_data:
#             user.profile_image = profile_image_data
#             user.save()

#         # Handle the M2M relationships
#         for rank in codes_data:
#             UserRank.objects.create(user=user, rank=rank)
#         if certificates_data:
#             user.certificates.set(certificates_data)

#         return user

#     def update(self, instance, validated_data):
#         # Pop relationship and file data
#         codes_data = validated_data.pop('codes', None)
#         certificates_data = validated_data.pop('certificates', None)
#         profile_image_data = validated_data.pop('profile_image', None)

#         # Update standard fields using the default DRF update method
#         instance = super().update(instance, validated_data)

#         # Handle the profile image update separately if a new image was provided
#         if profile_image_data is not None:
#             instance.profile_image = profile_image_data
#             instance.save()

#         # Handle relationship updates
#         if codes_data is not None:
#             instance.user_ranks.all().delete()
#             for rank in codes_data:
#                 UserRank.objects.create(user=instance, rank=rank)
#         if certificates_data is not None:
#             instance.certificates.set(certificates_data)

#         return instance


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Users
#         fields = ('email', 'password', 'first_name')

#         extra_kwargs = {
#             "password": {"write_only": True},
#             "email": {
#                 "required": True,
#                 "allow_blank": False,
#                 "validators": [
#                     validators.UniqueValidator(
#                         Users.objects.all(),
#                         message="This email is already registered."
#                     )
#                 ]
#             }
#         }

#     def create(self, validated_data):
#         user = Users.objects.create_user(
#             email=validated_data['email'],
#             password=validated_data['password'],
#             first_name=validated_data['first_name']
#         )
#         return user


# class ContractSerializer(serializers.ModelSerializer):
#     # Use nested serializers for readable output
#     user = serializers.StringRelatedField()
#     ship = serializers.StringRelatedField()
#     rank = serializers.StringRelatedField()

#     # Use IDs for writable input
#     user_id = serializers.IntegerField(write_only=True)
#     ship_id = serializers.IntegerField(write_only=True)
#     rank_id = serializers.IntegerField(write_only=True)

#     class Meta:
#         model = Contract
#         fields = [
#             'id',
#             'user', 'user_id',
#             'ship', 'ship_id',
#             'rank', 'rank_id',
#             'sign_on_date', 'sign_off_date', 'salary', 'status',
#             'created_at', 'updated_at'
#         ]



from rest_framework import serializers, validators
from .models import (
    Users, UserRank, Certificate, Rank, Contract, Reference, SeaService,
    Interview, CVSubmission, UserCertificate, Declaration
)
from companies.models import Company
from finance.models import FinanceRecord
from tickets_papers.models import Ticket, TravelingPaper
from ships.serializers import ShipSerializer


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
        extra_kwargs = {
            'user': {'required': False}
        }


class UserCertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for UserCertificate model.
    Includes nested certificate type information and calculated fields.
    """
    certificate_type_name = serializers.CharField(source='certificate_type.name', read_only=True, allow_null=True)
    certificate_type_code = serializers.CharField(source='certificate_type.code', read_only=True, allow_null=True)
    rank_name = serializers.CharField(source='rank.name', read_only=True, allow_null=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = UserCertificate
        fields = [
            'id',
            'user',
            'certificate_type',
            'certificate_type_name',
            'certificate_type_code',
            'document_name',
            'document_number',
            'country_of_issue',
            'issue_date',
            'expiry_date',
            'issued_by',
            'issued_at',
            'certificate_file',
            'category',
            'rank',
            'rank_name',
            'is_expired',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_expired']





class SeaServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeaService
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }


class UserMeSerializer(serializers.ModelSerializer):
    cv_status = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
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
        return f"{obj.candidate.first_name} {obj.candidate.last_name}".strip()


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
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


# =====================
# CV SUBMISSION SERIALIZERS
# =====================

class CVSubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    user_name = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    salary = serializers.CharField(source='user.salary', read_only=True, default=None)
    available_date = serializers.DateField(source='user.available_date', read_only=True, default=None)

    class Meta:
        model = CVSubmission
        fields = [
            'id', 'user', 'user_name', 'position_name', 'company_name',
            'experience_years', 'status', 'submitted_date', 'salary', 'available_date'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class CVSubmissionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.first_name', read_only=True)
    salary = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    available_date = serializers.DateField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CVSubmission
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'company', 'company_name', 'position', 'position_name',
            'cv_file', 'cover_letter', 'experience_years',
            'expected_salary', 'availability_date',
            'status', 'submitted_date',
            'reviewed_by', 'reviewed_by_name', 'reviewed_date',
            'notes', 'rating', 'created_at', 'updated_at',
            'salary', 'available_date'
        ]
        extra_kwargs = {
            'user': {'required': False}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['salary'] = instance.user.salary if instance.user else None
        ret['available_date'] = instance.user.available_date if instance.user else None
        return ret

    def create(self, validated_data):
        salary = validated_data.pop('salary', None)
        available_date = validated_data.pop('available_date', None)
        instance = super().create(validated_data)
        
        # Propagate to user
        user = instance.user
        if user:
            if salary is not None:
                user.salary = salary
            if available_date is not None:
                user.available_date = available_date
            user.save()
        return instance

    def update(self, instance, validated_data):
        salary = validated_data.pop('salary', None)
        available_date = validated_data.pop('available_date', None)
        instance = super().update(instance, validated_data)
        
        # Propagate to user
        user = instance.user
        if user:
            if salary is not None:
                user.salary = salary
            if available_date is not None:
                user.available_date = available_date
            user.save()
        return instance

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


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
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


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
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


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

    # Password field for user creation (write-only)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    
    # Write-only fields for nested creation of sea services and references
    sea_services_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of sea service records to create"
    )
    references_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of references to create"
    )

    class Meta:
        model = Users
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password',
            'profile_image', 'age', 'blood_type', 'smoker', 'us_visa_status',
            'schengen_visa_status', 'date_of_birth', 'marital_status', 'user_status',
            'nationality', 'Place_Of_Birth', 'Nearest_Port', 'Height_Cm', 'Weight_Kg',
            'college_or_school', 'marlins_test_issued_date', 'marlins_test_result',
            'marlins_test_issued_by', 'marlins_test_issued_at', 'salary', 'address',
            'phone_number', 'tel_number', 'created_at', 'updated_at', 'role',
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
            'next_of_kin_phone', 'next_of_kin_email',
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
            'sea_services_data', 'references_data'
        ]
        extra_kwargs = {
            'profile_image': {'required': False},
            'password': {'write_only': True, 'required': False}
        }

    def to_representation(self, instance):
        """Override to ensure proper serialization of nested fields"""
        representation = super().to_representation(instance)

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

        return representation

    def create(self, validated_data):
        # Pop the relationship data first
        codes_data = validated_data.pop('codes', [])
        certificates_data = validated_data.pop('certificates', [])
        sea_services_data = validated_data.pop('sea_services_data', [])
        references_data = validated_data.pop('references_data', [])
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

        # Create sea services
        for sea_service in sea_services_data:
            SeaService.objects.create(user=user, **sea_service)
        
        # Create references
        for reference in references_data:
            Reference.objects.create(user=user, **reference)

        return user

    def update(self, instance, validated_data):
        # Pop relationship and file data
        codes_data = validated_data.pop('codes', None)
        certificates_data = validated_data.pop('certificates', None)
        sea_services_data = validated_data.pop('sea_services_data', None)
        references_data = validated_data.pop('references_data', None)
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

        # Handle sea services update (replace all)
        if sea_services_data is not None:
            instance.sea_services.all().delete()
            for sea_service in sea_services_data:
                SeaService.objects.create(user=instance, **sea_service)
        
        # Handle references update (replace all)
        if references_data is not None:
            instance.references.all().delete()
            for reference in references_data:
                Reference.objects.create(user=instance, **reference)

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('email', 'password', 'first_name', 'last_name')

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
        user = Users.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', '')
        )
        return user


# =====================
# DECLARATION SERIALIZER
# =====================

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
        last = getattr(obj.user, 'last_name', '') or ""
        return f"{first} {last}".strip()