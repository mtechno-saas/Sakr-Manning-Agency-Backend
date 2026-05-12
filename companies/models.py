from django.db import models
from core.models import Flag, CompanyType

class Company(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Prospect', 'Prospect'),
    ]

    company_name = models.CharField(max_length=200, unique=True)
    company_type = models.ForeignKey(
        CompanyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies'
    )
    open_positions = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    owner = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True, help_text="Company website URL")
    company_flag = models.ForeignKey(
        Flag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies_with_flag',
        help_text="Country flag / nationality of the company"
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 💰 hourly rate
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['company_name']

    def __str__(self):
        return self.company_name


class JobOrder(models.Model):
    """
    Step 1: Client Management & Job Order Control
    Represents a formal manpower request from a Shipowner/Manager.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Open', 'Open / Sourcing'),
        ('Active', 'Active'),
        ('In Progress', 'In Progress / Interviewing'),
        ('Fulfilled', 'Fulfilled'),
        ('Cancelled', 'Cancelled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_orders')
    ship = models.ForeignKey('ships.Ship', on_delete=models.SET_NULL, null=True, blank=True, related_name='job_orders')
    reference_number = models.CharField(max_length=50, unique=True, help_text="e.g. JO-2024-001")
    request_date = models.DateField()
    target_joining_date = models.DateField()
    
    # Details from workflow Step 1B
    vessel_type_override = models.CharField(max_length=100, blank=True, help_text="Override if different from ship's default")
    trading_area = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.reference_number} - {self.company.company_name}"


class JobOrderPosition(models.Model):
    """
    Specific ranks required within a Job Order.
    Step 1C: Confirm rank, salary scale, etc.
    """
    job_order = models.ForeignKey(JobOrder, on_delete=models.CASCADE, related_name='positions')
    rank = models.ForeignKey('api.Rank', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    
    contract_duration_months = models.PositiveIntegerField(default=6)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.rank} ({self.quantity}) for {self.job_order.reference_number}"

