from rest_framework import serializers , fields
from .models import *


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = RANKS
        fields = "__all__"



class Certificates_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CERTIFICATES
        fields = "__all__"


class ManSerializer(serializers.ModelSerializer):
    codes = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset=Rank.objects.all())

    class Meta:
        model = Users
        fields = '__all__'





    