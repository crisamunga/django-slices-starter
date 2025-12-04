from unittest.mock import Mock

import ninja.errors
import pytest
from django.http import HttpRequest
from django.utils.translation import gettext as _

import lib.errors
from lib import jsonutils as json

from .. import resources
from ..error_handlers import (
    error_group,
    invalid_input,
    standard_error,
    unexpected_error,
)


@pytest.fixture
def mock_request() -> HttpRequest:
    request = Mock(spec=HttpRequest)
    request.user = Mock()
    return request


base_error_scenarios = {
    "unauthenticated_error": (lib.errors.UnauthenticatedError(message="Custom unauthenticated message."), 401),
    "authorization_error": (
        lib.errors.AuthorizationError("Authorization failed", message="A custom auth message."),
        403,
    ),
    "user_error": (lib.errors.UserError("User error occurred", message="A user error occurred."), 400),
    "input_error": (lib.errors.InputError("Input error occurred", message="field_name", path=["field_name"]), 422),
    "not_found_error": (lib.errors.NotFoundError("Resource not found", message="Resource missing."), 404),
}


@pytest.mark.parametrize(("exc", "code"), base_error_scenarios.values(), ids=base_error_scenarios.keys())
def test_base_errors(mock_request: HttpRequest, exc: lib.errors.BaseError, code: int) -> None:
    response = standard_error(mock_request, exc)
    assert response.status_code == code
    assert json.loads(response.content) == resources.ErrorResponse(
        errors=[
            resources.ErrorMessage(
                code=exc.code,
                message=exc.message,
                path=getattr(exc, "path", None),
            )
        ],
    ).model_dump(mode="json", exclude_none=True)


def test_unexpected_error(mock_request: HttpRequest) -> None:
    exc = Exception("Unexpected error")
    response = unexpected_error(mock_request, exc)
    assert response.status_code == 500
    assert json.loads(response.content) == resources.ErrorResponse(
        errors=[
            resources.ErrorMessage(
                code="internal_error",
                message=_("An unexpected error occurred."),
                path=None,
            )
        ]
    ).model_dump(mode="json", exclude_none=True)


def test_invalid_input(mock_request: HttpRequest) -> None:
    error_detail = {"type": "type_error", "msg": "Invalid input", "loc": ["field"]}
    exc = ninja.errors.ValidationError([error_detail])
    response = invalid_input(mock_request, exc)
    assert response.status_code == 422
    expected_errors = [
        resources.ErrorMessage(code=error_detail["type"], message=error_detail["msg"], path=error_detail["loc"])  # type: ignore
    ]
    assert json.loads(response.content) == resources.ErrorResponse(errors=expected_errors).model_dump(
        mode="json", exclude_none=True
    )


def test_error_group(mock_request: HttpRequest) -> None:
    exc1 = lib.errors.InputError("First input error", message="First error message", path=["field1"])
    exc2 = lib.errors.InputError("Second input error", message="Second error message", path=["field2"])
    error_group_exc = ExceptionGroup("Multiple input errors", [exc1, exc2])

    response = error_group(mock_request, error_group_exc)
    assert response.status_code == 422
    expected_errors = [
        resources.ErrorMessage(code=exc1.code, message=exc1.message, path=exc1.path),
        resources.ErrorMessage(code=exc2.code, message=exc2.message, path=exc2.path),
    ]
    assert json.loads(response.content) == resources.ErrorResponse(errors=expected_errors).model_dump(
        mode="json", exclude_none=True
    )
