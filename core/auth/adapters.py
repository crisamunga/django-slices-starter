import logging
from dataclasses import dataclass

from allauth.account.adapter import DefaultAccountAdapter
from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.mfa.adapter import DefaultMFAAdapter
from django.http import HttpRequest

from core.models import User

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    uuid: str
    email: str
    first_name: str
    last_name: str
    is_active: bool


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        # Custom logic to determine if signup is allowed
        return True

    # Additional overrides can be added here as needed
    # Refer to: https://docs.allauth.org/en/dev/account/adapter.html


class HeadlessAdapter(DefaultHeadlessAdapter):
    def user_as_dataclass(self, user: User) -> UserData:
        return UserData(
            uuid=str(user.uuid),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
        )

    # Additional overrides can be added here as needed
    # Refer to: https://docs.allauth.org/en/dev/headless/adapter.html


class MFAAdapter(DefaultMFAAdapter):
    def get_totp_label(self, user: User) -> str:
        return user.full_name  # type: ignore # mypy not typing generic db field

    # Additional overrides can be added here as needed
    # Refer to: https://docs.allauth.org/en/dev/mfa/adapter.html
