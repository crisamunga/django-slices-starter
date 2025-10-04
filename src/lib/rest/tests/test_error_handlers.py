from unittest.mock import Mock

import ninja.errors
import pytest
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

import lib.errors
import lib.messages
from lib import jsonutils as json

from .. import resources
from ..error_handlers import (
    authorization_failed,
    invalid_input,
    not_authenticated,
    not_found,
    unexpected_error,
)


@pytest.fixture
def mock_request() -> HttpRequest:
    request = Mock(spec=HttpRequest)
    request.user = Mock()
    return request


def test_not_authenticated(mock_request: HttpRequest) -> None:
    exc = lib.errors.UnauthenticatedError()
    response = not_authenticated(mock_request, exc)
    assert response.status_code == 401
    assert json.loads(response.content) == resources.Response401(
        message=lib.messages.get_message(code="unauthenticated", message=_("You must sign in to perform this action."))
    ).model_dump(mode="json", exclude_none=True)


def test_authorization_failed(mock_request: HttpRequest) -> None:
    exc = lib.errors.AuthorizationError("Authorization failed")
    response = authorization_failed(mock_request, exc)
    assert response.status_code == 403
    assert json.loads(response.content) == resources.Response403(
        message=lib.messages.get_message(
            code="unauthorized", message=_("You don't have permission to perform this action.")
        )
    ).model_dump(mode="json", exclude_none=True)


def test_unexpected_error(mock_request: HttpRequest) -> None:
    exc = Exception("Unexpected error")
    response = unexpected_error(mock_request, exc)
    assert response.status_code == 500
    assert json.loads(response.content) == resources.Response500(
        message=lib.messages.get_message(code="unexpected_error", message=_("An unexpected error occurred."))
    ).model_dump(mode="json", exclude_none=True)


def test_invalid_input(mock_request: HttpRequest) -> None:
    error_detail = {"type": "type_error", "msg": "Invalid input", "loc": ["field"]}
    exc = ninja.errors.ValidationError([error_detail])
    response = invalid_input(mock_request, exc)
    assert response.status_code == 422
    expected_errors = [
        resources.ErrorDetail(code=error_detail["type"], message=error_detail["msg"], path=error_detail["loc"])  # type: ignore
    ]
    assert json.loads(response.content) == resources.Response422(
        message=lib.messages.get_message(code="invalid_input", message=_("Invalid input.")), errors=expected_errors
    ).model_dump(mode="json", exclude_none=True)


def test_not_found(mock_request: HttpRequest) -> None:
    exc = lib.errors.NotFoundError("Not found")
    response = not_found(mock_request, exc)
    assert response.status_code == 404
    assert json.loads(response.content) == resources.Response404(
        message=lib.messages.get_message(code="not_found", message=_("The requested resource was not found."))
    ).model_dump(mode="json", exclude_none=True)
