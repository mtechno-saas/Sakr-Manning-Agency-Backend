from django.db import models
from api.models import Users, Contract

class FlightBooking(models.Model):
    """
    Step 8A: Book flights in line with cost and routing policy.
    """
    STATUS_CHOICES = [
        ('Requested', 'Requested'),
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='flight_bookings')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='flights')
    
    airline = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=50)
    departure_airport = models.CharField(max_length=100)
    arrival_airport = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    
    pnr = models.CharField(max_length=50, blank=True, help_text="Passenger Name Record")
    ticket_number = models.CharField(max_length=50, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    
    ticket_file = models.FileField(upload_to='flights/tickets/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.airline} {self.flight_number} - {self.user.email}"


class VisaApplication(models.Model):
    """
    Step 7: Visa, Flag State & Port Formalities
    """
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('Documents Collected', 'Documents Collected'),
        ('Submitted', 'Submitted'),
        ('Appointment Scheduled', 'Appointment Scheduled'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    VISA_TYPES = [
        ('Schengen', 'Schengen'),
        ('US C1/D', 'US C1/D'),
        ('Transit', 'Transit'),
        ('Arrival', 'Arrival'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='visa_applications')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True)
    
    country = models.CharField(max_length=100)
    visa_type = models.CharField(max_length=50, choices=VISA_TYPES, default='Other')
    
    submission_date = models.DateField(null=True, blank=True)
    appointment_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Not Started')
    remarks = models.TextField(blank=True)
    
    document_file = models.FileField(upload_to='visas/documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.country} Visa ({self.visa_type}) for {self.user.email}"


class JoiningInstruction(models.Model):
    """
    Step 8C: Issue joining instructions.
    Consolidates flight, visa, and port agent details.
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='joining_instructions')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='joining_instructions')
    
    issue_date = models.DateField(auto_now_add=True)
    port_agent_name = models.CharField(max_length=255, blank=True)
    port_agent_contact = models.TextField(blank=True, help_text="Address, Phone, Email")
    
    embarkation_port = models.CharField(max_length=100)
    embarkation_date = models.DateField()
    
    additional_guidelines = models.TextField(blank=True)
    
    is_sent_to_crew = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Joining Instr. for {self.user.email} at {self.embarkation_port}"
