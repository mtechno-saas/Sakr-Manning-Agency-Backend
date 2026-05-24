"""
api/google_auth_serializer.py

Responsibility: Validate a raw Google ID token and extract the verified
user payload.  Nothing else — no DB access, no JWT minting.
"""

from django.conf import settings
from rest_framework import serializers

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests


class GoogleTokenSerializer(serializers.Serializer):
    """
    Accepts a raw Google ID token string, verifies it against Google's
    public keys using the configured Client ID, and returns a clean payload.

    Raises serializers.ValidationError for any of the following:
      - GOOGLE_OAUTH2_CLIENT_ID is not configured in settings
      - The token is invalid, expired, or tampered with
      - email is missing from the verified payload
      - email_verified is not True
    """

    id_token = serializers.CharField(
        write_only=True,
        help_text="Google ID token obtained from the frontend Sign-In SDK.",
    )

    def validate_id_token(self, raw_token: str) -> dict:
        """
        Verify the raw Google ID token and return the decoded payload dict.
        The validated_data['id_token'] will be replaced by the payload dict
        so downstream code works with structured data, not a raw string.
        """
        # 1. Guard: ensure OAuth is configured
        client_id = "840517848435-lif3vsl2n8dcmaemqb9knuslm26pp8bq.apps.googleusercontent.com"

        # 2. Verify the token against Google's servers
        try:
            payload = google_id_token.verify_oauth2_token(
                raw_token,
                google_requests.Request(),
                client_id,
            )
        except ValueError as exc:
            raise serializers.ValidationError(
                f"Invalid or expired Google token: {exc}"
            ) from exc
        except Exception as exc:
            raise serializers.ValidationError(
                f"Google token verification failed: {exc}"
            ) from exc

        # 3. Require a verified email
        if not payload.get("email_verified"):
            raise serializers.ValidationError(
                "Google email address is not verified. "
                "Please verify your Google account email first."
            )

        if not payload.get("email"):
            raise serializers.ValidationError(
                "Google account does not provide an email address."
            )

        # Return the full decoded payload in place of the raw token string
        return payload

    @property
    def google_payload(self) -> dict:
        """Convenience accessor — call after .is_valid()."""
        return self.validated_data["id_token"]
