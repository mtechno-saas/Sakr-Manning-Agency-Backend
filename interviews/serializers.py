from rest_framework import serializers
from .models import Interview
from api.serializers import UserSerializer  # Assuming UserSerializer exists

# NOTE: ReminderSerializer was moved to the new `reminders` app on 2026-07-25.
# Use `from reminders.serializers import ReminderSerializer` if you need it.

class InterviewSerializer(serializers.ModelSerializer):
    candidate_details = UserSerializer(source='candidate', read_only=True)
    interviewer_details = UserSerializer(source='interviewer', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    interviewer_email = serializers.CharField(source='interviewer.email', read_only=True)

    class Meta:
        model = Interview
        fields = '__all__'
