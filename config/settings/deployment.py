# ------------------------------------------------------------------------------------------------
# DEPLOYMENT SETTINGS
#   - Configures deployment environment and project metadata.
#   - This file can be safely be imported from any other settings file
#
# Environment variables used:
#   DEBUG               - Enable or disable debug mode ('True' or 'False')
#   ENVIRONMENT         - Deployment environment (e.g., 'development', 'staging', 'production')
#   APP_DOMAIN          - Domain name for the project (e.g., 'example.com')
#   APP_FRONTEND_URL    - URL of the frontend application
#   APP_ID              - Unique identifier for the project
#   APP_NAME            - Human-readable name for the project
#   APP_SCHEME          - URL scheme for the project ('http' or 'https')
#   SUPPORT_EMAIL       - Support contact email address
#   SUPPORT_PHONE       - Support contact phone number
#   SUPPORT_WEBSITE     - Support contact website URL
# ------------------------------------------------------------------------------------------------

import os
import sys
from pathlib import Path

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG") == "True"
TESTING = "test" in sys.argv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

APP_ID = os.environ.get("APP_ID", "django_slices_starter")
APP_NAME = os.environ.get("APP_NAME", "Django Slices Starter")
APP_DOMAIN = os.environ.get("APP_DOMAIN", "localhost:8000")
APP_SCHEME = os.environ.get("APP_SCHEME", "http")
APP_URL = f"{APP_SCHEME}://{APP_DOMAIN}"
APP_FRONTEND_URL = os.environ.get("APP_FRONTEND_URL", "http://localhost:3000")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", f"support@{APP_DOMAIN}")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE")
SUPPORT_WEBSITE = os.getenv("SUPPORT_WEBSITE")

__all__ = [
    "APP_DOMAIN",
    "APP_FRONTEND_URL",
    "APP_ID",
    "APP_NAME",
    "APP_SCHEME",
    "APP_URL",
    "BASE_DIR",
    "DEBUG",
    "ENVIRONMENT",
    "SUPPORT_EMAIL",
    "SUPPORT_PHONE",
    "SUPPORT_WEBSITE",
    "TESTING",
]
