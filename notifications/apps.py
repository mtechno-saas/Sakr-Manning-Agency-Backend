from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "Notifications"

    def ready(self):
        # Wire the post_save handlers. Imported here so app registry is
        # fully populated before the signals try to resolve models.
        from . import signals  # noqa: F401
