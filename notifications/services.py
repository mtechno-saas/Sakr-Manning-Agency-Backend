"""
Notification email service.

Public functions
----------------
- :func:`send_reminder_notification`  – email the admin who set a Reminder
- :func:`send_expiring_document_notification`  – email the admin who
  uploaded a PersonalDocument (or set a Users expiry field, when called
  directly)

All senders are best-effort: if the email fails for any reason we log
the failure and return False. The HTTP request that triggered the
write must NEVER fail because of a notification problem.
"""
import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from core.threadlocals import get_current_user

logger = logging.getLogger(__name__)

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _actor() -> Optional[User]:
    """
    Return the user who triggered the current request, or None.

    The ``CurrentUserMiddleware`` mirrors ``request.user`` into a
    thread-local. Signal handlers call this so the email body can
    say "Hi <actor name>, you set ..." for traceability.
    """
    actor = get_current_user()
    if actor is None or not getattr(actor, "is_authenticated", False):
        return None
    return actor


def _recipient_email() -> Optional[str]:
    """
    Return the address that should receive admin notifications.

    All admin notifications go to a single shared inbox (the
    ``NOTIFICATIONS_ADMIN_EMAIL`` setting, defaults to
    ``crew@sakrshipping.com``). This gives the team one place to
    monitor what was recorded, regardless of which admin/HR/Recruiter
    did the work. The actual actor is still recorded in the email body.
    """
    to = getattr(settings, "NOTIFICATIONS_ADMIN_EMAIL", None)
    if not to or not isinstance(to, str) or not to.strip():
        logger.warning(
            "notifications: NOTIFICATIONS_ADMIN_EMAIL is not set; "
            "no admin notification will be sent."
        )
        return None
    return to.strip()


def _send(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
) -> bool:
    """
    Send one multipart (text + optional HTML) email. Returns True on
    success, False on any failure. Never raises.
    """
    if not to_email:
        logger.warning(
            "notifications: refusing to send email with no recipient; subject=%r",
            subject,
        )
        return False
    try:
        from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL", "noreply@sakrshipping.com"
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=[to_email],
        )
        if html_body:
            msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as exc:  # noqa: BLE001  - intentional broad catch
        logger.exception(
            "notifications: failed to send email to %s (subject=%r): %s",
            to_email,
            subject,
            exc,
        )
        return False


def _admin_label(actor) -> str:
    """Best-effort human label for the actor (admin who triggered)."""
    if not actor:
        return "An admin"
    full = getattr(actor, "full_name", "") or ""
    if not full:
        first = getattr(actor, "first_name", "") or ""
        middle = getattr(actor, "middle_name", "") or ""
        full = f"{first} {middle}".strip()
    if full:
        return full
    return getattr(actor, "email", None) or getattr(actor, "username", None) or "An admin"


def _crew_label(user) -> str:
    """Best-effort human label for a crew member."""
    if not user:
        return "—"
    full = getattr(user, "full_name", "") or ""
    if not full:
        first = getattr(user, "first_name", "") or ""
        middle = getattr(user, "middle_name", "") or ""
        full = f"{first} {middle}".strip()
    if full:
        return full
    return getattr(user, "email", None) or getattr(user, "username", None) or f"user#{getattr(user, 'id', '?')}"


# ---------------------------------------------------------------------------
# Public senders
# ---------------------------------------------------------------------------


def send_reminder_notification(reminder) -> bool:
    """
    Email the shared admin inbox about a new ``reminder``.

    The recipient is the team's shared inbox
    (``settings.NOTIFICATIONS_ADMIN_EMAIL``) so the whole admin/HR team
    sees every reminder that gets set. The actual actor (the
    request user) is recorded in the email body ("Hi <actor>, you
    set ...") for traceability. The crew member the reminder is for
    is NOT emailed.
    """
    actor = _actor()
    to_email = _recipient_email()
    if not to_email:
        logger.info(
            "notifications: no NOTIFICATIONS_ADMIN_EMAIL; skipping "
            "reminder notification for Reminder id=%s",
            getattr(reminder, "id", None),
        )
        return False

    who = _crew_label(getattr(reminder, "user", None))
    when = reminder.reminder_date.strftime("%Y-%m-%d") if reminder.reminder_date else "—"
    at = reminder.reminder_time.strftime("%H:%M") if reminder.reminder_time else "—"
    text = (reminder.text or "").strip()
    snippet = (text[:80] + "…") if len(text) > 80 else text

    subject = f"New reminder set for {who} on {when}"
    text_body = (
        f"Hi {_admin_label(actor)},\n\n"
        f"You set a new reminder.\n\n"
        f"  For:   {who}\n"
        f"  Date:  {when}\n"
        f"  Time:  {at}\n"
        f"  Note:  {snippet or '(no note)'}\n"
        f"  ID:    {getattr(reminder, 'id', '?')}\n\n"
        f"— Sakr Manning Agency (automated notification)\n"
    )
    return _send(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
    )


def send_expiring_document_notification(doc) -> bool:
    """
    Email the shared admin inbox about a new ``doc`` (a PersonalDocument).

    Recipient is the team's shared inbox. The actor (request user)
    is recorded in the body.
    """
    actor = _actor()
    to_email = _recipient_email()
    if not to_email:
        logger.info(
            "notifications: no NOTIFICATIONS_ADMIN_EMAIL; skipping "
            "expiring-document notification for PersonalDocument id=%s",
            getattr(doc, "id", None),
        )
        return False

    who = _crew_label(getattr(doc, "user", None))
    doc_type = getattr(doc, "document_type", "—") or "—"
    doc_number = getattr(doc, "document_number", None) or "—"
    issue = (
        doc.issue_date.strftime("%Y-%m-%d")
        if getattr(doc, "issue_date", None)
        else "—"
    )
    expiry = (
        doc.expiry_date.strftime("%Y-%m-%d")
        if getattr(doc, "expiry_date", None)
        else "—"
    )
    country = getattr(doc, "issuing_country", None) or "—"

    subject = f"New expiring document recorded: {doc_type} for {who}"
    text_body = (
        f"Hi {_admin_label(actor)},\n\n"
        f"You recorded a new expiring document.\n\n"
        f"  Crew member:  {who}\n"
        f"  Document:     {doc_type}\n"
        f"  Number:       {doc_number}\n"
        f"  Issued:       {issue}\n"
        f"  Expires:      {expiry}\n"
        f"  Country:      {country}\n"
        f"  ID:           {getattr(doc, 'id', '?')}\n\n"
        f"— Sakr Manning Agency (automated notification)\n"
    )
    return _send(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
    )


# Tiny helper used by tests to assert the actor is set.
def _now_label() -> str:
    return timezone.now().strftime("%Y-%m-%d %H:%M:%S")
