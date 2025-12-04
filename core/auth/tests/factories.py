from time import time

from allauth.mfa.totp.internal.auth import format_hotp_value, hotp_value
from django.conf import settings
from factory.django import DjangoModelFactory

from lib.tests import factory_fake as fake

from ..models import User


class UserFactory(DjangoModelFactory[User]):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = fake("email")
    first_name = fake("first_name")
    last_name = fake("last_name")
    is_active = True


def generate_totp(*, secret: str) -> str:
    counter = int(time() // settings.MFA_TOTP_PERIOD)
    value = hotp_value(secret, counter)
    return format_hotp_value(value)  # type: ignore # allauth methods not typed
