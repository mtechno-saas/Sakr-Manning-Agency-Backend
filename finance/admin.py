from django.contrib import admin
from .models import FinanceRecord


@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "company",
        "start_date",
        "end_date",
        "get_total_days",
        "get_daily_rate",
        "get_total_money",
    )
    list_filter = ("company", "user", "start_date", "end_date")
    search_fields = ("user__first_name", "user__last_name", "company__company_name")

    def get_total_days(self, obj):
        return obj.total_days
    get_total_days.short_description = "Total Days"

    def get_daily_rate(self, obj):
        return obj.daily_rate
    get_daily_rate.short_description = "Daily Rate"

    def get_total_money(self, obj):
        return obj.total_money
    get_total_money.short_description = "Total Money"
