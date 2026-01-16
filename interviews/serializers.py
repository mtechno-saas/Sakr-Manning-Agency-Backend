from rest_framework import serializers
from .models import Interview
from api.serializers import UserSerializer  # Assuming UserSerializer exists

class InterviewSerializer(serializers.ModelSerializer):
    candidate_details = UserSerializer(source='candidate', read_only=True)
    interviewer_details = UserSerializer(source='interviewer', read_only=True)

    class Meta:
        model = Interview
        fields = '__all__'
