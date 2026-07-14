from rest_framework import serializers
from .models import Interview, Reminder
from api.serializers import UserSerializer  # Assuming UserSerializer exists

class InterviewSerializer(serializers.ModelSerializer):
    candidate_details = UserSerializer(source='candidate', read_only=True)
    interviewer_details = UserSerializer(source='interviewer', read_only=True)

    class Meta:
        model = Interview
        fields = '__all__'


class ReminderSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Reminder
        fields = '__all__'
        extra_kwargs = {
            'text': {'required': True, 'allow_blank': False},
            'reminder_date': {'required': True},
            'reminder_time': {'required': True},
            'user': {'required': True},
        }

    def get_user_name(self, obj):
        if not obj.user:
            return None
        full = obj.user.get_full_name() if hasattr(obj.user, 'get_full_name') else ''
        return full or getattr(obj.user, 'username', None) or getattr(obj.user, 'email', None)
