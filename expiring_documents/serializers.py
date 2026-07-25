"""Serializers for the Expiring Documents app."""
from rest_framework import serializers


class ExpiringDocumentItemSerializer(serializers.Serializer):
    """
    One row in the Expiring Documents list.
    Not bound to a single model — this is an aggregation of
    `Users` (9 expiry fields) + `PersonalDocument` (expiry_date column).
    """

    # Unique id for the row (e.g. "user_42_passport_expiry_date" or "pd_87")
    id = serializers.CharField(read_only=True)

    # Document info
    type = serializers.CharField(read_only=True)              # e.g. "Passport", "ABLE SEAFARER DECK"
    name = serializers.CharField(read_only=True)              # "{type} - {number}"
    number = serializers.CharField(read_only=True)            # document number or "N/A"

    # User info
    user = serializers.CharField(read_only=True)              # full name (first + middle)
    userId = serializers.IntegerField(read_only=True)
    userEmail = serializers.EmailField(read_only=True)
    userPosition = serializers.CharField(read_only=True, allow_null=True)  # e.g. "Able Seaman"

    # Expiry
    expiryDate = serializers.DateField(read_only=True)
    daysToExpiry = serializers.IntegerField(read_only=True)
    category = serializers.CharField(read_only=True)         # expired | critical | warning | notice | active

    # Provenance
    source = serializers.CharField(read_only=True)           # user_profile | personal_document


class ExpiringDocumentsCountsSerializer(serializers.Serializer):
    """Counts of items per category, plus total."""
    expired = serializers.IntegerField()
    critical = serializers.IntegerField()
    warning = serializers.IntegerField()
    notice = serializers.IntegerField()
    active = serializers.IntegerField()
    total = serializers.IntegerField()


class ExpiringDocumentsResponseSerializer(serializers.Serializer):
    """Top-level response wrapper."""
    counts = ExpiringDocumentsCountsSerializer()
    days_window = serializers.IntegerField()
    today = serializers.DateField()
    category_filter = serializers.CharField()
    results = ExpiringDocumentItemSerializer(many=True)
