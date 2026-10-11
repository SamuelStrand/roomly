from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """Configure the bookings application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bookings'
    verbose_name = "Bookings"
