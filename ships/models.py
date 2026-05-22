

# from django.db import models
# from companies.models import Company
# # Import the Users model from your api app
# from api.models import Users

# class Ship(models.Model):
#     SHIP_TYPES = [
#         ('Container Ship', 'Container Ship'),
#         ('Cruise Ship', 'Cruise Ship'),
#         ('Bulk Carrier', 'Bulk Carrier'),
#         ('Tanker', 'Tanker'),
#         ('Other', 'Other'),
#     ]

#     SHIP_STATUS = [
#         ('Active', 'Active'),
#         ('Under Maintenance', 'Under Maintenance'),
#         ('Inactive', 'Inactive'),
#     ]

#     ship_name = models.CharField(max_length=200)
#     imo_number = models.CharField(max_length=10, unique=True)
#     ship_type = models.CharField(max_length=20, choices=SHIP_TYPES)
#     flag_country = models.CharField(max_length=100)
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ships')
#     status = models.CharField(max_length=20, choices=SHIP_STATUS, default='Active')

#     # --- This is the new field to connect Ships and Users ---
#     crew = models.ManyToManyField(
#         Users,
#         related_name='ships',  # Lets you access user.ships
#         blank=True             # Allows a ship to have no crew members
#     )
#     # ---------------------------------------------------------

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['imo_number']),
#             models.Index(fields=['company']),
#         ]
#         ordering = ['ship_name']

#     def __str__(self):
#         return f"{self.ship_name} ({self.imo_number})"

# ships/models.py
from django.db import models
from companies.models import Company
from core.models import Flag, VesselType  # <-- Import new models
from api.models import Users  # Assuming your custom user model is here

class Ship(models.Model):
    SHIP_STATUS = [
        ('Active', 'Active'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Inactive', 'Inactive'),
    ]

    # --- Core Information ---
    ship_name = models.CharField(max_length=200, null=True, blank=True)
    imo_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='ships')
    crew = models.ManyToManyField(Users, related_name='ships', blank=True)

    # --- Fields from Figma (New & Updated) ---
    ship_type = models.ForeignKey(
        VesselType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ships'
    )
    flag = models.ForeignKey(
        Flag,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ships'
    )
    official_no = models.CharField(max_length=50, null=True, blank=True)
    call_sign = models.CharField(max_length=20, null=True, blank=True)
    mmsi_no = models.CharField(max_length=50, null=True, blank=True)
    port_of_registry = models.CharField(max_length=100, null=True, blank=True)

    # --- Technical Details ---
    gross_tonnage = models.PositiveIntegerField(default=0, null=True, blank=True)
    deadweight = models.PositiveIntegerField(default=0, help_text="in metric tons", null=True, blank=True)
    year_built = models.PositiveIntegerField(null=True, blank=True)
    builder = models.CharField(max_length=200, null=True, blank=True)
    engine_type = models.CharField(max_length=100, null=True, blank=True)
    engine_power_kw = models.PositiveIntegerField(default=0, verbose_name="Engine Power (KW)", null=True, blank=True)

    # --- Status & Timestamps ---
    status = models.CharField(max_length=20, choices=SHIP_STATUS, default='Active', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['imo_number']),
            models.Index(fields=['company']),
        ]
        ordering = ['ship_name']

    def __str__(self):
        return f"{self.ship_name} ({self.imo_number})"
