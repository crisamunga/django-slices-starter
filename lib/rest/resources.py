from datetime import datetime
from typing import Any, Literal

from ninja import Field, Schema
from pydantic import UUID4

from lib.validation import Input, ValidationRule


class BaseObjectResource(Schema):
    uuid: UUID4 = Field(..., description="The object's UUID.")
    created_at: datetime = Field(..., description="The time the object was created.")
    updated_at: datetime = Field(..., description="The time the object was last updated.")


class ErrorMessage(Schema):
    code: str = Field(..., description="A unique error code.")
    message: str = Field(..., description="A human-readable error message.")
    path: list[str | int] | None = Field(
        None,
        description="A list of path segments that indicate the location of the error in the data provided.",
    )


class ErrorResponse(Schema):
    errors: list[ErrorMessage] | None = Field(
        None, description="A list of error details, if any. Each detail object describes a specific error."
    )


error_codes = frozenset({400, 405, 422, 500})


def response[T: Schema](
    code: int, type_: type[T] | type[list[T]] | None = None
) -> dict[int | frozenset[int], Any | None]:
    return {
        code: type_,
        400: ErrorResponse,
        401: ErrorResponse,
        403: ErrorResponse,
        404: ErrorResponse,
        405: Literal["Method not allowed."],
        422: ErrorResponse,
        500: ErrorResponse,
    }


class BaseInput(Input, Schema):
    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="python")

    @property
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]:
        return {}
