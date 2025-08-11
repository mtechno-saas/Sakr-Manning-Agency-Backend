# from django.contrib import admin
# from . import models
# # Register your models here.
# admin.site.site_header = "Sakr Manning Agency Administration"
# admin.site.site_title = "Sakr Manning Admin Portal"
# admin.site.index_title = "Welcome to Sakr Manning Agency Management"
# admin.site.register(models.Users)


# api/admin.py
# api/admin.py
from django.contrib import admin
from .models import Users

@admin.register(Users)
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


    )




    readonly_fields = ("created_at", "updated_at")  
    list_display = ("first_name", "last_name", "nationality", "email", "phone_number", "salary")
    search_fields = ("first_name", "last_name", "email", "phone_number","salary","nationality")
    list_filter = ("nationality",)

