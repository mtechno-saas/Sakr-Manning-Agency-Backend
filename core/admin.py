
# core/admin.py
from django.contrib import admin
from .models import Flag, VesselType

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(VesselType)
class VesselTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
