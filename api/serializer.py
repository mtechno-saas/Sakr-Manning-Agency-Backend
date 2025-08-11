from rest_framework import serializers
from .models import *


class ManSerializer(serializers.ModelSerializer):
    class Meta:
        model = Man
        fields = '__all__'

