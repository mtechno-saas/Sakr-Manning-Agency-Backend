# ai_agents/serializers.py
from rest_framework import serializers
from ships.models import Ship
from api.models import Users

class ShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = [
            "id",
            "ship_name",
            "imo_number",
            "company",
            "ship_type",
            "flag",
            "official_no",
            "call_sign",
            "mmsi_no",
            "port_of_registry",
            "gross_tonnage",
            "deadweight",
            "year_built",
            "builder",
            "engine_type",
            "engine_power_kw",
            "status",
            "created_at",
            "updated_at",
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "nationality",
            "Place_Of_Birth",
            "passport_no",
            "passport_issue_date",
            "passport_expiry_date",
            "seaman_book_no",
            "seaman_book_issue_date",
            "seaman_book_expiry_date",
            "age",
            "date_of_birth",
        ]
