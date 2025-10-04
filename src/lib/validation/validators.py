from datetime import datetime
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import lib.messages
from lib.asyncutils import alist
from lib.errors import InputError, InputErrorGroup
from lib.models import BaseModel

from .base import ValidationRule


class EmailShouldBeValid(ValidationRule):
    async def __call__(self, *, value: str | None, path: list[str | int], **kwargs: Any) -> None:
        if not value:
            return
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except ValidationError as e:
            raise InputError(
                f"Invalid email {value}",
                message=lib.messages.get_message(
                    code="invalid_email", message=_("Invalid email address {value}."), value=value
                ),
                path=path,
            ) from e


class DateShouldNotBeInFuture(ValidationRule):
    async def __call__(self, *, value: datetime, path: list[str | int], **kwargs: Any) -> None:
        if not isinstance(value, datetime):
            raise InputError(
                "Invalid date",
                message=lib.messages.get_message(code="invalid_date", message=_("Invalid date.")),
                path=path,
            )
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        if value > timezone.now():
            raise InputError(
                f"Date {value} cannot be in the future",
                message=lib.messages.get_message(
                    code="date_in_future",
                    message=_("Date {value} should not be in the future."),
                    value=value.strftime("%Y-%m-%d %H:%M:%S"),
                ),
                path=path,
            )


class ModelShouldNotExist(ValidationRule):
    def __init__(self, db_model: type[BaseModel], field: str | None = None) -> None:
        self.db_model = db_model
        self.field = field or "uuid"

    async def __call__(self, *, value: Any, path: list[str | int], **kwargs: Any) -> None:
        if not value:
            return

        filters = {self.field: value}

        if await self.db_model.objects.filter(**filters).aexists():  # type: ignore
            raise InputError(
                f"Duplicate object {value}",
                message=lib.messages.get_message(
                    code="duplicate", message=_("{field} {object} already exists."), field=self.field, object=value
                ),
                path=path,
            )


class MultipleModelsShouldExist(ValidationRule):
    def __init__(self, db_model: type[BaseModel], field: str | None = None) -> None:
        self.db_model = db_model
        self.field = field or "uuid"

    async def __call__(self, *, value: list[Any], path: list[str | int], **kwargs: Any) -> None:
        if not value:
            return

        filters = {f"{self.field}__in": value}

        existing = set(await alist(self.db_model.objects.filter(**filters).values_list(self.field, flat=True)))  # type: ignore

        errors: list[InputError] = []

        for i, val in enumerate(value):
            if val not in existing:
                errors.append(
                    InputError(
                        f"Object not found {val}",
                        message=lib.messages.get_message(
                            code="object_not_found", message=_("Object {value} not found."), value=val
                        ),
                        path=[*path, i],
                    )
                )

        if errors:
            raise InputErrorGroup("Some objects were not found", errors)


class MinMaxLength(ValidationRule):
    def __init__(self, min_length: int | None = None, max_length: int | None = None) -> None:
        self.min_length = min_length
        self.max_length = max_length

    async def __call__(self, *, value: str | list[Any] | None, path: list[str | int], **kwargs: Any) -> None:
        if value is None:
            return

        if self.min_length is not None and self.min_length > len(value):
            raise InputError(
                f"Invalid length {len(value)}",
                message=lib.messages.get_message(
                    code="min_length_not_met", message=_("Minimum length {length} not met."), length=self.min_length
                ),
                path=path,
            )

        if self.max_length is not None and self.max_length < len(value):
            raise InputError(
                f"Invalid length {len(value)}",
                message=lib.messages.get_message(
                    code="max_length_exceeded", message=_("Maximum length {length} exceeded."), length=self.max_length
                ),
                path=path,
            )
