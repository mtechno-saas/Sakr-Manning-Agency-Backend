from rest_framework import serializers
from .models import *


class ManSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

