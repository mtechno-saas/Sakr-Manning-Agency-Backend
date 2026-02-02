# core/serializers.py
from rest_framework import serializers
from .models import Flag, VesselType

class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = ['id', 'name', 'icon']

class VesselTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VesselType
        fields = ['id', 'name']
