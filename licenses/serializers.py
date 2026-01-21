from rest_framework import serializers
from .models import UserLicense

class UserLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLicense
        fields = [
            'id', 'user', 'document_name', 'document_number', 
            'country_of_issue', 'issue_date', 'expiration_date', 
            'document_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']