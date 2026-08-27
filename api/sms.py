"""SMS service abstraction for the seafarer phone-verification flow.

The system needs to send an OTP SMS to the seafarer's phone. Real
production deployments will plug in a real provider (Twilio, Vonage,
AWS SNS, MessageBird, etc.) by implementing the :class:`SMSService`
protocol and pointing the ``SMS_SERVICE`` Django setting at it.

For local development and tests, :class:`ConsoleSMSService` is the
default — it logs the OTP to the server console instead of actually
sending an SMS. The seafarer can't actually receive the OTP via SMS
in dev, so this is ONLY suitable for local work and automated tests
where the test code can read the log/captured output.

To plug in a real provider in production:

    1. Add the provider SDK to requirements.txt (e.g. ``twilio``).
    2. Subclass :class:`SMSService` and implement :meth:`send_otp` using
       the provider's API. Read credentials from environment variables.
    3. Set ``SMS_SERVICE = "your.module.YourSMSService"`` in
       ``saker/settings.py`` (or via env var).
    4. The seafarer's phone is passed in E.164 format
       (e.g. ``+201234567890``); format as needed for your provider.

The default backend in dev is intentionally a no-op for real SMS
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


class SMSService(Protocol):
    """Pluggable SMS provider.

    Implementations must accept the seafarer's phone number (in any
    format — prefer E.164 like ``+201234567890``) and the OTP code
    (a 6-digit numeric string), and deliver the message.
    """

    def send_otp(self, phone: str, otp: str, *, ttl_minutes: int = 10) -> bool:
        """Send ``otp`` to ``phone``. Returns True on success, False on
        any failure (network error, invalid number, etc.)."""
        ...


# ── Default dev backend: log to console ──────────────────────────────


class ConsoleSMSService:
    """Default backend for dev/test.

    Logs the OTP to the server console. Does NOT actually send an
    SMS — the seafarer cannot receive it via their phone. This is
    only useful for local development (where the developer reads
    the OTP from the server log) and for automated tests (which
    capture the log and assert on its contents).
    """

    def send_otp(self, phone: str, otp: str, *, ttl_minutes: int = 10) -> bool:
        logger.info(
            "[SMS-CONSOLE] Sending OTP to phone=%s | otp=%s | ttl=%d min",
            phone, otp, ttl_minutes,
        )
        return True


# ── Loader ───────────────────────────────────────────────────────────


def get_sms_service() -> SMSService:
    """Return the configured SMS service instance.

    The service class is looked up via ``settings.SMS_SERVICE``
    (default ``"api.sms.ConsoleSMSService"``) and instantiated
    with no arguments. Override ``SMS_SERVICE`` in production.
    """
    path = getattr(settings, "SMS_SERVICE", "api.sms.ConsoleSMSService")
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
