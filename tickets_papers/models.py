from django.db import models
from api.models import Users

class Ticket(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="tickets")
    ticket_number = models.CharField(max_length=100)
    file = models.FileField(upload_to="tickets/")
    created_at = models.DateTimeField(auto_now_add=True)



class TravelingPaper(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="traveling_papers")
    title = models.CharField(max_length=255)
    issued_date = models.DateField()
    file = models.FileField(upload_to="traveling_papers/")
    created_at = models.DateTimeField(auto_now_add=True)

