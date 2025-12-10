from django.db import models

class Company(models.Model):
    COMPANY_TYPES = [
        ('Shipping Manning Companies', 'Shipping Manning Companies'),
        ('Cargo Manning Companies', 'Cargo Manning Companies'),
        ('Cruise & Hospitality Manning Companies', 'Cruise & Hospitality Manning Companies'),
        ('Offshore & Oil/Gas Manning Companies', 'Offshore & Oil/Gas Manning Companies'),
        ('Fishing Fleet Manning Companies', 'Fishing Fleet Manning Companies'),
        ('General Crew Manning Companies', 'General Crew Manning Companies'),
        ('Specialized Marine Manning Companies', 'Specialized Marine Manning Companies'),
        ('Temporary / Contract Manning Agencies', 'Temporary / Contract Manning Agencies'),
        ('Full Crew Management Companies', 'Full Crew Management Companies'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Prospect', 'Prospect'),
    ]

    company_name = models.CharField(max_length=200, unique=True)
    company_type = models.CharField(max_length=100, choices=COMPANY_TYPES)
    open_positions = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    contact_email = models.EmailField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 💰 hourly rate
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['company_name']

    def __str__(self):
        return self.company_name
