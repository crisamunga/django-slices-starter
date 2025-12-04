from typing import Any

import strawberry

from lib.graphql import Base, Info, make_schema, relay
from lib.logs import log_error

from . import models, services

# ------------------------------------------------------------------------------
# Types
# ------------------------------------------------------------------------------


@strawberry.type
class Profile(Base, relay.Node):
    email: str = strawberry.field(description="Email of the user.")
    first_name: str = strawberry.field(description="First name of the user.")
    last_name: str = strawberry.field(description="Last name of the user.")
    is_active: bool = strawberry.field(description="Indicates if the user is active.")

    @classmethod
    def is_type_of(cls, obj: Any, info: Info) -> bool:
        return isinstance(obj, models.User) and obj == info.user

    @classmethod
    def resolve_node(cls, node_id: str, *, info: Info, required: bool) -> Any:
        return services.get_profile(auth_user=info.user)

    @classmethod
    @log_error()
    async def resolve_reference(
        cls,
        info: Info,
        id: str | None = None,  # noqa: A002 # 'id' is required by federation
        uuid: str | None = None,
    ) -> Any:
        return await services.get_profile(auth_user=info.user)


# ------------------------------------------------------------------------------
# Queries
# ------------------------------------------------------------------------------


@strawberry.type
class Query:
    @strawberry.field(
        description="Fetch the profile of the authenticated user.",
        graphql_type=Profile,
    )  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def profile(self, info: Info) -> models.User | None:
        return await services.get_profile(auth_user=info.user)


# ------------------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------------------
types = (Profile,)

schema = make_schema(query=Query, types=types)
