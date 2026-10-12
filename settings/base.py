import os

from django.urls import reverse_lazy

from settings.conf import *  # noqa: F403

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"
AUTH_USER_MODEL = "users.CustomUser"


DJANGO_AND_THIRD_PARTY_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = [
    "apps.abstracts.apps.AbstractsConfig",
    "apps.users.apps.UsersConfig",
    "apps.spaces.apps.SpacesConfig",
    "apps.bookings.apps.BookingsConfig",
    "apps.schedules.apps.SchedulesConfig",
    "apps.notifications.apps.NotificationsConfig",
]

INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Qyzylorda"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


UNFOLD = {
    "SITE_TITLE": "Roomly Admin",
    "SITE_HEADER": "Roomly",
    "SITE_SUBHEADER": "Room booking administration",
    "SITE_SYMBOL": "meeting_room",
    "SITE_URL": None,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": True,
    "BORDER_RADIUS": "8px",
    "COLORS": {
        "primary": {
            "50": "oklch(97% .014 254.604)",
            "100": "oklch(93.2% .032 255.585)",
            "200": "oklch(88.2% .059 254.128)",
            "300": "oklch(80.9% .105 251.813)",
            "400": "oklch(70.7% .165 254.624)",
            "500": "oklch(62.3% .214 259.815)",
            "600": "oklch(54.6% .245 262.881)",
            "700": "oklch(48.8% .243 264.376)",
            "800": "oklch(42.4% .199 265.638)",
            "900": "oklch(37.9% .146 265.522)",
            "950": "oklch(28.2% .091 267.935)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Roomly",
                "items": [
                    {
                        "title": "Overview",
                        "icon": "home",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Administration",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "group",
                        "link": reverse_lazy(
                            "admin:users_customuser_changelist",
                        ),
                        "permission": "apps.users.admin.can_view_users",
                    },
                    {
                        "title": "Groups",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": "apps.users.admin.can_view_groups",
                    },
                ],
            },
        ],
    },
}
