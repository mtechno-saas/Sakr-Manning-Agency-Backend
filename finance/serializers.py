from rest_framework import serializers
from .models import FinanceRecord


class FinanceRecordSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()
    daily_rate = serializers.ReadOnlyField()
    total_money = serializers.ReadOnlyField()

    class Meta:
        model = FinanceRecord
        fields = "__all__"
