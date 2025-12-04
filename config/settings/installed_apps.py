# ------------------------------------------------------------------------------------------------
# INSTALLED APPS SETTINGS
# ------------------------------------------------------------------------------------------------

from .deployment import DEBUG, TESTING

INSTALLED_APPS = [
    "daphne",
    # -------------------------------------------------
    # Project apps
    # -------------------------------------------------
    "core",
    "tools",
    # -------------------------------------------------
    # Django apps
    # -------------------------------------------------
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # "django.contrib.messages", - Messages framework is not used
    "django.contrib.staticfiles",
    # -------------------------------------------------
    # 3rd party apps
    # -------------------------------------------------
    "django_typer",
    # -------------------------------------------------
    # Allauth apps
    # -------------------------------------------------
    "allauth",
    "allauth.account",
    # "allauth.socialaccount",  # if using social auth
    "allauth.headless",  # if using backend as api only
    "allauth.mfa",  # if using multi-factor authentication
]


if DEBUG and not TESTING:
    INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar"]

__all__ = ["INSTALLED_APPS"]
