"""Email service abstraction for the seafarer phone-verification flow.

The system sends an OTP to the seafarer's email (on file from the CV)
when they need to verify ownership of the phone number. Real production
deployments will plug in a real provider (SMTP, SendGrid, Mailgun,
Postmark, AWS SES, etc.) by implementing the :class:`EmailService`
protocol and pointing the ``EMAIL_SERVICE`` Django setting at it.

Two backends ship in this module:

  * :class:`ConsoleEmailService` — the default for dev/test. Logs
    the would-be email to the server console instead of actually
    sending. The seafarer can't actually receive the email in dev,
    so this is ONLY suitable for local work and automated tests
    where the test code can read the log/captured output.

  * :class:`DjangoSMTPEmailService` — uses ``django.core.mail.send_mail``
    with the SMTP backend configured in ``saker/settings.py``
    (``EMAIL_HOST`` etc., currently Gmail SMTP). Fine for
    low-volume transactional mail; switch to SendGrid / SES /
    etc. when volume picks up. Enable with::

        EMAIL_SERVICE = "api.email.DjangoSMTPEmailService"

To plug in a real third-party provider (SendGrid, Mailgun, etc.):

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

    def send_set_password_link(
        self,
        to_email: str,
        link: str,
        *,
        ttl_hours: int = 24,
    ) -> bool:
        """Send a "click here to set your password" magic-link email.

        ``link`` is the full URL the seafarer clicks on (frontend
        set-password page with ``?uidb64=...&token=...`` query params).
        ``ttl_hours`` is included in the email body so the seafarer
        knows how long the link is valid. Returns True on success,
        False on any failure.
        """
        ...

    def send_welcome_credentials_email(
        self,
        to_email: str,
        username: str,
        password: str,
        *,
        first_name: str = "",
    ) -> bool:
        """Send a "your account is ready" email containing the
        username (email) and the default password (phone number)
        in plain text.

        SECURITY NOTE: this method embeds the password in the email
        body, which is the standard "do not do this" anti-pattern.
        It exists because the project explicitly chose that trade-off
        for the admin-onboarded seafarer flow (the seafarer already
        has the phone in hand; the alternative magic-link flow adds
        a step the Admin wanted to skip). Use the magic-link flow
        (``send_set_password_link``) for any case where the password
        must NOT be transmitted in plain text.

        Returns True on success, False on any failure.
        """
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

    def send_set_password_link(
        self,
        to_email: str,
        link: str,
        *,
        ttl_hours: int = 24,
    ) -> bool:
        logger.info(
            "[EMAIL-CONSOLE] To: %s | SET-PASSWORD link=%s | ttl=%d h",
            to_email, link, ttl_hours,
        )
        return True

    def send_welcome_credentials_email(
        self,
        to_email: str,
        username: str,
        password: str,
        *,
        first_name: str = "",
    ) -> bool:
        logger.info(
            "[EMAIL-CONSOLE] To: %s | WELCOME-CREDS username=%s password=%s",
            to_email, username, password,
        )
        return True


class DjangoSMTPEmailService:
    """Real-email backend for prod-like deployments.

    Uses ``django.core.mail.send_mail`` which dispatches via the SMTP
    backend configured in ``saker/settings.py`` (``EMAIL_HOST``,
    ``EMAIL_PORT``, ``EMAIL_USE_TLS``, ``EMAIL_HOST_USER``,
    ``EMAIL_HOST_PASSWORD``, ``DEFAULT_FROM_EMAIL``). On this project
    that's Gmail SMTP (mtechsaas@gmail.com) — fine for low-volume
    transactional mail; switch to SendGrid / Mailgun / SES when
    volume picks up.

    Returns ``True`` on success, ``False`` on any send failure
    (network error, auth failure, recipient rejected, etc.). The
    caller (RequestOTPView / _save_parser_output) treats ``False``
    as a non-fatal warning — the OTP is still on the User row and
    the seafarer can re-request or read it from the log.
    """

    def send_otp_email(
        self,
        to_email: str,
        otp: str,
        *,
        ttl_minutes: int = 10,
    ) -> bool:
        from django.core.mail import send_mail
        from django.conf import settings as dj_settings

        subject = f"Your Sakr Manning Agency verification code: {otp}"
        body = (
            f"Hello,\n\n"
            f"Your verification code is: {otp}\n\n"
            f"This code is valid for {ttl_minutes} minutes. "
            f"Enter it on the verification page to confirm your email "
            f"and unlock your account.\n\n"
            f"If you did not request this code, you can safely "
            f"ignore this email.\n\n"
            f"— Sakr Manning Agency"
        )
        from_email = getattr(
            dj_settings, "DEFAULT_FROM_EMAIL", "noreply@sakrshipping.com"
        )

        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            # send_mail returns the number of messages successfully sent.
            return sent == 1
        except Exception:
            logger.exception(
                "DjangoSMTPEmailService: send_mail failed for to_email=%s",
                to_email,
            )
            return False

    def send_set_password_link(
        self,
        to_email: str,
        link: str,
        *,
        ttl_hours: int = 24,
    ) -> bool:
        from django.core.mail import send_mail
        from django.conf import settings as dj_settings

        subject = "Welcome to Sakr Manning Agency — set your password"
        body = (
            f"Hello,\n\n"
            f"You've been added to Sakr Manning Agency. To access "
            f"your profile and manage your account, please set a "
            f"password by clicking the link below:\n\n"
            f"  {link}\n\n"
            f"This link is valid for {ttl_hours} hours. "
            f"After that, you'll need to request a new one.\n\n"
            f"If you did not expect this email, you can safely "
            f"ignore it.\n\n"
            f"— Sakr Manning Agency"
        )
        from_email = getattr(
            dj_settings, "DEFAULT_FROM_EMAIL", "noreply@sakrshipping.com"
        )

        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return sent == 1
        except Exception:
            logger.exception(
                "DjangoSMTPEmailService: send_set_password_link failed "
                "for to_email=%s",
                to_email,
            )
            return False

    def send_welcome_credentials_email(
        self,
        to_email: str,
        username: str,
        password: str,
        *,
        first_name: str = "",
    ) -> bool:
        from django.core.mail import send_mail
        from django.conf import settings as dj_settings

        greeting = f"Hello {first_name}," if first_name else "Hello,"
        subject = "Welcome to Sakr Manning Agency — your account is ready"
        body = (
            f"{greeting}\n\n"
            f"Your account on Sakr Manning Agency has been created. "
            f"Here are your login credentials:\n\n"
            f"  Username: {username}\n"
            f"  Password: {password}\n\n"
            f"You can log in at https://sakrshipping.com/login with "
            f"these credentials. We recommend changing your password "
            f"after your first login.\n\n"
            f"If you did not expect this email, please contact us.\n\n"
            f"— Sakr Manning Agency"
        )
        from_email = getattr(
            dj_settings, "DEFAULT_FROM_EMAIL", "noreply@sakrshipping.com"
        )

        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return sent == 1
        except Exception:
            logger.exception(
                "DjangoSMTPEmailService: send_welcome_credentials_email "
                "failed for to_email=%s",
                to_email,
            )
            return False


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
