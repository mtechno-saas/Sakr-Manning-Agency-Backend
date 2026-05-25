from rest_framework import serializers
from .models import Vaccination
from api.serializers import FlexibleDateField

class VaccinationSerializer(serializers.ModelSerializer):
    issue_date = FlexibleDateField(required=False, allow_null=True)
    expiry_date = FlexibleDateField(required=False, allow_null=True)
    first_date = FlexibleDateField(required=False, allow_null=True)
    last_date = FlexibleDateField(required=False, allow_null=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Vaccination
        fields = "__all__"
        read_only_fields = ("user", "download_url", "created_at", "updated_at")

    def get_download_url(self, obj):
        if getattr(obj, 'document', None) and getattr(obj, 'user', None):
            path = f"/api/users/{obj.user.id}/download-vaccination/{obj.id}/"
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.document and instance.user:
            ret['document'] = self.get_download_url(instance)
        return ret

    def validate(self, data):
        issue = data.get("issue_date")
        expiry = data.get("expiry_date")
        first = data.get("first_date")
        last = data.get("last_date")

        if issue and expiry and expiry < issue:
            raise serializers.ValidationError("Expiry date must be after issue date.")

        if first and last and last < first:
            raise serializers.ValidationError("Last date must be after first date.")

        return data
