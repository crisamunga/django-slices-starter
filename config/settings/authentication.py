# ------------------------------------------------------------------------------------------------
# AUTHENTICATION SETTINGS
# ------------------------------------------------------------------------------------------------

from .deployment import APP_FRONTEND_URL, APP_NAME, DEBUG

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",  # Change this to custom backend
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "core.User"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "core.auth.validators.PasswordComplexityValidator",
    },
]

# Allauth settings
# https://docs.allauth.org/en/dev/account/configuration.html
ACCOUNT_EMAIL_SUBJECT_PREFIX = f"[{APP_NAME}] "
ACCOUNT_MAX_EMAIL_ADDRESSES = 3
ACCOUNT_ADAPTER = "core.auth.adapters.AccountAdapter"
ACCOUNT_USER_MODEL_USERNAME_FIELD: str | None = None
ACCOUNT_SIGNUP_FIELDS = ("email*", "first_name*", "last_name*", "password1*", "password2*")
ACCOUNT_LOGIN_METHODS = ("email",)
ACCOUNT_SIGNUP_FORM_CLASS = "core.auth.forms.SignupForm"

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND = True
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS = 3
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT = 1800  # 30 minutes

ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = True
ACCOUNT_PASSWORD_RESET_BY_CODE_TIMEOUT = 300  # 5 minutes

ACCOUNT_LOGIN_BY_CODE_TIMEOUT = 300  # 5 minutes

# Allauth headless settings
# https://docs.allauth.org/en/dev/headless/configuration.html

HEADLESS_ONLY = True
HEADLESS_ADAPTER = "core.auth.adapters.HeadlessAdapter"
HEADLESS_TOKEN_STRATEGY = "core.auth.token_strategy.TokenStrategy"  # noqa: S105 - This is not a hardcoded secret
HEADLESS_SERVE_SPECIFICATION = DEBUG
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": f"{APP_FRONTEND_URL}/account/verify-email/?token={{key}}",
    "account_reset_password": f"{APP_FRONTEND_URL}/account/password/reset",
    "account_reset_password_from_key": f"{APP_FRONTEND_URL}/account/password/reset/key/{{key}}",
    "account_signup": f"{APP_FRONTEND_URL}/account/signup",
    "socialaccount_login_error": f"{APP_FRONTEND_URL}/account/provider/callback",
}

# Allauth MFA settings
# https://docs.allauth.org/en/dev/mfa/configuration.html

MFA_ADAPTER = "core.auth.adapters.MFAAdapter"
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_PASSKEY_SIGNUP_ENABLED = False
MFA_RECOVERY_CODE_COUNT = 10
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_TOTP_ISSUER = APP_NAME
MFA_TOTP_TOLERANCE = 1
MFA_TOTP_PERIOD = 30
MFA_TRUST_ENABLED = True
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGINS = DEBUG

__all__ = [
    "ACCOUNT_ADAPTER",
    "ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS",
    "ACCOUNT_EMAIL_SUBJECT_PREFIX",
    "ACCOUNT_EMAIL_VERIFICATION",
    "ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED",
    "ACCOUNT_EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS",
    "ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT",
    "ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND",
    "ACCOUNT_LOGIN_BY_CODE_TIMEOUT",
    "ACCOUNT_LOGIN_METHODS",
    "ACCOUNT_MAX_EMAIL_ADDRESSES",
    "ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED",
    "ACCOUNT_PASSWORD_RESET_BY_CODE_TIMEOUT",
    "ACCOUNT_SIGNUP_FIELDS",
    "ACCOUNT_SIGNUP_FORM_CLASS",
    "ACCOUNT_USER_MODEL_USERNAME_FIELD",
    "AUTHENTICATION_BACKENDS",
    "AUTH_PASSWORD_VALIDATORS",
    "AUTH_USER_MODEL",
    "HEADLESS_ADAPTER",
    "HEADLESS_FRONTEND_URLS",
    "HEADLESS_ONLY",
    "HEADLESS_SERVE_SPECIFICATION",
    "HEADLESS_TOKEN_STRATEGY",
    "MFA_ADAPTER",
    "MFA_PASSKEY_LOGIN_ENABLED",
    "MFA_PASSKEY_SIGNUP_ENABLED",
    "MFA_RECOVERY_CODE_COUNT",
    "MFA_SUPPORTED_TYPES",
    "MFA_TOTP_ISSUER",
    "MFA_TOTP_PERIOD",
    "MFA_TOTP_TOLERANCE",
    "MFA_TRUST_ENABLED",
    "MFA_WEBAUTHN_ALLOW_INSECURE_ORIGINS",
]
