# from django.contrib import admin
# from . import models
# # Register your models here.

# admin.site.register(models.Users)


# api/admin.py
# api/admin.py
from django.contrib import admin
from .models import Users , CERTIFICATES 
from django import forms
from django.utils.html import format_html

admin.site.site_header = "Sakr Manning Agency Administration"
admin.site.site_title = "Sakr Manning Admin Portal"
admin.site.index_title = "Welcome to Sakr Manning Agency Management"


# class UsersAdminForm(forms.ModelForm):
#     codes = forms.MultipleChoiceField(
#         choices=RANKS,
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )
#     certificates = forms.MultipleChoiceField(
#         choices=CERTIFICATES,
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Users
#         fields = "__all__"

#     def clean_codes(self):
#         return self.cleaned_data["codes"]

#     def clean_certificates(self):
#         return self.cleaned_data["certificates"]


#@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Personal Information", {
            "fields": (
                "first_name", "last_name", "age", "date_of_birth", 
                "nationality", "Place_Of_Birth", "Nearest_Port", 
                "Height_Cm", "Weight_Kg", "marital_status"
            )
        }),
        ("Contact Information", {
            "fields": ("address", "phone_number", "email")
        }),
        ("Employment Details", {
            "fields": ("salary",)
        }),
        ("Education Details", {
            "fields": (
                "marlins_test_issued_date",
                "marlins_test_result",
                "marlins_test_issued_by",
                "marlins_test_issued_at",
                "college_or_school"
            ),
            "description": "Includes Marlins Test and other certifications."
        }),
            ("Code Employee", {
            "fields": ("codes",),
           # "classes": ("collapse",),  # This makes it collapsible
            "description": "Expand to select completed codes for employement."
        }),
        ("Travel Documents", {
            "fields": (
                "passport_no", "passport_issue_date", "passport_expiry_date",
                "passport_issued_by", "passport_place_of_issue",
                "seaman_book_no", "seaman_book_issue_date", "seaman_book_expiry_date",
                "seaman_book_issued_by", "seaman_book_place_of_issue",
                "other_seaman_book_no", "other_seaman_book_issue_date", "other_seaman_book_expiry_date",
                "other_seaman_book_issued_by", "other_seaman_book_place_of_issue"
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),

                # ... existing sections ...

        ("Professional Qualification / Certificate of Competency", {
            "fields": (
                "coc_certificate_name", "coc_certificate_number",
                "coc_issue_date", "coc_expiry_date",
                "coc_issued_by", "coc_issued_at",
                "goc_certificate_number",
                "goc_issue_date", "goc_expiry_date",
                "goc_issued_by", "goc_issued_at"
            )
        }),

         ("Next of Kin / Emergency Contact", {
            "fields": (
                "next_of_kin_full_name",
                "next_of_kin_relationship",
                "next_of_kin_address_country",
                "next_of_kin_phone",
                "next_of_kin_email"
            )
        }),

        ("Health Certificates & Vaccinations", {
        "fields": (
        "health_flag_state", "health_number", "health_issue_date", "health_expiry_date",
        "health_issued_by", "health_issued_at",
        "international_medical_number", "international_medical_issue_date", "international_medical_expiry_date",
        "yellow_fever_number", "yellow_fever_issue_date", "yellow_fever_expiry_date",
        "cholera_number", "cholera_issue_date", "cholera_expiry_date",
        "covid_vaccine_name", "covid_first_dose", "covid_second_dose", "covid_other_doses_or_remarks"
        ),
        "description": "Includes International Medical, Yellow Fever, Cholera, and COVID-19 vaccinations."
        }),

        ("Certificates & Training", {
            "fields": ("certificates",),
            "classes": ("collapse",),  # This makes it collapsible
            "description": "Expand to select completed certificates and training."
        }),


    )







    readonly_fields = ("created_at", "updated_at")  
    #list_display = ("first_name", "last_name", "nationality", "email", "phone_number", "salary","codes")
    search_fields = ("first_name", "last_name", "email", "phone_number","salary","nationality")
    list_filter = ("nationality","codes")

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "user_status",
        "profile_pic", 
        "nationality",
        "email",
        "phone_number",
        "salary",
        "display_codes",
        "get_certificates",
    )

    filter_horizontal = ('codes',)

    def display_codes(self, obj):
        return "\n ".join(f"{code.code} - {code.name}" for code in obj.codes.all())
    display_codes.short_description = "Codes"


    def get_certificates(self, obj):
        return "\n ".join(c.name for c in obj.certificates.all())

    get_certificates.short_description = "Certificates"

    def profile_pic(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.profile_image.url)
        return "No Image"
    profile_pic.short_description = "Profile Image"





