from typing import Any

import pytest
from asgiref.sync import async_to_sync

from core.models import AnonymousUser, User
from lib.errors import InputError, InputErrorGroup
from lib.messages import Message

from ..base import Input, ValidationRule, validate

MockMessage1 = Message(
    message="Value is invalid",
    code="invalid_value",
)

MockMessage2 = Message(
    message="Value is not 123",
    code="invalid_value",
)


class MockRule1(ValidationRule):
    async def __call__(
        self, *, value: Any, auth_user: User | AnonymousUser, path: list[str | int], **kwargs: Any
    ) -> None:
        if value == "invalid":
            raise InputError("Invalid value", path=path, message=MockMessage1)


class MockRule2(ValidationRule):
    async def __call__(
        self, *, value: Any, auth_user: User | AnonymousUser, path: list[str | int], **kwargs: Any
    ) -> None:
        if value != 123:
            raise InputError("Invalid value", path=path, message=MockMessage2)


class MockInput(Input):
    field1: str
    field2: int

    @property
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]:
        return {
            "field1": (MockRule1(),),
            "field2": (MockRule2(),),
        }

    def as_dict(self) -> dict[str, Any]:
        return {"field1": self.field1, "field2": self.field2}

    def __init__(self, field1: str, field2: int) -> None:
        self.field1 = field1
        self.field2 = field2


def test_validate_success() -> None:
    obj = MockInput(field1="valid", field2=123)

    try:
        async_to_sync(validate)(obj)
    except InputErrorGroup:
        pytest.fail("validate() raised InputErrorGroup unexpectedly")


def test_validate_failure() -> None:
    obj = MockInput(field1="invalid", field2=123)

    with pytest.raises(InputErrorGroup) as exc_info:
        async_to_sync(validate)(obj)

    assert len(exc_info.value.exceptions) == 1
    assert exc_info.value.exceptions[0].message.message == MockMessage1.message


def test_validate_multiple_failures() -> None:
    obj = MockInput(field1="invalid", field2=321)

    with pytest.raises(InputErrorGroup) as exc_info:
        async_to_sync(validate)(obj)

    assert len(exc_info.value.exceptions) == 2
    assert all(error.message in [MockMessage1, MockMessage2] for error in exc_info.value.exceptions)
