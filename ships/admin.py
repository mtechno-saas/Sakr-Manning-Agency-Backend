# from django.contrib import admin
# from .models import Ship

# @admin.register(Ship)
# class ShipAdmin(admin.ModelAdmin):
#     list_display = ('ship_name', 'imo_number', 'ship_type', 'status', 'company', 'created_at')
#     search_fields = ('ship_name', 'imo_number')
#     list_filter = ('ship_type', 'status', 'company')


from django.contrib import admin
from .models import Ship

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ('ship_name', 'imo_number', 'ship_type', 'status', 'company', 'get_crew_count')
    search_fields = ('ship_name', 'imo_number', 'crew__first_name', 'crew__last_name') # Allow searching by crew member name
    list_filter = ('ship_type', 'status', 'company')

    # This creates the user-friendly multi-select box for adding crew members
    filter_horizontal = ('crew',)

    # Add a custom method to show how many crew members are on a ship
    def get_crew_count(self, obj):
        return obj.crew.count()
    get_crew_count.short_description = 'Crew Count'
