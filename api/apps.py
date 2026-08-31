from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Wire up the post_save signal that dedupes overlapping
        # SeaService rows. Importing the module registers the
        # receiver via the @receiver decorator.
        from . import signals  # noqa: F401
