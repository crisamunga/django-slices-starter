# ------------------------------------------------------------------------------------------------
# WEB SERVER / ROUTER SETTINGS
# ------------------------------------------------------------------------------------------------

APPEND_SLASH = True

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

__all__ = [
    "APPEND_SLASH",
    "ASGI_APPLICATION",
    "ROOT_URLCONF",
    "WSGI_APPLICATION",
]
