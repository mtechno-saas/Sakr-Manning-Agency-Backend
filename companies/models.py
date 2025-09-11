from django.db import models

class Company(models.Model):
    COMPANY_TYPES = [
        ('Shipping', 'Shipping'),
        ('Cruise', 'Cruise'),
        ('Cargo', 'Cargo'),
        ('Offshore', 'Offshore'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    company_name = models.CharField(max_length=200, unique=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    open_positions = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    contact_email = models.EmailField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 💰 hourly rate
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.company_name
