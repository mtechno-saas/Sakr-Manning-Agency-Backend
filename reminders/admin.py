"""Django admin registration for the Reminders app."""
from django.contrib import admin

from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'reminder_date', 'reminder_time',
        'is_completed', 'created_at',
    )
    list_filter = ('is_completed', 'reminder_date')
    search_fields = ('user__email', 'user__first_name', 'user__middle_name', 'text')
    raw_id_fields = ('user',)
    date_hierarchy = 'reminder_date'
    ordering = ('reminder_date', 'reminder_time')
