from decouple import config
from django.core.exceptions import ImproperlyConfigured

LOCAL_ENV_ID = "local"
PROD_ENV_ID = "prod"
ENV_IDS = (LOCAL_ENV_ID, PROD_ENV_ID)

ENV_ID: str = config("ROOMLY_ENV_ID", cast=str)
SECRET_KEY: str = config("ROOMLY_SECRET_KEY", cast=str)

if ENV_ID not in ENV_IDS:
    raise ImproperlyConfigured(
        "ROOMLY_ENV_ID must be either 'local' or 'prod'.",
    )

if not SECRET_KEY.strip():
    raise ImproperlyConfigured("ROOMLY_SECRET_KEY must not be empty.")
