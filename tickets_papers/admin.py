# from django.contrib import admin
# from .models import Ticket, TravelingPaper

# @admin.register(Ticket)
# class TicketAdmin(admin.ModelAdmin):
#     list_display = ("ticket_number", "user", "file", "created_at")
#     search_fields = ("ticket_number", "user__first_name", "user__last_name")
#     list_filter = ("created_at",)


# @admin.register(TravelingPaper)
# class TravelingPaperAdmin(admin.ModelAdmin):
#     list_display = ("title", "user", "issued_date", "file", "created_at")
#     search_fields = ("title", "user__first_name", "user__last_name")
#     list_filter = ("issued_date", "created_at")


from django.contrib import admin
from .models import Ticket, TravelingPaper
from api.models import Users



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "user", "created_at")
    search_fields = ("ticket_number", "user__first_name", "user__last_name")
    list_filter = ("created_at",)


@admin.register(TravelingPaper)
class TravelingPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "issued_date", "created_at")
    search_fields = ("title", "user__first_name", "user__last_name")
    list_filter = ("issued_date", "created_at")

