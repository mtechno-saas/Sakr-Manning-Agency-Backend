"""
Credential provisioning for staff accounts.

The problem
-----------
The dashboard's add-user form has no password field, so an account
created there starts life with **no password at all**. When an admin
later promotes that applicant to a staff role (Admin / HR Manager /
Recruiter), the promotion used to hand out one shared, hard-coded
password -- ``admin123!`` -- to every staff account in the company.

That is a real hole:

  * no per-person accountability (an audit log cannot tell two people
    apart when they share a credential)
  * the value is in the repository's git history
  * it is a known password to anyone who has ever seen the repo

What this module does instead
-----------------------------
Whenever a staff account is created or promoted without an explicit
password, the system now:

  1. generates a random 8-digit password (``secrets``, not ``random``)
  2. sets it as the account's password
  3. emails it to the account holder

The plaintext password is transmitted by email only. It is never
returned in an API response, never written to a log line, and never
stored anywhere but the bcrypt hash on the user row.

The email goes through the existing pluggable email service
(:mod:`api.email`). In production that is
``api.email.DjangoSMTPEmailService`` -- real SMTP via Gmail. The
existing ``send_welcome_credentials_email`` method is reused: it already
sends a username + plain-text password message, and the subject line
("your account is ready") reads correctly for someone being given
dashboard access for the first time.

If the email cannot be sent, the password is STILL set -- the promotion
itself succeeded and the account must work -- but the failure is
reported to the caller (so the API can tell the admin) and recorded in
the audit trail. The recovery path is to PATCH the user with an
explicit password.
"""

from __future__ import annotations

import logging
import secrets

logger = logging.getLogger(__name__)

# Length of a generated staff password, in digits.
STAFF_PASSWORD_DIGITS = 8


def generate_staff_password(digits: int = STAFF_PASSWORD_DIGITS) -> str:
    """Return a random numeric password of exactly ``digits`` characters.

    Uses ``secrets.randbelow`` so the value is cryptographically
    unpredictable. A predictable "random" staff password is a backdoor,
    not a password.

    Leading zeros are preserved: ``generate_staff_password()`` always
    returns exactly 8 characters, e.g. ``"04183027"``.
    """
    upper = 10 ** digits
    return f"{secrets.randbelow(upper):0{digits}d}"


def email_staff_credentials(user, password: str, *, role: str = "") -> dict:
    """Email the generated password to the account holder.

    Never raises -- a mail problem must not roll back the promotion.

    :returns: ``{"email_sent": bool, "email": str, "role": str}`` --
        safe to hand to an API response, it never contains the password.
    """
    role = role or getattr(user, "role", "") or ""

    email_sent = False
    email_service = ""
    if not user or not user.email:
        logger.warning(
            "staff_credentials: cannot email credentials -- user id=%s "
            "has no email address",
            getattr(user, "id", None),
        )
    else:
        from api.email import get_email_service

        service = get_email_service()
        email_service = (
            f"{type(service).__module__}.{type(service).__name__}"
        )
        try:
            email_sent = bool(
                service.send_welcome_credentials_email(
                    to_email=user.email,
                    username=user.email,
                    password=password,
                    first_name=user.first_name or "",
                )
            )
        except Exception:
            logger.exception(
                "staff_credentials: email service raised for user id=%s",
                user.id,
            )

    if not email_sent:
        logger.error(
            "staff_credentials: the credentials email FAILED for user id=%s "
            "(%s). The account was given a new password that nobody "
            "knows -- set an explicit password on the account, or re-send "
            "the email.",
            getattr(user, "id", None),
            getattr(user, "email", ""),
        )
    elif email_service.endswith("ConsoleEmailService"):
        # The console backend reports success but only writes the message
        # to the server log -- nothing is actually delivered. Say so, or
        # the admin will believe the person got an email.
        logger.warning(
            "staff_credentials: EMAIL_SERVICE is the console backend "
            "(%s) -- the credentials for user id=%s were only written to "
            "the server log, NOT delivered to %s.",
            email_service,
            getattr(user, "id", None),
            getattr(user, "email", ""),
        )

    return {
        "email_sent": email_sent,
        "email": getattr(user, "email", "") or "",
        "role": role,
        "email_service": email_service,
    }
