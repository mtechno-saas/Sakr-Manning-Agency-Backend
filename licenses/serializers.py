from rest_framework import serializers
from .models import UserLicense, DOCUMENT_NAME_CHOICES
from api.serializers import CaseInsensitiveChoiceField, FlexibleDateField

class UserLicenseSerializer(serializers.ModelSerializer):
    document_name = CaseInsensitiveChoiceField(choices=DOCUMENT_NAME_CHOICES, required=False, allow_blank=True, allow_null=True)
    issue_date = FlexibleDateField(required=False, allow_null=True)
    expiration_date = FlexibleDateField(required=False, allow_null=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = UserLicense
        fields = [
            'id', 'user', 'document_name', 'document_number', 
            'country_of_issue', 'issue_date', 'expiration_date', 
            'document_file', 'download_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'download_url', 'created_at', 'updated_at']

    def get_download_url(self, obj):
        if getattr(obj, 'document_file', None) and getattr(obj, 'user', None):
            path = f"/api/users/{obj.user.id}/download-license/{obj.id}/"
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.document_file and instance.user:
            ret['document_file'] = self.get_download_url(instance)
        return ret