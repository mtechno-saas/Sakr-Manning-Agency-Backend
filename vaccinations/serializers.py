from rest_framework import serializers
from .models import Vaccination

class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

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
