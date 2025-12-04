# ------------------------------------------------------------------------------------------------
# SECURITY SETTINGS
#
# Environment variables used:
#   SECURITY_ALLOWED_HOSTS     - Comma-separated list of allowed hosts
#   SECURITY_SECRET_KEY        - Secret key for the Django application
# ------------------------------------------------------------------------------------------------


import os

from .deployment import ENVIRONMENT

SECRET_KEY = os.environ["SECURITY_SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("SECURITY_ALLOWED_HOSTS", "").split(",")

INTERNAL_IPS = []

if ENVIRONMENT == "dev":
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

__all__ = [
    "ALLOWED_HOSTS",
    "INTERNAL_IPS",
    "SECRET_KEY",
]
