from django.apps import AppConfig


class AbstractsConfig(AppConfig):
    """Configure the abstracts application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.abstracts'
    verbose_name = "Shared models"
