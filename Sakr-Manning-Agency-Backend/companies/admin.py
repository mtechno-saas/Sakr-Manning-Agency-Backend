from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_type', 'status', 'open_positions', 'created_at')
    search_fields = ('company_name', 'contact_email')
    list_filter = ('company_type', 'status')
