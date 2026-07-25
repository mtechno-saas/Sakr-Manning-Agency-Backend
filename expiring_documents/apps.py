from django.apps import AppConfig


class ExpiringDocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expiring_documents'
    verbose_name = 'Expiring Documents'
