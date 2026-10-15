from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    """Configure the schedules application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.schedules'
    verbose_name = "Schedules"
