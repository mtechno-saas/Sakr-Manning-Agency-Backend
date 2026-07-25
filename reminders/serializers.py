"""Serializers for the Reminders app."""
from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    """Full serializer for the Reminder model."""

    # Read-only computed fields
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Reminder
        fields = [
            'id',
            'user',
            'user_name',
            'user_email',
            'text',
            'reminder_date',
            'reminder_time',
            'is_completed',
            'is_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'text': {'required': True, 'allow_blank': False},
            'reminder_date': {'required': True},
            'reminder_time': {'required': True},
            'user': {'required': True},
        }

    def get_user_name(self, obj):
        if not obj.user:
            return None
        full = (
            f"{getattr(obj.user, 'first_name', '')} {getattr(obj.user, 'middle_name', '')}"
            .strip()
        )
        if full:
            return full
        return getattr(obj.user, 'email', None) or getattr(obj.user, 'username', None)

    def get_is_overdue(self, obj):
        """True if the reminder is in the past AND not yet completed."""
        from django.utils import timezone
        if obj.is_completed:
            return False
        now = timezone.localtime()
        # Combine date+time into one datetime
        from datetime import datetime
        try:
            reminder_dt = datetime.combine(obj.reminder_date, obj.reminder_time)
            return reminder_dt < now
        except (TypeError, ValueError):
            return False

    def validate(self, attrs):
        """Cross-field validation."""
        # If both date and time are provided, ensure they form a sensible instant
        reminder_date = attrs.get('reminder_date') or getattr(self.instance, 'reminder_date', None)
        reminder_time = attrs.get('reminder_time') or getattr(self.instance, 'reminder_time', None)
        if reminder_date and reminder_time:
            # Optional: prevent saving reminders far in the past (configurable)
            # Keeping it lenient for now; uncomment to enforce:
            # from django.utils import timezone
            # from datetime import datetime
            # if datetime.combine(reminder_date, reminder_time) < timezone.now():
            #     raise serializers.ValidationError(
            #         "Cannot create a reminder in the past."
            #     )
            pass
        return attrs
