# Testing Guidelines

- Use `pytest` for writing tests.
- Use `async_to_sync` from `asgiref.sync` to call async functions in tests.
- Use fixtures to set up any necessary test data or state.
- Use parametrization to test multiple scenarios for the same function.
- Account for common edge cases like empty inputs, invalid data types, and boundary values. Include comments on expected behavior for each test case.
- Organize tests in arrange, act, assert format for clarity.
- Tests are placed at the module level within the `tests` package of each slice, they don't need to be inside a class unless using fixtures that require it.

## Factories

- Use `Factory Boy` to create test data.
- Define factories in a `factories.py` file within the slice's `tests` package.
- Use the factories to create instances of models for testing.
- Factories should have sensible default values for all fields, but allow overriding them when needed.
- Use `factory_fake` from `lib.tests` to generate realistic fake data for fields. This is a helper that wraps `Faker` library for use in factories.

**Example:**

```python
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

```

## Rest API Testing Guidelines

- Tests for the REST API endpoints should be defined in a `tests` package within the slice directory, e.g., `core/<slice>/tests/`. The files should match the structure of the rest api files with a `test_` prefix, e.g., `test_rest.py`.
- Django test client should be used to simulate HTTP requests to the endpoints.

**Example:**

```python
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
```

## GraphQL API Testing Guidelines

- Tests for the GraphQL API endpoints should be defined in a `tests` package within the slice directory, e.g., `core/<slice>/tests/`. The files should match the structure of the graphql files with a `test_` prefix, e.g., `test_graphql.py`.
- Use the Django test client to simulate HTTP requests to the GraphQL endpoints.
- Define a `GRAPHQL_PATH` constant for the endpoint path to be used in tests.
-

**Example:**

```python
import pytest
from django.test import Client

from core.auth.tests.factories import UserFactory

GRAPHQL_PATH = "/graphql/core/auth/"


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
```
