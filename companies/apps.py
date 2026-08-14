from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies'

    def ready(self):
        # Wire up signals (auto-transition JobOrder.status to
        # Fulfilled when all positions are fully filled).
        from . import signals  # noqa: F401
