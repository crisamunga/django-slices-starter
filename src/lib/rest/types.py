from typing import Annotated, Any
from uuid import UUID as UUID_

from pydantic import BeforeValidator


def change_to_list(value: Any) -> Any:
    if isinstance(value, str):
        return [UUID_(item.strip()) for item in value.split(",") if item.strip()]
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
        return [UUID_(item.strip()) for item in value[0].split(",") if item.strip()]
    return value


UUIDList = Annotated[list[UUID_] | None, BeforeValidator(change_to_list)]
