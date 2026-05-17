from django.db import models
from core.models import Flag
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
        ('Maritime Services Company', 'Maritime Services Company'),
        ('Crewing & Manning Agency', 'Crewing & Manning Agency'),
        ('Shipping & Marine Services Company', 'Shipping & Marine Services Company'),
        ('International Ship Manning & Crew Management', 'International Ship Manning & Crew Management'),
        ('Marine Recruitment & Offshore Services', 'Marine Recruitment & Offshore Services'),
        ('Global Maritime Crewing Solutions', 'Global Maritime Crewing Solutions'),
        ('Shipping, Manning & Logistics Company', 'Shipping, Manning & Logistics Company'),
        ('Marine Operations & Crew Supply Services', 'Marine Operations & Crew Supply Services'),
        ('Offshore, Cargo & Passenger Crew Management', 'Offshore, Cargo & Passenger Crew Management'),
        ('Full Maritime & Ship Management Services', 'Full Maritime & Ship Management Services'),
        ('Seafarer Recruitment & Crew Deployment Company', 'Seafarer Recruitment & Crew Deployment Company'),
        ('Marine Human Resources & Manning Services', 'Marine Human Resources & Manning Services'),
        ('Cruise, Cargo & Offshore Crewing Agency', 'Cruise, Cargo & Offshore Crewing Agency'),
        ('Maritime Consultancy & Ship Crew Management', 'Maritime Consultancy & Ship Crew Management'),
        ('Global Shipping & Marine Support Services', 'Global Shipping & Marine Support Services'),
        ('Cargo & Bulker Manning Company', 'Cargo & Bulker Manning Company'),
        ('Other', 'Other'),
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
    website = models.URLField(max_length=255, blank=True, null=True, help_text="Company website URL")
    company_flag = models.CharField(
        max_length=100,
        choices=Flag.FLAG_CHOICES,
        blank=True,
        null=True,
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


class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

