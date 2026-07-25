"""Serializers for the Reminders app."""
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Reminder

User = get_user_model()


class UserFlexiblePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    A PrimaryKeyRelatedField for the User model that accepts BOTH:

    - Integer id            → 42
    - Stringified integer id → "42"

    on write. On read, it still returns the integer id (the standard
    ForeignKey representation). The frontend never needs to convert
    "42" → 42 manually.

    Email and username lookups are NOT supported by this field — the
    frontend's "Crew Member" dropdown already knows the id it picked.
    If you need email/username lookup later, add a custom resolver.
    """

    def to_internal_value(self, data):
        # If the frontend sent the id as a string (e.g. from a form value),
        # convert to int so the standard pk lookup works.
        if isinstance(data, str) and data.isdigit():
            data = int(data)
        return super().to_internal_value(data)


class ReminderSerializer(serializers.ModelSerializer):
    """Full serializer for the Reminder model."""

    # Use the flexible field so the form can submit either 42 or "42".
    user = UserFlexiblePrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
    )

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
        if obj.is_completed:
            return False
        now = timezone.localtime()
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
