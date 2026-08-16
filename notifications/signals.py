"""
Signal wiring for the notifications app.

- ``Reminder`` post_save → email the admin who set it.
- ``PersonalDocument`` post_save → email the admin who uploaded it.

Both handlers are best-effort: any failure inside the email service
is logged but never propagated. Signals run after the database
commit, so even an exception in the handler cannot corrupt the
underlying write.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import PersonalDocument
from reminders.models import Reminder

from . import services

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Reminder)
def reminder_post_save(sender, instance, created, **kwargs):
    """
    Notify the admin whenever a new Reminder is created.

    Updates (``created=False``) do NOT send — the admin just modified
    something they already own; that's not news.
    """
    if not created:
        return
    try:
        services.send_reminder_notification(instance)
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "notifications: unexpected error handling Reminder post_save "
            "(id=%s): %s",
            getattr(instance, "id", None),
            exc,
        )


@receiver(post_save, sender=PersonalDocument)
def personal_document_post_save(sender, instance, created, **kwargs):
    """
    Notify the admin whenever a new PersonalDocument is uploaded.

    Like reminders, updates are silent — the admin already knows the
    doc exists, no need to ping them every time the expiry is bumped.
    """
    if not created:
        return
    try:
        services.send_expiring_document_notification(instance)
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "notifications: unexpected error handling PersonalDocument "
            "post_save (id=%s): %s",
            getattr(instance, "id", None),
            exc,
        )
