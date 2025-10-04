from datetime import datetime
from typing import Any
from uuid import UUID

import strawberry


@strawberry.interface
class Base:
    uuid: UUID = strawberry.field(description="The unique identifier of the object.")
    created_at: datetime = strawberry.field(description="The date and time the object was created.")
    updated_at: datetime = strawberry.field(description="The date and time the object was last updated.")

    @classmethod
    def is_type_of(cls, obj: Any, info: Any) -> bool:
        raise NotImplementedError("is_type_of must be implemented in subclasses.")
