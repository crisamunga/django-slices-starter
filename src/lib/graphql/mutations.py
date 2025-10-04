from typing import Any

import strawberry.annotation
from asgiref.sync import async_to_sync
from strawberry.field_extensions import InputMutationExtension as _InputMutationExtension
from strawberry.types import arguments
from strawberry.types.field import StrawberryField

from lib.validation import Input, ValidationRule, validate

from .info import Info


@strawberry.type()
class Payload[T]:
    client_request_id: str | None
    data: T | None

    def __init__(self, client_request_id: str | None = None, data: T | None = None) -> None:
        self.client_request_id = client_request_id
        self.data = data


class GraphqlInput(Input):
    def __init__(self, data: object, validators: dict[str, tuple[ValidationRule, ...]]) -> None:
        self._data = data
        self._validators = validators or {}

    def as_dict(self) -> dict[str, Any]:
        return vars(self._data)

    @property
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]:
        return self._validators

    def __getattribute__(self, name: str) -> Any:
        if name in ("_data", "_validators", "validators", "as_dict"):
            return super().__getattribute__(name)
        if hasattr(self._data, name):
            return getattr(self._data, name)
        return super().__getattribute__(name)


class ValidatedInputMutationExtension(_InputMutationExtension):
    def __init__(self, validation_rules: dict[str, tuple[ValidationRule, ...]] | None = None) -> None:
        self._validation_rules = validation_rules or {}
        super().__init__()

    def apply(self, field: StrawberryField) -> None:
        resolver = field.base_resolver
        if resolver:
            resolver.wrapped_func.__annotations__["client_request_id"] = str | None
            resolver.arguments += [
                arguments.StrawberryArgument(
                    python_name="client_request_id",
                    graphql_name=None,
                    type_annotation=strawberry.annotation.StrawberryAnnotation(strawberry.ID | None),
                    description="A unique identifier for the request.",
                    default=None,
                ),
            ]

        return super().apply(field)

    def resolve(self, next_: Any, source: Any, info: Info, **kwargs: Any) -> Any:  # type: ignore # Info class super
        input_ = kwargs.get("input")
        client_request_id = input_.__dict__.pop("client_request_id", None)
        if input_ and self._validation_rules:
            async_to_sync(validate)(
                GraphqlInput(data=input_, validators=self._validation_rules),
                auth_user=info.user,
                base_path=[*info.path.as_list(), "input"],
            )

        result = super().resolve(next_, source, info, **kwargs)
        return Payload(client_request_id=client_request_id, data=result)

    async def resolve_async(self, next_: Any, source: Any, info: Info, **kwargs: Any) -> Any:  # type: ignore # Info class super
        input_ = kwargs.get("input")
        client_request_id = input_.__dict__.pop("client_request_id", None)
        if input_ and self._validation_rules:
            await validate(
                GraphqlInput(data=input_, validators=self._validation_rules),
                auth_user=info.user,
                base_path=[*info.path.as_list(), "input"],
            )

        result = await super().resolve_async(next_, source, info, **kwargs)
        return Payload(client_request_id=client_request_id, data=result)
