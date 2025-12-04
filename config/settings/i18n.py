# ------------------------------------------------------------------------------------------------
# I18N, L10N, T9N SETTINGSs

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
# ------------------------------------------------------------------------------------------------

from .deployment import BASE_DIR

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("fr", "French"),
    ("ar", "Arabic"),
    # add others as needed
]

LOCALE_PATHS = [
    str(BASE_DIR / "locale"),
]

__all__ = [
    "LANGUAGES",
    "LANGUAGE_CODE",
    "LOCALE_PATHS",
    "TIME_ZONE",
    "USE_I18N",
    "USE_TZ",
]
