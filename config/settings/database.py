# ------------------------------------------------------------------------------------------------
# DATABASE SETTINGS
#
# Environment variables used:
#   DB_NAME           - Name of the database
#   DB_USER           - Database username
#   DB_PASSWORD       - Database user password
#   DB_HOST           - Database host address
#   DB_PORT           - Database port
#   DB_SSL_MODE       - (Optional) SSL mode for database connection (e.g., 'require', 'disable')
#   DB_SSL_ROOT_CERT  - (Optional) Path to the SSL root certificate file
# ------------------------------------------------------------------------------------------------

import os

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


def _get_db_ssl_settings() -> dict[str, str]:
    ssl_mode = os.environ.get("DB_SSL_MODE")
    if not ssl_mode:
        return {}
    ssl_settings = {"sslmode": ssl_mode}
    ssl_root_cert = os.environ.get("DB_SSL_ROOT_CERT")
    if ssl_root_cert:
        ssl_settings["sslrootcert"] = ssl_root_cert
    return ssl_settings


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
        "OPTIONS": {
            **(_get_db_ssl_settings()),
        },
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

__all__ = ["DATABASES", "DEFAULT_AUTO_FIELD"]
