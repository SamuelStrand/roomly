from django.apps import AppConfig


class SpacesConfig(AppConfig):
    """Configure the spaces application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.spaces'
    verbose_name = "Spaces"
