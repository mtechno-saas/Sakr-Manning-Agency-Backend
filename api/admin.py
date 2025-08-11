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
                "Height_Cm", "Weight_Kg"
            )
        }),
        ("Contact Information", {
            "fields": ("address", "phone_number", "email")
        }),
        ("Employment Details", {
            "fields": ("salary",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("created_at", "updated_at")  
    list_display = ("first_name", "last_name", "nationality", "email", "phone_number", "salary")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    list_filter = ("nationality",)

