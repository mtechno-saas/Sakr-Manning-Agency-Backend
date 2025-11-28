



# from django.contrib import admin
# from django import forms
# from .models import Users, Rank, Certificate, UserRank, Contract, Reference, SeaService


# class UsersAdminForm(forms.ModelForm):
#     """Custom form that handles ManyToMany relationships and password hashing"""
#     password = forms.CharField(
#         widget=forms.PasswordInput(),
#         required=False,
#         help_text="Leave empty for default password"
#     )

#     class Meta:
#         model = Users
#         fields = '__all__'

#     def save(self, commit=True):
#         user = super().save(commit=False)

#         # Handle password
#         password = self.cleaned_data.get('password')
#         if password:
#             user.set_password(password)
#         elif not user.pk:  # New user without password
#             user.set_password('defaultpassword123')

#         if commit:
#             user.save()
#             self.save_m2m()

#         return user


# class UsersAdmin(admin.ModelAdmin):
#     form = UsersAdminForm

#     # Fields to display in the admin list view
#     list_display = ('email', 'first_name', 'is_staff', 'is_active', 'created_at')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'marital_status', 'nationality')
#     search_fields = ('email', 'first_name', 'middle_name')
#     ordering = ('email',)

#     # Make some fields read-only
#     readonly_fields = ('created_at', 'updated_at', 'last_login')

#     # ManyToMany widgets
#     filter_horizontal = ('certificates', 'codes')

#     # Organize fields in sections
#     fieldsets = (
#         ('Personal Info', {
#             'fields': ('first_name', 'middle_name', 'email', 'profile_image', 'age', 'date_of_birth', 'marital_status')
#         }),
#         ('Contact Information', {
#             'fields': ('phone_number', 'tel_number', 'address', 'nationality', 'Place_Of_Birth', 'Nearest_Port')
#         }),
#         ('Physical Details', {
#             'fields': ('Height_Cm', 'Weight_Kg', 'blood_type', 'smoker', 'overall_size', 'shirt_size', 'trouser_size', 'shoes_size'),
#             'classes': ('collapse',)
#         }),
#         ('Education & Language', {
#             'fields': ('college_or_school', 'english_language_level', 'other_language', 'other_language_level'),
#             'classes': ('collapse',)
#         }),
#         ('Marlins Test', {
#             'fields': ('marlins_test_issued_date', 'marlins_test_result', 'marlins_test_issued_by', 'marlins_test_issued_at'),
#             'classes': ('collapse',)
#         }),
#         ('Travel Documents', {
#             'fields': (
#                 'passport_no', 'passport_issue_date', 'passport_expiry_date', 'passport_issued_by', 'passport_place_of_issue',
#                 'seaman_book_no', 'seaman_book_issue_date', 'seaman_book_expiry_date', 'seaman_book_issued_by', 'seaman_book_place_of_issue',
#                 'other_seaman_book_no', 'other_seaman_book_issue_date', 'other_seaman_book_expiry_date', 'other_seaman_book_issued_by', 'other_seaman_book_place_of_issue'
#             ),
#             'classes': ('collapse',)
#         }),
#         ('Professional Qualifications', {
#             'fields': (
#                 'coc_certificate_name', 'coc_certificate_number', 'coc_issue_date', 'coc_expiry_date', 'coc_issued_by', 'coc_issued_at',
#                 'goc_certificate_number', 'goc_issue_date', 'goc_expiry_date', 'goc_issued_by', 'goc_issued_at'
#             ),
#             'classes': ('collapse',)
#         }),
#         ('Next of Kin', {
#             'fields': ('next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_address_country', 'next_of_kin_phone', 'next_of_kin_email'),
#             'classes': ('collapse',)
#         }),
#         ('Health Certificates', {
#             'fields': (
#                 'health_flag_state', 'health_number', 'health_issue_date', 'health_expiry_date', 'health_issued_by', 'health_issued_at',
#                 'international_medical_number', 'international_medical_issue_date', 'international_medical_expiry_date',
#                 'yellow_fever_number', 'yellow_fever_issue_date', 'yellow_fever_expiry_date',
#                 'cholera_number', 'cholera_issue_date', 'cholera_expiry_date'
#             ),
#             'classes': ('collapse',)
#         }),
#         ('COVID-19 Vaccination', {
#             'fields': ('covid_vaccine_name', 'covid_first_dose', 'covid_second_dose', 'covid_other_doses_or_remarks'),
#             'classes': ('collapse',)
#         }),
#         ('Health Declarations', {
#             'fields': ('disease_history', 'accident_history', 'psychiatric_treatment_history', 'addiction_history'),
#             'classes': ('collapse',)
#         }),
#         ('Declaration', {
#             'fields': ('declaration_consent', 'declaration_date', 'declaration_place'),
#             'classes': ('collapse',)
#         }),
#         ('Office Use', {
#             'fields': ('initial_assessment_comments', 'responsible_person_name', 'assessment_date'),
#             'classes': ('collapse',)
#         }),
#         ('Visa Status', {
#             'fields': ('us_visa_status', 'schengen_visa_status'),
#             'classes': ('collapse',)
#         }),
#         ('System Info', {
#             'fields': ('user_status', 'salary', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#         ('Certificates & Ranks', {
#             'fields': ('certificates', 'codes'),
#             'description': 'Select certificates and ranks for this user'
#         }),
#     )


