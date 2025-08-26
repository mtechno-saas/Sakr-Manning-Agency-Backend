from django.contrib import admin
from .models import Ship

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ('ship_name', 'imo_number', 'ship_type', 'status', 'company', 'created_at')
    search_fields = ('ship_name', 'imo_number')
    list_filter = ('ship_type', 'status', 'company')
