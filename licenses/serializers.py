from rest_framework import serializers
from .models import UserLicense, DOCUMENT_NAME_CHOICES
from api.serializers import CaseInsensitiveChoiceField, FlexibleDateField

class UserLicenseSerializer(serializers.ModelSerializer):
    document_name = CaseInsensitiveChoiceField(choices=DOCUMENT_NAME_CHOICES, required=False, allow_blank=True, allow_null=True)
    issue_date = FlexibleDateField(required=False, allow_null=True)
    expiration_date = FlexibleDateField(required=False, allow_null=True)

    class Meta:
        model = UserLicense
        fields = [
            'id', 'user', 'document_name', 'document_number', 
            'country_of_issue', 'issue_date', 'expiration_date', 
            'document_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']