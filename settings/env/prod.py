from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

from settings.base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS: list[str] = config("ROOMLY_ALLOWED_HOSTS", cast=Csv())

if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ROOMLY_ALLOWED_HOSTS must list explicit production hosts.",
    )

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("ROOMLY_POSTGRES_DB", cast=str),
        "USER": config("ROOMLY_POSTGRES_USER", cast=str),
        "PASSWORD": config("ROOMLY_POSTGRES_PASSWORD", cast=str),
        "HOST": config("ROOMLY_POSTGRES_HOST", cast=str),
        "PORT": config("ROOMLY_POSTGRES_PORT", cast=int),
    },
}
