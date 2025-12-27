from rest_framework import serializers
from .models import FlightBooking, VisaApplication, JoiningInstruction

class FlightBookingSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = FlightBooking
        fields = '__all__'

class VisaApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = VisaApplication
        fields = '__all__'

class JoiningInstructionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = JoiningInstruction
        fields = '__all__'
