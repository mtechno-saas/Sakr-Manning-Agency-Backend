from rest_framework import serializers
from .models import Audit, IncidentReport

class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = '__all__'

class IncidentReportSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    ship_name = serializers.CharField(source='ship.ship_name', read_only=True)
    
    class Meta:
        model = IncidentReport
        fields = '__all__'