# # Register models
# admin.site.register(Users, UsersAdmin)


# @admin.register(Rank)
# class RankAdmin(admin.ModelAdmin):
#     list_display = ('code', 'name')
#     search_fields = ('code', 'name')
#     ordering = ('code',)


# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ('code', 'name')
#     search_fields = ('code', 'name')
#     ordering = ('code',)


# @admin.register(UserRank)
# class UserRankAdmin(admin.ModelAdmin):
#     list_display = ('user', 'rank', 'assigned_code')
#     list_filter = ('rank',)
#     search_fields = ('user__email', 'user__first_name', 'assigned_code')
#     readonly_fields = ('assigned_code',)


# @admin.register(Contract)
# class ContractAdmin(admin.ModelAdmin):
#     list_display = ('user', 'ship', 'rank', 'sign_on_date', 'status')
#     list_filter = ('status', 'sign_on_date')
#     search_fields = ('user__email', 'user__first_name')


# @admin.register(Reference)
# class ReferenceAdmin(admin.ModelAdmin):
#     list_display = ('user', 'company_name', 'position', 'name')
#     search_fields = ('user__email', 'company_name', 'name')


# @admin.register(SeaService)
# class SeaServiceAdmin(admin.ModelAdmin):
#     list_display = ('user', 'company_name', 'vessel_name_imo', 'rank', 'signed_on', 'signed_off')
#     list_filter = ('signed_on', 'signed_off')
#     search_fields = ('user__email', 'company_name', 'vessel_name_imo')




from django.contrib import admin
from django import forms
from .models import (
    Users, Rank, Certificate, UserRank, Contract, Reference, SeaService,
    Company, Interview, CVSubmission  # Add new models, NO FinanceRecord
)
#from finance.models import FinanceRecord  # Import from finance app


class UsersAdminForm(forms.ModelForm):
    """Custom form that handles ManyToMany relationships and password hashing"""
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave empty for default password"
    )

    class Meta:
        model = Users
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_password('defaultpassword123')

        if commit:
            user.save()
            self.save_m2m()

        return user


