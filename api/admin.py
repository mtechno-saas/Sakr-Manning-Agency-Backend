
# from django.contrib import admin
# from .models import Rank, Users , CERTIFICATES ,Certificate , UserRank
# from django import forms
# from django.utils.html import format_html
# from tickets_papers.models import Ticket, TravelingPaper

# admin.site.site_header = "Sakr Manning Agency Administration"
# admin.site.site_title = "Sakr Manning Admin Portal"
# admin.site.index_title = "Welcome to Sakr Manning Agency Management"




# api/admin.py
from django.contrib import admin
from .models import Rank, Users, Certificate, UserRank
from django.utils.html import format_html
from tickets_papers.models import Ticket, TravelingPaper

# --- Admin Site Configuration ---
admin.site.site_header = "Sakr Manning Agency Administration"
admin.site.site_title = "Sakr Manning Admin Portal"
admin.site.index_title = "Welcome to Sakr Manning Agency Management"


# --- Inlines for related models ---
class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("ticket_number", "file", "created_at")


class TravelingPaperInline(admin.TabularInline):
    model = TravelingPaper
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("title", "issued_date", "file", "created_at")


class UserRankInline(admin.TabularInline):
    model = UserRank
    extra = 0
    readonly_fields = ("assigned_code",)
    fields = ("rank", "assigned_code")


# --- Main ModelAdmin for Users ---
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    # This line creates the double-box widget for both codes and certificates.
    filter_horizontal = ("codes","certificates")

    # This organizes the user detail page into collapsible sections.
    fieldsets = (
        ("Personal & Contact Info", {
            "fields": ("first_name", "last_name", "profile_image", "user_status", "marital_status", "age", "date_of_birth", "nationality", "Place_Of_Birth", "address", "phone_number", "email")
        }),
        ("Employment & Education", {
            "fields": ("salary", "college_or_school", "marlins_test_result", "marlins_test_issued_date")
        }),
        # This section will now correctly render the multi-select widget for codes.
        # ("Ranks (Codes)", {
        #     "fields": ("codes",)
        # }),
        # This section is now added back to render the certificates widget.
        ("Certificates & Training", {
            "fields": ("certificates",)
        }),
        ("Travel Documents", {
            "classes": ("collapse",),
            "fields": (
                "passport_no", "passport_issue_date", "passport_expiry_date",
                "seaman_book_no", "seaman_book_issue_date", "seaman_book_expiry_date",
            )
        }),
        ("Health & Vaccinations", {
            "classes": ("collapse",),
            "fields": (
                "health_flag_state", "health_issue_date", "health_expiry_date",
                "yellow_fever_issue_date", "yellow_fever_expiry_date",
                "covid_first_dose", "covid_second_dose",
            )
        }),
    )

    # --- List View Configuration ---
    list_display = (
        "first_name",
        "last_name",
        "user_status",
        "profile_pic",
        "nationality",
        "get_user_ranks",
        "get_certificates",
    )
    list_filter = ("nationality", "user_status", "codes")
    search_fields = ("first_name", "last_name", "email", "user_ranks__assigned_code")

    # --- Inlines ---
    inlines = [UserRankInline, TicketInline, TravelingPaperInline]

    # --- Custom Display Methods ---
    def get_user_ranks(self, obj):
        return ", ".join(
            [f"{ur.assigned_code} ({ur.rank.name})" for ur in obj.user_ranks.all()]
        )
    get_user_ranks.short_description = "User Ranks"

    def get_certificates(self, obj):
        return ", ".join([c.name for c in obj.certificates.all()])
    get_certificates.short_description = "Certificates"

    def profile_pic(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;" />',
                obj.profile_image.url,
            )
        return "No Image"
    profile_pic.short_description = "Profile Image"


# --- Other ModelAdmins ---
@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(UserRank)
class UserRankAdmin(admin.ModelAdmin):
    list_display = ("user", "rank", "assigned_code")
    search_fields = ("user__first_name", "user__last_name", "rank__name", "assigned_code")
    list_filter = ("rank",)


