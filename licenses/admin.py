from django.contrib import admin
from .models import UserLicense

@admin.register(UserLicense)
class UserLicenseAdmin(admin.ModelAdmin):
    # Fields to show in the main list
    list_display = ('document_name', 'user', 'document_number', 'country_of_issue', 'expiration_date')
    
    # Search functionality (searching through the document and the user's email/name)
    search_fields = ('document_name', 'document_number', 'user__email', 'user__first_name')
    
    # Filters on the right side
    list_filter = ('country_of_issue', 'expiration_date', 'issue_date')
    
    # Organizing the detail view
    fieldsets = (
        ('Ownership', {
            'fields': ('user',)
        }),
        ('Document Details', {
            'fields': ('document_name', 'document_number', 'country_of_issue')
        }),
        ('Validity', {
            'fields': ('issue_date', 'expiration_date')
        }),
        ('File Attachment', {
            'fields': ('document_file',)
        }),
    )

    # To make sure you don't accidentally link a license to no one
    raw_id_fields = ('user',)