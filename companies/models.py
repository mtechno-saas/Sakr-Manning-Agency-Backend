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
    contact_person = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="Primary contact name at the company",
    )
    alt_phone = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Alternative phone number",
    )
    address = models.TextField(
        blank=True, null=True,
        help_text="Full postal address",
    )
    notes = models.TextField(
        blank=True, null=True,
        help_text="Internal notes about this company",
    )
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
        ('Open', 'Open / Sourcing'),
        ('Close', 'Closed'),
        ('Full Filled', 'Full Filled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_orders')
    ship = models.ForeignKey('ships.Ship', on_delete=models.SET_NULL, null=True, blank=True, related_name='job_orders')
    reference_number = models.CharField(max_length=50, unique=True, help_text="e.g. JO-2024-001")
    request_date = models.DateField()
    target_joining_date = models.DateField()

    # Details from workflow Step 1B
    vessel_type_override = models.CharField(max_length=100, blank=True, help_text="Override if different from ship's default")
    trading_area = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Open')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.reference_number} - {self.company.company_name}"

    def is_fully_filled(self) -> bool:
        """
        True when every position under this job order has been fully
        filled. A position counts as fully filled only when its
        quantity > 0 AND the number of contracts linked to it is >=
        quantity. Positions with quantity=0 (data quality edge case
        — e.g. imported legacy data) are SKIPPED, not failed — they
        don't block the order from being marked "fully filled".

        Contract statuses that count as "signed" (i.e. the slot is
        taken):
          - Active
          - Signed
          - Pending Signature
          - Pending
          - Completed
        Draft and Cancelled do NOT count (the slot is free again).

        NOTE: previously this only checked "Active" and "Signed",
        which made the UI's "remaining=0" disagree with the
        backend's "fully_filled" when the contract was in
        Pending Signature (the Contract Setup form's default).
        The UI counts Pending Signature as signed, so the backend
        must too.

        NOTE 2: an earlier version of this method used
        `if pos.quantity <= 0: return False` (early-out), which
        caused legacy positions with quantity=0 (e.g. the ETO
        position on HORIZON ATHANASIA in the 2026-09-04 incident)
        to be permanently reported as "not fully filled" even
        when a contract was assigned. `continue` is the correct
        behaviour here.
        """
        filled_statuses = (
            "Active", "Signed", "Pending Signature", "Pending", "Completed",
        )
        for pos in self.positions.all():
            if pos.quantity <= 0:
                # Legacy / data-quality edge case: a position with
                # quantity=0 has no slots to fill, so it can't
                # block the order. Skip it.
                continue
            filled = sum(
                1 for c in pos.contracts.all()
                if c.status in filled_statuses
            )
            if filled < pos.quantity:
                return False
        # No positions at all -> not "fully filled" (no work was
        # requested to begin with).
        return self.positions.exists()


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rank} ({self.quantity}) for {self.job_order.reference_number}"

