


# # api/admin.py
# from django.contrib import admin
# from .models import Rank, Users, Certificate, UserRank , Contract
# from ships.models import Ship
# from django.utils.html import format_html
# from tickets_papers.models import Ticket, TravelingPaper
# from rest_framework.authtoken.models import TokenProxy as AuthToken

# # --- Admin Site Configuration ---
# admin.site.site_header = "Sakr Manning Agency Administration"
# admin.site.site_title = "Sakr Manning Admin Portal"
# admin.site.index_title = "Welcome to Sakr Manning Agency Management"


# # --- Inlines for related models ---
# class TicketInline(admin.TabularInline):
#     model = Ticket
#     extra = 0
#     readonly_fields = ("created_at",)
#     fields = ("ticket_number", "file", "created_at")


# class TravelingPaperInline(admin.TabularInline):
#     model = TravelingPaper
#     extra = 0
#     readonly_fields = ("created_at",)
#     fields = ("title", "issued_date", "file", "created_at")


# class UserRankInline(admin.TabularInline):
#     model = UserRank
#     extra = 0
#     readonly_fields = ("assigned_code",)
#     fields = ("rank", "assigned_code")


# # --- Main ModelAdmin for Users ---
# @admin.register(Users)
# class UsersAdmin(admin.ModelAdmin):
#     # This line creates the double-box widget for both codes and certificates.
#     filter_horizontal = ("codes","certificates")

#     # This organizes the user detail page into collapsible sections.
#     fieldsets = (
#         ("Personal & Contact Info", {
#             "fields": ("first_name", "last_name", "profile_image", "user_status", "marital_status", "age", "date_of_birth", "nationality", "Place_Of_Birth", "address", "phone_number", "email")
#         }),
#         ("Employment & Education", {
#             "fields": ("salary", "college_or_school", "marlins_test_result", "marlins_test_issued_date")
#         }),
#         # This section will now correctly render the multi-select widget for codes.
#         # ("Ranks (Codes)", {
#         #     "fields": ("codes",)
#         # }),
#         # This section is now added back to render the certificates widget.
#         ("Certificates & Training", {
#             "fields": ("certificates",)
#         }),
#         ("Travel Documents", {
#             "classes": ("collapse",),
#             "fields": (
#                 "passport_no", "passport_issue_date", "passport_expiry_date",
#                 "seaman_book_no", "seaman_book_issue_date", "seaman_book_expiry_date",
#             )
#         }),
#         ("Health & Vaccinations", {
#             "classes": ("collapse",),
#             "fields": (
#                 "health_flag_state", "health_issue_date", "health_expiry_date",
#                 "yellow_fever_issue_date", "yellow_fever_expiry_date",
#                 "covid_first_dose", "covid_second_dose",
#             )
#         }),
#     )

#     # --- List View Configuration ---
#     list_display = (
#         "first_name",
#         "last_name",
#         "user_status",
#         "profile_pic",
#         "nationality",
#         "get_user_ranks",
#         "get_certificates",
#         "get_assigned_ships",
#     )
#     list_filter = ("nationality", "user_status", "codes" , "ships")
#     search_fields = ("first_name", "last_name", "email", "user_ranks__assigned_code")

#     # --- Inlines ---
#     inlines = [UserRankInline, TicketInline, TravelingPaperInline]

#     # --- Custom Display Methods ---
#     def get_user_ranks(self, obj):
#         return ", ".join(
#             [f"{ur.assigned_code} ({ur.rank.name})" for ur in obj.user_ranks.all()]
#         )
#     get_user_ranks.short_description = "User Ranks"

#     def get_certificates(self, obj):
#         return ", ".join([c.name for c in obj.certificates.all()])
#     get_certificates.short_description = "Certificates"


#     def get_assigned_ships(self, obj):
#         """
#         Gets all ships the user is a crew member of.
#         The 'ships' related_name comes from the ManyToManyField on the Ship model.
#         """
#         # `obj.ships.all()` works because of the `related_name='ships'`
#         # we set on the `crew` field in the `Ship` model.
#         return ", ".join([ship.ship_name for ship in obj.ships.all()])

#     # Give the column a user-friendly name in the admin
#     get_assigned_ships.short_description = 'Assigned Ships'

#     def profile_pic(self, obj):
#         if obj.profile_image:
#             return format_html(
#                 '<img src="{}" width="50" height="50" style="border-radius:50%;" />',
#                 obj.profile_image.url,
#             )
#         return "No Image"
#     profile_pic.short_description = "Profile Image"


# # --- Other ModelAdmins ---
# @admin.register(Rank)
# class RankAdmin(admin.ModelAdmin):
#     list_display = ("code", "name")
#     search_fields = ("code", "name")


# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ("name",)
#     search_fields = ("name",)


# @admin.register(UserRank)
# class UserRankAdmin(admin.ModelAdmin):
#     list_display = ("user", "rank", "assigned_code")
#     search_fields = ("user__first_name", "user__last_name", "rank__name", "assigned_code")
#     list_filter = ("rank",)

# @admin.register(Contract)
# class ContractAdmin(admin.ModelAdmin):
#     list_display = ('user', 'ship', 'rank', 'sign_on_date', 'sign_off_date', 'status')
#     list_filter = ('status', 'ship', 'rank')
#     search_fields = ('user__email', 'ship__ship_name')

# if admin.site.is_registered(AuthToken):
#     admin.site.unregister(AuthToken)


# admin.py - Update your admin.py file with this content
from django.contrib import admin
from django import forms
from .models import Users, Rank, Certificate, UserRank, Contract, Reference, SeaService

class UsersAdminForm(forms.ModelForm):
    """Custom form that handles username generation and ManyToMany relationships"""
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave empty for default password"
    )
    
    class Meta:
        model = Users
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        
        # Auto-generate username from email if not provided
        if email and not cleaned_data.get('username'):
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            # Ensure username is unique
            while Users.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            cleaned_data['username'] = username
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set username from cleaned_data
        if hasattr(self, 'cleaned_data') and 'username' in self.cleaned_data:
            user.username = self.cleaned_data['username']
        
        # Handle password
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:  # New user without password
            user.set_password('defaultpassword123')
        
        if commit:
            user.save()
            self.save_m2m()  # Save ManyToMany relationships
        
        return user

class UsersAdmin(admin.ModelAdmin):
    form = UsersAdminForm
    
    # Fields to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'username', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'marital_status', 'nationality')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('email',)
    
    # Make username read-only since it's auto-generated
    readonly_fields = ('username', 'date_joined', 'last_login')
    
    # Nice widgets for ManyToMany fields
    filter_horizontal = ('certificates', 'codes')
    
    # Organize fields in sections
    fieldsets = (
        # ('Authentication', {
        #     'fields': ('email', 'username', 'password'),
        #     'description': 'Username is auto-generated from email'
        # }),
        ('Personal Info', {
            'fields': ('first_name', 'middle_name', 'last_name', 'email', 'profile_image', 'age', 'date_of_birth', 'marital_status')
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
            'fields': ('passport_no', 'passport_issue_date', 'passport_expiry_date', 'passport_issued_by', 'passport_place_of_issue',
                      'seaman_book_no', 'seaman_book_issue_date', 'seaman_book_expiry_date', 'seaman_book_issued_by', 'seaman_book_place_of_issue',
                      'other_seaman_book_no', 'other_seaman_book_issue_date', 'other_seaman_book_expiry_date', 'other_seaman_book_issued_by', 'other_seaman_book_place_of_issue'),
            'classes': ('collapse',)
        }),
        ('Professional Qualifications', {
            'fields': ('coc_certificate_name', 'coc_certificate_number', 'coc_issue_date', 'coc_expiry_date', 'coc_issued_by', 'coc_issued_at',
                      'goc_certificate_number', 'goc_issue_date', 'goc_expiry_date', 'goc_issued_by', 'goc_issued_at'),
            'classes': ('collapse',)
        }),
        ('Next of Kin', {
            'fields': ('next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_address_country', 'next_of_kin_phone', 'next_of_kin_email'),
            'classes': ('collapse',)
        }),
        ('Health Certificates', {
            'fields': ('health_flag_state', 'health_number', 'health_issue_date', 'health_expiry_date', 'health_issued_by', 'health_issued_at',
                      'international_medical_number', 'international_medical_issue_date', 'international_medical_expiry_date',
                      'yellow_fever_number', 'yellow_fever_issue_date', 'yellow_fever_expiry_date',
                      'cholera_number', 'cholera_issue_date', 'cholera_expiry_date'),
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
            'fields': ('user_status', 'salary', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
        ('Certificates & Ranks', {
            'fields': ('certificates', 'codes'),
            'description': 'Select certificates and ranks for this user'
        }),
    )

# Register models
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
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'assigned_code')
    readonly_fields = ('assigned_code',)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'ship', 'rank', 'sign_on_date', 'status')
    list_filter = ('status', 'sign_on_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'position', 'name')
    search_fields = ('user__email', 'company_name', 'name')

@admin.register(SeaService)
class SeaServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'vessel_name_imo', 'rank', 'signed_on', 'signed_off')
    list_filter = ('signed_on', 'signed_off')
    search_fields = ('user__email', 'company_name', 'vessel_name_imo')
