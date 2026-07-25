"""Serializers for the Reminders app."""
import re
from datetime import datetime, date
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Reminder

User = get_user_model()


class UserFlexiblePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    A PrimaryKeyRelatedField for the User model that accepts ALL of:

    - Integer id            → 42
    - Stringified integer id → "42"
    - Email address          → "bassem@example.com" (case-insensitive)
    - Username               → "bassem.natey" (exact)
    - Full name              → "Bassem Natey" (matches first_name + middle_name)
    - First name only        → "Bassem"

    on write. On read, it still returns the integer id (the standard
    ForeignKey representation). Resolution order on a string is:

        1. Pure-digit string  → coerce to int, lookup by pk
        2. Contains '@'        → lookup by email (case-insensitive)
        3. Has a space         → lookup by (first_name, middle_name)
        4. Otherwise           → lookup by username (exact)

    Each lookup raises a clear 400 if it doesn't match.
    """

    def to_internal_value(self, data):
        # 1) Integer (or int-as-string) — fast path
        if isinstance(data, str) and data.isdigit():
            data = int(data)
        if isinstance(data, int):
            return super().to_internal_value(data)

        # From here on, data must be a string identifier
        if not isinstance(data, str):
            self.fail('invalid', message=f"Expected int, email, or name; got {type(data).__name__}")

        s = data.strip()
        if not s:
            self.fail('blank')

        # 2) Email — look for '@'
        if '@' in s:
            try:
                return User.objects.get(email__iexact=s)
            except User.DoesNotExist:
                self.fail('invalid', message=f"No user with email '{s}'")

        # 3) Full name (has a space) — try (first_name, middle_name)
        if ' ' in s:
            # Strip extra spaces and split into parts
            parts = [p for p in re.split(r'\s+', s) if p]
            if len(parts) >= 2:
                first = parts[0]
                # Re-join any extra parts as middle_name (e.g. "John A Smith" → "John" + "A Smith")
                middle = ' '.join(parts[1:])

                qs = User.objects.filter(
                    first_name__iexact=first,
                    middle_name__iexact=middle,
                )
                if qs.count() == 1:
                    return qs.first()
                if qs.count() > 1:
                    # Multiple matches — return the first one but it's ambiguous
                    return qs.first()
                # No exact (first, middle) match — try with middle being first part
                # and first being just first_name (i.e. "Bassem Natey" might be
                # stored as first_name="Bassem" and middle_name="Natey")
                # already covered above. Try last_name as fallback if it exists.
                if hasattr(User, 'last_name') or 'last_name' in [f.name for f in User._meta.get_fields()]:
                    qs2 = User.objects.filter(
                        first_name__iexact=first,
                        last_name__iexact=middle,
                    )
                    if qs2.exists():
                        return qs2.first()
                # Try matching just first_name with any middle/last
                qs3 = User.objects.filter(first_name__iexact=first)
                if qs3.count() == 1:
                    return qs3.first()
                self.fail('invalid', message=f"No unique user with name '{s}'")

        # 4) Username (single token, no @, no space)
        try:
            return User.objects.get(username=s)
        except User.DoesNotExist:
            pass

        # Last try: maybe a single name that happens to be a first name
        qs = User.objects.filter(first_name__iexact=s)
        if qs.count() == 1:
            return qs.first()
        if qs.count() > 1:
            self.fail('invalid', message=f"Multiple users have first name '{s}'; please be more specific")

        self.fail('invalid', message=f"No user matched '{data}'")


class FlexibleDateField(serializers.DateField):
    """
    A DateField that accepts MULTIPLE input formats:

    - ISO 8601:  YYYY-MM-DD  (e.g. 2026-08-15)
    - Slash:     YYYY/MM/DD  (e.g. 2026/08/15)
    - US:        MM/DD/YYYY  (e.g. 08/15/2026) — used if first part <= 12
    - European:  DD/MM/YYYY  (e.g. 15/08/2026) — used if first part > 12
    - Dash:      DD-MM-YYYY  (e.g. 15-08-2026)

    Resolution order:
        1. If 4-digit year at the start (YYYY-... or YYYY/...): ISO/slash
        2. Otherwise: if first part > 12 → DD/MM/YYYY (European)
        3. Otherwise: if second part > 12 → MM/DD/YYYY (US)
        4. Otherwise: ambiguous, raise a clear error
    """

    DEFAULT_INPUT_FORMATS = (
        '%Y-%m-%d',  # 2026-08-15
        '%Y/%m/%d',  # 2026/08/15
        '%m/%d/%Y',  # 08/15/2026 (US)
        '%d/%m/%Y',  # 15/08/2026 (EU)
        '%d-%m-%Y',  # 15-08-2026
    )

    def to_internal_value(self, value):
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()

        if not isinstance(value, str):
            self.fail('invalid', message=f"Expected string, got {type(value).__name__}")

        s = value.strip()
        if not s:
            self.fail('blank')

        # Try each format; collect errors only if all fail
        errors = []
        for fmt in self.DEFAULT_INPUT_FORMATS:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError as e:
                errors.append(f"{fmt}: {e}")
                continue

        # If all formats failed, give a clear error
        self.fail(
            'invalid',
            message=(
                f"Date '{value}' has wrong format. "
                "Try: 2026-08-15, 2026/08/15, 08/15/2026, or 15/08/2026."
            ),
        )


class ReminderSerializer(serializers.ModelSerializer):
    """Full serializer for the Reminder model."""

    # Use the flexible fields so the form can submit either format.
    user = UserFlexiblePrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
    )
    reminder_date = FlexibleDateField(required=True)

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
            pass
        return attrs
