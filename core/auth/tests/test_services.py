import pytest
from asgiref.sync import async_to_sync

from lib.errors import AuthorizationError

from .. import services
from ..models import AnonymousUser
from .factories import UserFactory


@pytest.mark.django_db
def test_get_profile() -> None:
    user = UserFactory.create()
    result = async_to_sync(services.get_profile)(auth_user=user)
    assert result == user


@pytest.mark.django_db
def test_get_profile_anonymous_user() -> None:
    user = AnonymousUser()
    with pytest.raises(AuthorizationError):
        async_to_sync(services.get_profile)(auth_user=user)
