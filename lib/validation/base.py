from abc import ABC, abstractmethod
from typing import Any

from core.models import AnonymousUser, User
from lib.errors import InputError


class ValidationRule(ABC):
    @abstractmethod
    async def __call__(
        self,
        *,
        value: Any,
        auth_user: User | AnonymousUser,
        obj: "Input",
        path: list[str | int],
    ) -> None: ...


class Input(ABC):
    @abstractmethod
    def as_dict(self) -> dict[str, Any]:
        return self.__dict__

    @property
    @abstractmethod
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]:
        return {}


async def validate(  # noqa: C901 # Necessary complexity due to unmarshalling ExceptionGroup
    obj: Input,
    *,
    auth_user: User | AnonymousUser | None = None,
    base_path: list[str | int] | None = None,
) -> None:
    errors = []
    base_path = base_path or []

    if not obj.validators:
        return

    if not auth_user:
        auth_user = AnonymousUser()

    for field_name, rules in obj.validators.items():
        for rule in rules:
            try:
                await rule(
                    value=getattr(obj, field_name),
                    auth_user=auth_user,
                    obj=obj,
                    path=[*base_path, field_name],
                )
            except InputError as e:
                errors.append(e)
            except ExceptionGroup as e:

                def get_exceptions(group: ExceptionGroup) -> list[InputError]:
                    excs: list[InputError] = []
                    for exc in group.exceptions:
                        if isinstance(exc, InputError):
                            excs.append(exc)
                        elif isinstance(exc, ExceptionGroup):
                            excs.extend(get_exceptions(exc))
                        else:
                            raise Exception("Non-InputError found in ExceptionGroup") from exc
                    return excs

                errors.extend(get_exceptions(e))
            except Exception:
                raise

    if errors:
        raise ExceptionGroup("Validation failed", errors)
