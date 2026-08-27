"""Email service abstraction for the seafarer phone-verification flow.

The system sends an OTP to the seafarer's email (on file from the CV)
when they need to verify ownership of the phone number. Real production
deployments will plug in a real provider (SMTP, SendGrid, Mailgun,
Postmark, AWS SES, etc.) by implementing the :class:`EmailService`
protocol and pointing the ``EMAIL_SERVICE`` Django setting at it.

For local development and tests, :class:`ConsoleEmailService` is the
default — it logs the would-be email to the server console instead
of actually sending. The seafarer can't actually receive the email
in dev, so this is ONLY suitable for local work and automated tests
where the test code can read the log/captured output.

To plug in a real provider in production:

    1. Add the provider SDK to requirements.txt (e.g. ``sendgrid``).
    2. Subclass :class:`EmailService` and implement
       :meth:`send_otp_email` using the provider's API. Read SMTP /
       API-key credentials from environment variables.
    3. Set ``EMAIL_SERVICE = "your.module.YourEmailService"`` in
       ``saker/settings.py`` (or via env var).
    4. The seafarer's email is passed in lowercase. Format the body
       using the OTP and the TTL.

The default backend in dev is intentionally a no-op for real email
sending — never use the console backend in production unless you
want OTPs in your server logs.
"""

from __future__ import annotations

import logging
import secrets
from typing import Protocol

from django.conf import settings
from django.utils.module_loading import import_string


logger = logging.getLogger(__name__)


# ── Abstract interface ──────────────────────────────────────────────


class EmailService(Protocol):
    """Pluggable email provider.

    Implementations must accept the seafarer's email address
    (lowercase, e.g. ``mohashehata1995@gmail.com``) and the OTP code
    (a 6-digit numeric string), and deliver the message.
    """

    def send_otp_email(
        self,
        to_email: str,
        otp: str,
        *,
        ttl_minutes: int = 10,
    ) -> bool:
        """Send an OTP email to ``to_email``. Returns True on success,
        False on any failure (network error, invalid address, etc.)."""
        ...


# ── Default dev backend: log to console ──────────────────────────────


class ConsoleEmailService:
    """Default backend for dev/test.

    Logs the would-be email to the server console. Does NOT actually
    send anything — the seafarer cannot receive the OTP. This is
    only useful for local development (where the developer reads
    the OTP from the server log) and for automated tests (which
    capture the log and assert on its contents).
    """

    def send_otp_email(
        self,
        to_email: str,
        otp: str,
        *,
        ttl_minutes: int = 10,
    ) -> bool:
        logger.info(
            "[EMAIL-CONSOLE] To: %s | OTP: %s | ttl=%d min",
            to_email, otp, ttl_minutes,
        )
        return True


# ── Loader ───────────────────────────────────────────────────────────


def get_email_service() -> EmailService:
    """Return the configured email service instance.

    The service class is looked up via ``settings.EMAIL_SERVICE``
    (default ``"api.email.ConsoleEmailService"``) and instantiated
    with no arguments. Override ``EMAIL_SERVICE`` in production.
    """
    path = getattr(settings, "EMAIL_SERVICE", "api.email.ConsoleEmailService")
    cls = import_string(path)
    return cls()


# ── Helpers ──────────────────────────────────────────────────────────


def generate_otp() -> str:
    """Return a 6-digit numeric OTP as a string.

    Uses ``secrets.randbelow`` for cryptographic randomness so the
    OTP is unpredictable. Leading zeros are preserved
    (``secrets.randbelow(1_000_000)`` can return 0).
    """
    return f"{secrets.randbelow(1_000_000):06d}"


def otp_default_ttl_minutes() -> int:
    """OTP time-to-live, in minutes. Configurable via
    ``settings.OTP_TTL_MINUTES`` (default 10)."""
    return int(getattr(settings, "OTP_TTL_MINUTES", 10))
