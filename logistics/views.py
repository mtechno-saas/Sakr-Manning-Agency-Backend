from rest_framework import viewsets
from .models import FlightBooking, VisaApplication, JoiningInstruction
from .serializers import FlightBookingSerializer, VisaApplicationSerializer, JoiningInstructionSerializer

from api.filters import FlightBookingFilter, VisaApplicationFilter

class FlightBookingViewSet(viewsets.ModelViewSet):
    queryset = FlightBooking.objects.all()
    serializer_class = FlightBookingSerializer
    filterset_class = FlightBookingFilter

class VisaApplicationViewSet(viewsets.ModelViewSet):
    queryset = VisaApplication.objects.all()
    serializer_class = VisaApplicationSerializer
    filterset_class = VisaApplicationFilter

class JoiningInstructionViewSet(viewsets.ModelViewSet):
    queryset = JoiningInstruction.objects.all()
    serializer_class = JoiningInstructionSerializer
    filterset_fields = ['user']
