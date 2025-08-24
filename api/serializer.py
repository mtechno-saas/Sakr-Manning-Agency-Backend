from rest_framework import serializers , fields
from tickets_papers.models import Ticket, TravelingPaper
from .models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        #fields = ["id", "ticket_number", "file", "created_at"]
        fields = "__all__"

class TravelingPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelingPaper
        #fields = ["id", "title", "issued_date", "file", "created_at"]
        fields = "__all__"

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


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"


    