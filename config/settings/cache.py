# ------------------------------------------------------------------------------------------------
# CACHE SETTINGS
#
# Environment variables used:
#   CACHE_URL           - Url for the cache backend (e.g., redis://<host>:<port>)
# ------------------------------------------------------------------------------------------------

import os

from .deployment import TESTING

# Cache configuration
# https://docs.djangoproject.com/en/5.2/topics/cache

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("CACHE_URL"),
    }
}

if TESTING:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests",
        }
    }

__all__ = ["CACHES"]
