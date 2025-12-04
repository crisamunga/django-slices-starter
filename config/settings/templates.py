# ------------------------------------------------------------------------------------------------
# TEMPLATE SETTINGS
# ------------------------------------------------------------------------------------------------

from .deployment import BASE_DIR

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.support_contact",
                "config.context_processors.app_info",
                "config.context_processors.auth_info",
            ],
        },
    },
]

__all__ = [
    "TEMPLATES",
]
