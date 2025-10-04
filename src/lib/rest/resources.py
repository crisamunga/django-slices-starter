from datetime import datetime
from typing import Any, Literal

from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import UUID4

from lib import messages
from lib.validation import Input, ValidationRule


class BaseObjectResource(Schema):
    uuid: UUID4 = Field(..., description="The object's UUID.")
    created_at: datetime = Field(..., description="The time the object was created.")
    updated_at: datetime = Field(..., description="The time the object was last updated.")


class ErrorDetail(Schema):
    code: str = Field(..., description="A unique error code.")
    message: str = Field(..., description="A human-readable error message.")
    path: list[str | int] | None = Field(
        None,
        description="A list of path segments that indicate the location of the error in the data provided.",
    )


class Response400(Schema):
    message: messages.Message = Field(..., description="A message object describing the error.")
    errors: list[ErrorDetail] | None = Field(
        None, description="A list of error details, if any. Each detail object describes a specific error."
    )


class Response401(Schema):
    message: messages.Message = Field(
        messages.get_message(code="unauthenticated", message=_("You must sign in to perform this action.")),
        description="The error message.",
    )


class Response403(Schema):
    message: messages.Message = Field(
        messages.get_message(code="unauthorized", message=_("You don't have permission to perform this action.")),
        description="The error message.",
    )


class Response404(Schema):
    message: messages.Message = Field(
        messages.get_message(code="not_found", message=_("The requested resource was not found.")),
        description="The error message.",
    )


class Response422(Schema):
    message: messages.Message = Field(
        messages.get_message(code="invalid_input", message=_("Invalid input.")),
        description="The error message.",
    )
    errors: list[ErrorDetail] | None = Field(
        None, description="A list of error details, if any. Each detail object describes a specific error."
    )


class Response500(Schema):
    message: messages.Message = Field(
        messages.get_message(code="unexpected_error", message=_("An unexpected error occurred.")),
        description="The error message.",
    )


error_codes = frozenset({400, 405, 422, 500})


def response[T: Schema](
    code: int, type_: type[T] | type[list[T]] | None = None
) -> dict[int | frozenset[int], Any | None]:
    return {
        code: type_,
        400: Response400,
        401: Response401,
        403: Response403,
        404: Response404,
        405: Literal["Method not allowed."],
        422: Response422,
        500: Response500,
    }


class BaseInput(Input, Schema):
    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="python")

    @property
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]:
        return {}
