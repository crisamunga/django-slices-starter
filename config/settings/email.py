# ------------------------------------------------------------------------------------------------
# EMAIL SETTINGS
#
# Environment variables used:
#   EMAIL_HOST          - SMTP server host
#   EMAIL_HOST_PASSWORD - SMTP server password
#   EMAIL_HOST_USER     - SMTP server username
#   EMAIL_PORT          - SMTP server port
#   EMAIL_SENDER        - Default sender email address
#   EMAIL_TIMEOUT       - Timeout for SMTP connection in seconds
#   EMAIL_USE_TLS       - Enable TLS for SMTP connection ('True' or 'False')
# ------------------------------------------------------------------------------------------------

import os

from .deployment import APP_DOMAIN, TESTING

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

if TESTING:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "1025"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False") == "True"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "5"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER", f"no-reply@{APP_DOMAIN}")

__all__ = [
    "EMAIL_BACKEND",
    "EMAIL_HOST",
    "EMAIL_HOST_PASSWORD",
    "EMAIL_HOST_USER",
    "EMAIL_PORT",
    "EMAIL_SENDER",
    "EMAIL_TIMEOUT",
    "EMAIL_USE_TLS",
]