class UsersAdmin(admin.ModelAdmin):
    form = UsersAdminForm
    list_display = ('email', 'first_name', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'marital_status', 'nationality')
    search_fields = ('email', 'first_name', 'middle_name')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    filter_horizontal = ('certificates', 'codes')

    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'middle_name', 'email', 'profile_image', 'age', 'date_of_birth', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'tel_number', 'address', 'nationality', 'Place_Of_Birth', 'Nearest_Port')
        }),
        ('Physical Details', {
            'fields': ('Height_Cm', 'Weight_Kg', 'blood_type', 'smoker', 'overall_size', 'shirt_size', 'trouser_size', 'shoes_size'),
            'classes': ('collapse',)
        }),
        ('Education & Language', {
            'fields': ('college_or_school', 'english_language_level', 'other_language', 'other_language_level'),
            'classes': ('collapse',)
        }),
        ('Marlins Test', {
            'fields': ('marlins_test_issued_date', 'marlins_test_result', 'marlins_test_issued_by', 'marlins_test_issued_at'),
            'classes': ('collapse',)
        }),
        ('Travel Documents', {
            'fields': (
                'passport_no', 'passport_issue_date', 'passport_expiry_date', 'passport_issued_by', 'passport_place_of_issue',
                'seaman_book_no', 'seaman_book_issue_date', 'seaman_book_expiry_date', 'seaman_book_issued_by', 'seaman_book_place_of_issue',
                'other_seaman_book_no', 'other_seaman_book_issue_date', 'other_seaman_book_expiry_date', 'other_seaman_book_issued_by', 'other_seaman_book_place_of_issue'
            ),
            'classes': ('collapse',)
        }),
        ('Professional Qualifications', {
            'fields': (
                'coc_certificate_name', 'coc_certificate_number', 'coc_issue_date', 'coc_expiry_date', 'coc_issued_by', 'coc_issued_at',
                'goc_certificate_number', 'goc_issue_date', 'goc_expiry_date', 'goc_issued_by', 'goc_issued_at'
            ),
            'classes': ('collapse',)
        }),
        ('Next of Kin', {
            'fields': ('next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_address_country', 'next_of_kin_phone', 'next_of_kin_email'),
            'classes': ('collapse',)
        }),
        ('Health Certificates', {
            'fields': (
                'health_flag_state', 'health_number', 'health_issue_date', 'health_expiry_date', 'health_issued_by', 'health_issued_at',
                'international_medical_number', 'international_medical_issue_date', 'international_medical_expiry_date',
                'yellow_fever_number', 'yellow_fever_issue_date', 'yellow_fever_expiry_date',
                'cholera_number', 'cholera_issue_date', 'cholera_expiry_date'
            ),
            'classes': ('collapse',)
        }),
        ('COVID-19 Vaccination', {
            'fields': ('covid_vaccine_name', 'covid_first_dose', 'covid_second_dose', 'covid_other_doses_or_remarks'),
            'classes': ('collapse',)
        }),
        ('Health Declarations', {
            'fields': ('disease_history', 'accident_history', 'psychiatric_treatment_history', 'addiction_history'),
            'classes': ('collapse',)
        }),
        ('Declaration', {
            'fields': ('declaration_consent', 'declaration_date', 'declaration_place'),
            'classes': ('collapse',)
        }),
        ('Office Use', {
            'fields': ('initial_assessment_comments', 'responsible_person_name', 'assessment_date'),
            'classes': ('collapse',)
        }),
        ('Visa Status', {
            'fields': ('us_visa_status', 'schengen_visa_status'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('user_status', 'role', 'salary', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Certificates & Ranks', {
            'fields': ('certificates', 'codes'),
            'description': 'Select certificates and ranks for this user'
        }),
    )


admin.site.register(Users, UsersAdmin)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(UserRank)
class UserRankAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'assigned_code')
    list_filter = ('rank',)
    search_fields = ('user__email', 'user__first_name', 'assigned_code')
    readonly_fields = ('assigned_code',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'ship', 'company', 'rank', 'sign_on_date', 'status')
    list_filter = ('status', 'sign_on_date', 'company')
    search_fields = ('user__email', 'user__first_name', 'ship__ship_name')


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'position', 'name')
    search_fields = ('user__email', 'company_name', 'name')


@admin.register(SeaService)
class SeaServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'vessel_name_imo', 'rank', 'signed_on', 'signed_off')
    list_filter = ('signed_on', 'signed_off')
    search_fields = ('user__email', 'company_name', 'vessel_name_imo')


# =====================
# NEW MODEL ADMINS
# =====================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_type', 'email', 'country', 'open_positions', 'status')
    list_filter = ('company_type', 'status', 'country')
    search_fields = ('name', 'email', 'contact_person')
    ordering = ('name',)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'company', 'position', 'scheduled_date', 'interview_type', 'status', 'result')
    list_filter = ('status', 'result', 'interview_type', 'scheduled_date')
    search_fields = ('candidate__email', 'candidate__first_name', 'company__name')
    ordering = ('-scheduled_date',)


@admin.register(CVSubmission)
class CVSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position', 'status', 'submitted_date', 'rating')
    list_filter = ('status', 'submitted_date')
    search_fields = ('user__email', 'user__first_name', 'company__name')
    ordering = ('-submitted_date',)


