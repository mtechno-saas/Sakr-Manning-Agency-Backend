from django.db import models
from api.models import Users
from companies.models import Company


class FinanceRecord(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="finance_records")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="finance_records")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    @property
    def total_days(self):
        """Total days worked"""
        return (self.end_date - self.start_date).days + 1

    @property
    def daily_rate(self):
        """Calculate daily rate from company's hourly_rate"""
        if hasattr(self.company, "hourly_rate") and self.company.hourly_rate:
            return self.company.hourly_rate * 8  # assume 8 hrs/day
        return 0

    @property
    def total_money(self):
        return self.total_days * self.daily_rate

    def __str__(self):
        return f"{self.user.first_name} @ {self.company.company_name} ({self.start_date} → {self.end_date})"
