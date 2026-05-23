"""
api/jwt_token_service.py

Responsibility: Issue Simple-JWT refresh + access token pairs for a given user.
No user lookup, no Google calls — only token creation.
"""

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Users


class JWTTokenService:
    """
    Stateless service that wraps Simple-JWT token generation.

    Usage::

        tokens = JWTTokenService.get_tokens_for_user(user)
        # {'refresh': '...', 'access': '...'}
    """

    @staticmethod
    def get_tokens_for_user(user: Users) -> dict:
        """
        Generate a refresh/access token pair for *user*.

        The token lifetime is governed by ``SIMPLE_JWT`` in Django settings
        (currently 15 days for both access and refresh).

        Parameters
        ----------
        user : Users
            An active ``Users`` model instance.

        Returns
        -------
        dict
            ``{'refresh': str, 'access': str}``
        """
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
