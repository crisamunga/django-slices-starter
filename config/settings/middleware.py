# ------------------------------------------------------------------------------------------------
# MIDDLEWARE SETTINGS
# ------------------------------------------------------------------------------------------------

from .deployment import DEBUG, TESTING

MIDDLEWARE = [
    # -------------------------------------------------
    # Initial middleware
    # -------------------------------------------------
    # -------------------------------------------------
    # Django middleware
    # -------------------------------------------------
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # -------------------------------------------------
    # Third party middleware
    # -------------------------------------------------
    "allauth.account.middleware.AccountMiddleware",
    # -------------------------------------------------
    # Final middleware
    # -------------------------------------------------
    "lib.monitoring.middleware.TelemetryMiddleware",
]

if DEBUG and not TESTING:
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", *MIDDLEWARE]

__all__ = ["MIDDLEWARE"]
