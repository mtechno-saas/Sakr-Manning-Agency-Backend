# from django.db import models
# from companies.models import Company

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


from django.db import models
from companies.models import Company
# Import the Users model from your api app
from api.models import Users

class Ship(models.Model):
    SHIP_TYPES = [
        ('Container Ship', 'Container Ship'),
        ('Cruise Ship', 'Cruise Ship'),
        ('Bulk Carrier', 'Bulk Carrier'),
        ('Tanker', 'Tanker'),
        ('Other', 'Other'),
    ]

    SHIP_STATUS = [
        ('Active', 'Active'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Inactive', 'Inactive'),
    ]

    ship_name = models.CharField(max_length=200)
    imo_number = models.CharField(max_length=10, unique=True)
    ship_type = models.CharField(max_length=20, choices=SHIP_TYPES)
    flag_country = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ships')
    status = models.CharField(max_length=20, choices=SHIP_STATUS, default='Active')

    # --- This is the new field to connect Ships and Users ---
    crew = models.ManyToManyField(
        Users,
        related_name='ships',  # Lets you access user.ships
        blank=True             # Allows a ship to have no crew members
    )
    # ---------------------------------------------------------

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
