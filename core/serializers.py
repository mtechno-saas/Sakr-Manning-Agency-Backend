# core/serializers.py
from rest_framework import serializers
from .models import Flag, VesselType, CompanyType

class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = ['id', 'name', 'icon']

class VesselTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VesselType
        fields = ['id', 'name']

class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ['id', 'name']
