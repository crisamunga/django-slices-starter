from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


def support_contact(request: HttpRequest) -> dict[str, str | None]:  # noqa: ARG001 - context processor requires this arg
    return {
        "support_email": settings.SUPPORT_EMAIL,
        "support_phone": settings.SUPPORT_PHONE,
        "support_message": _("For assistance, please contact support. Email: {email}, Phone: {phone}").format(
            email=settings.SUPPORT_EMAIL,
            phone=settings.SUPPORT_PHONE,
        ),
    }


def app_info(request: HttpRequest) -> dict[str, str]:  # noqa: ARG001 - context processor requires this arg
    return {
        "app_domain": settings.APP_DOMAIN,
        "app_frontend_url": settings.APP_FRONTEND_URL,
        "app_id": settings.APP_ID,
        "app_name": settings.APP_NAME,
        "app_scheme": settings.APP_SCHEME,
    }


def auth_info(request: HttpRequest) -> dict[str, str | int]:  # noqa: ARG001 - context processor requires this arg
    return {
        "auth_signup_timeout": (settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT) // 60,  # in minutes
        "auth_login_timeout": (settings.ACCOUNT_LOGIN_BY_CODE_TIMEOUT) // 60,  # in minutes
        "auth_password_reset_timeout": (settings.ACCOUNT_PASSWORD_RESET_BY_CODE_TIMEOUT) // 60,  # in minutes
    }
