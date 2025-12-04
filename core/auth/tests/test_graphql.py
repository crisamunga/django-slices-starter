import pytest
from django.test import Client

from core.auth.tests.factories import UserFactory

GRAPHQL_PATH = "/graphql/auth/"


@pytest.mark.django_db
def test_query_profile() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)
    response = client.post(
        GRAPHQL_PATH,
        data={
            "query": "{ profile { uuid email firstName lastName } }",
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "profile": {
                "uuid": str(user.uuid),
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
            }
        }
    }
