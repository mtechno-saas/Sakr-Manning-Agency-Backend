"""
api/google_user_service.py

Responsibility: Map a verified Google OAuth payload to a local Users record.
No token verification, no JWT minting — only DB read/write.
"""

from typing import Tuple

from .models import Users


class GoogleUserService:
    """
    Stateless service that resolves a Google OAuth payload to a local user.

    Usage::

        user, created = GoogleUserService.get_or_create_user_from_google(payload)
    """

    @staticmethod
    def get_or_create_user_from_google(google_payload: dict) -> Tuple[Users, bool]:
        """
        Find or create a Users record from a verified Google ID-token payload.

        Rules
        -----
        - New users receive role='Employee', is_active=True, and an unusable
          password (Google is their only authentication method unless an admin
          later sets a password explicitly).
        - Existing users are returned *as-is* — no fields are overwritten.
          This preserves any role promotions or profile edits made by admins.

        Parameters
        ----------
        google_payload : dict
            The decoded, verified payload returned by
            ``google.oauth2.id_token.verify_oauth2_token``.

        Returns
        -------
        (user, created) : tuple[Users, bool]
            ``created`` is True when a brand-new account was just created.
        """
        email: str = google_payload["email"]
        first_name: str = (
            google_payload.get("given_name")
            or google_payload.get("name", "").split(" ")[0]
            or "User"
        )
        middle_name: str = google_payload.get("family_name", "")

        user, created = Users.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "middle_name": middle_name,
                "role": "Employee",
                "is_active": True,
            },
        )

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        return user, created
