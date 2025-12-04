import pytest
from django.test import Client
from django.urls import reverse

from core.auth.tests.factories import UserFactory


@pytest.mark.django_db
def test_get_profile_authenticated() -> None:
    # Arrange
    user = UserFactory.create()
    client = Client()
    client.force_login(user)
    url = reverse("api:profile-read")

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == str(user.uuid)
    assert data["full_name"] == user.full_name
    assert data["email"] == user.email


@pytest.mark.django_db
def test_get_profile_unauthenticated() -> None:
    # Arrange
    client = Client()
    url = reverse("api:profile-read")

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 401
