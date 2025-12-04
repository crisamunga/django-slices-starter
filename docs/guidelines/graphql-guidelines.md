# GraphQL Guidelines

- This project uses `strawberry-graphql` for GraphQL implementation.
- GraphQL schema and operations are defined in `graphql.py` modules or `graphql` packages within each slice.
- Each slice manages its own GraphQL types, resolvers, and schemas. The API is built by federating these schemas.
- Strawberry resolvers are not typed, and are susceptible to the `Untyped Decorator` error from the type-checker. You can comment them as `# type: ignore # Untyped decorator from strawberry`.
- Always specify the return type using the `graphql_type` parameter in the `@strawberry.federation.field`, `@relay.connection`, `@strawberry.field` or `@strawberry.federation.mutation` decorators.

## Data loaders

- Data loaders are defined at the top of the `graphql.py` module or in a separate `loaders.py` file within the slice's `graphql` package.
- Data loaders have a header section.
- Extend the data loaders from `lib.graphql.DataLoader` to create slice-specific loaders.
- Defines a ket structure for each loader to encapsulate the parameters needed for loading data.
- Caching is only done in-memory during the request lifecycle to avoid stale data issues and cross-request contamination.

**Example:**

```python
from uuid import UUID

import core.models
from . import services
from lib.graphql import DataLoader, Info
from lib.logs import log_error

# ------------------------------------------------------------------------------
# Data loader
# ------------------------------------------------------------------------------


class UserLoader(DataLoader["UserLoader.Key", "core.models.User | None"]):
    class Key:
        def __init__(self, user_uuid: UUID, includes: list[str], auth_user: core.models.User) -> None:
            self.user_uuid = user_uuid
            self.includes = includes
            self.auth_user = auth_user

    @log_error()
    async def execute(self, keys: list[Key]) -> list[core.models.User | None | Exception]:
        uuids = []
        includes = set()
        auth_user = keys[0].auth_user  # Assuming all keys have the same auth_user since loader is called per request
        for k in keys:
            uuids.append(k.user_uuid)
            includes.update(k.includes)

        # Load users from the database or any other source
        users = await services.list_users(uuids=uuids, includes=list(includes), auth_user=auth_user)
        user_map = await users.ain_bulk(uuids, field_name="uuid")
        user_list: list[core.models.User | None | Exception] = []
        for key in keys:
            user = user_map.get(key.user_uuid)
            if user is None:
                user_list.append(None)
            else:
                user_list.append(user)

        return user_list
```

## Graphql Types and Resolvers

- Do not auto-generate GraqhQL types from models; define them explicitly to maintain control over the API.
- Resource types have a header section.
- All types are created as federated types with the `@strawberry.federation.type` decorator, except for types not resolved such as input types.
- The `@strawberry.federation.type` decorator includes `keys` parameter for defining the fields used for federation. It should usually include both `uuid` and `id`.
- All federated types must extend `lib.graphql.Node` to include the `id` field and support global identification.
- All types that belong to the slice should extend from `lib.graphql.Base` to inherit common fields (`uuid`, `created_at`, `updated_at`).
- All resolvers are async functions to leverage asynchronous capabilities.
- Utilize strawberry's `strawberry.field` decorator / function for adding description and metadata to fields.
- Related properties and dynamic properties are defined using the function syntax.
- Resource properties are based on the model fields, with the following guidelines:
  - Use Optional types (e.g., `str | None`) for fields that can be null.
  - Use lists (e.g., `list[Post]`) for related fields that are many-to-many or one-to-many relationships.
  - Use the appropriate primitive types (e.g., `str`, `int`, `bool`, `float`, etc.) for basic fields.
  - For datetime fields, use `datetime.datetime` type.
  - For decimal fields, use `decimal.Decimal` type.
- All federated types must implement the `is_type_of` and `resolve_reference` class methods for proper type resolution in a federated schema.
- Do not import types from other slices directly; instead, define slim types that can be extended in the federated schema.
- Resolvers should use data loaders to fetch data.
- Decorate resolvers with `@log_error()` to log exceptions that occur during resolution.

**Example:**

```python
from typing import Annotated, Any
import strawberry
from uuid import UUID
from lib.graphql import Base, Context, DataLoader, Info, relay
from lib.logs import log_error

# ------------------------------------------------------------------------------
# Types
# ------------------------------------------------------------------------------

@strawberry.federation.type(keys=["uuid", "id"], description="Post")
class Post(relay.Node):
    @classmethod
    def is_type_of(cls, obj: Any, info: Info) -> bool:
        return super().is_type_of(obj, info) or isinstance(obj, core.models.Post)

    @classmethod
    def resolve_node(cls, node_id: str, *, info: Info, required: bool) -> "Post":
        return cls(uuid=UUID(node_id))


@strawberry.federation.type(keys=["uuid", "id"], description="User")
class User(Base, relay.Node):
    email: str = strawberry.field(description="The user's email address.")
    first_name: str = strawberry.field(description="The user's first name.")
    last_name: str = strawberry.field(description="The user's last name.")
    is_active: bool = strawberry.field(description="Whether the user is active or not.")

    @strawberry.field(graphql_type=list[Post] | None, description="The posts written by the user.")  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def posts(self, info: strawberry.Info[Context]) -> Any:
        with suppress(SynchronousOnlyOperation):
            return list(self.posts.all())


    @classmethod
    def is_type_of(cls, obj: Any, info: Info) -> bool:
        return isinstance(obj, core.models.User)

    @classmethod
    @log_error()
    def resolve_node(cls, node_id: str, *, info: Info, required: bool) -> Any:
        loader = info.get_loader(UserLoader)
        includes = info.get_includes(
            path=["node"],
            depth=2,
            selection_include_mapping={"roles": "roles", "authors": "authors"},
        )
        return loader.load(
            UserLoader.Key(
                user_uuid=UUID(node_id),
                includes=includes,
                auth_user=info.user,
            )
        )

    @classmethod
    @log_error()
    def resolve_reference(cls, info: Info, id: str | None = None, uuid: str | None = None) -> Any:  # noqa: A002
        includes = info.get_includes(
            path=["_entities"],
            depth=2,
            selection_include_mapping={"roles": "roles", "authors": "authors"},
        )
        loader = info.get_loader(UserLoader)
        if uuid:
            return loader.load(
                UserLoader.Key(
                    user_uuid=UUID(uuid),
                    includes=includes,
                    auth_user=info.user,
                )
            )
        elif id:
            global_id = relay.GlobalID.from_id(id)
            if global_id.type_name == "User":
                return loader.load(
                    UserLoader.Key(
                        user_uuid=UUID(global_id.node_id),
                        includes=includes,
                        auth_user=info.user,
                    )
                )
```

## Queries

- Queries are defined in the `Query` class within the `graphql.py` module of each slice.
- Queries have a header section.
- Inputs for queries are defined as separate input types using `strawberry.input`.
- Queries should support pagination using relay-style connections from `lib.graphql.relay`.
- Queries should use data loaders to fetch data efficiently.
- Identify fields that need to be pre-fetched using includes from the query info, and include them when loading data.
- Always include both plural and singular queries for resources (e.g., `users` and `user`) where applicable.

**Example:**

```python

# ------------------------------------------------------------------------------
# Queries
# ------------------------------------------------------------------------------
from typing import Annotated, Any
import strawberry
from uuid import UUID
from lib.graphql import Base, Context, DataLoader, Info, make_schema, mutations, relay
from lib.logs import log_error
from . import services

@strawberry.input
class UserFilter:
    uuids: Annotated[list[UUID] | None, strawberry.argument(description="The UUIDs of the users to filter by.")] = None


@strawberry.type
class Query:
    @strawberry.federation.field(graphql_type=User, description="Get a single user", tags=["Admin"])  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def user(
        self,
        info: Info,
        user_uuid: Annotated[UUID, strawberry.argument(description="The UUID of the user.")],
    ) -> Any:
        includes = info.get_includes(
            path=["user"],
            depth=2,
            selection_include_mapping={"roles": "roles", "authors": "authors"},
        )
        return await services.get_user(auth_user=info.context.request.user, user_uuid=user_uuid, includes=includes)

    @relay.connection(graphql_type=User, description="List users", tags=["Admin"])  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def users(
        self,
        info: Info,
        filter_: Annotated[
            UserFilter | None, strawberry.argument(description="Filters to apply.", name="filter")
        ] = None,
        search: Annotated[str | None, strawberry.argument(description="Search for users by name.")] = None,
        sort: Annotated[str | None, strawberry.argument(description="Sort users by name.")] = None,
    ) -> Any:
        includes = info.get_includes(
            path=["users", "edges", "node"],
            depth=2,
            selection_include_mapping={"roles": "roles", "authors": "authors"},
        )
        return await services.list_users(
            auth_user=info.user, includes=includes, search=search, sort=sort, uuids=filter_.uuids if filter_ else None
        )
```

## Mutations

- Mutations are defined in the `Mutation` class within the `graphql.py` module of each slice.
- Mutations have a header section.
- Responses are defined by separate types extending the generic `lib.graphql.mutations.Payload` base class with a type parameter for the main result type.
- Inputs for mutations are defined in `strawberry.federation.mutation` decorator as parameters.
- Each mutation should include an extension of `lib.graphql.mutations.ValidationInputMutationExtension` to transform parameters to an input class.
- The extension accepts validation rules to enforce on the input data.
- Edit mutations should allow partial updates by making parameters optional.
- Decorate mutations with `@log_error()` to log exceptions that occur during execution.
- All mutations should be defined as async functions.

**Example:**

```python
from typing import Annotated, Any
from uuid import UUID

import strawberry

import core.models
from core.users import services
from . import validation as v
from lib.asyncutils import suppress_sync_only_error
from lib.graphql import Base, Context, DataLoader, Info, make_schema, mutations, relay
from lib.logs import log_error

# ------------------------------------------------------------------------------
# Mutations
# ------------------------------------------------------------------------------

@strawberry.federation.type(tags=["Admin"])
class AddUserPayload(mutations.Payload[User]): ...


@strawberry.federation.type(tags=["Admin"])
class EditUserPayload(mutations.Payload[User]): ...


@strawberry.federation.type(tags=["Admin"])
class DeleteUserPayload(mutations.Payload[bool]): ...


@strawberry.type
class Mutation:
    @strawberry.federation.mutation(
        description="Add a user",
        extensions=[
            mutations.ValidatedInputMutationExtension(
                {
                    "email": (v.EmailShouldBeUnique(), v.EmailShouldBeValid()),
                }
            )
        ],
        graphql_type=AddUserPayload,
        tags=["Admin"],
    )  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def add_user(
        self,
        info: Info,
        email: Annotated[str, strawberry.argument(description="The email of the user.")],
        first_name: Annotated[str, strawberry.argument(description="The first name of the user.")],
        last_name: Annotated[str, strawberry.argument(description="The last name of the user.")],
    ) -> Any:
        return await services.create_user(
            auth_user=info.user,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )

    @strawberry.federation.mutation(
        description="Edit a user",
        extensions=[
            mutations.ValidatedInputMutationExtension(
                {
                    "email": (v.EmailShouldBeUnique(exclude_current=True), v.EmailShouldBeValid()),
                }
            )
        ],
        graphql_type=EditUserPayload,
        tags=["Admin"],
    )  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def edit_user(
        self,
        info: Info,
        user_uuid: Annotated[UUID, strawberry.argument(description="The UUID of the user.")],
        email: Annotated[str | None, strawberry.argument(description="The email of the user.")] = None,
        first_name: Annotated[str | None, strawberry.argument(description="The first name of the user.")] = None,
        last_name: Annotated[str | None, strawberry.argument(description="The last name of the user.")] = None,
    ) -> Any:
        return await services.edit_user(
            auth_user=info.user,
            user_uuid=user_uuid,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

    @strawberry.federation.mutation(
        description="Delete a user",
        extensions=[mutations.ValidatedInputMutationExtension()],
        graphql_type=DeleteUserPayload,
        tags=["Admin"],
    )  # type: ignore # Untyped decorator from strawberry
    @log_error()
    async def delete_user(
        self,
        info: Info,
        user_uuid: Annotated[UUID, strawberry.argument(description="The UUID of the user.")],
    ) -> Any:
        await services.delete_user(
            auth_user=info.user,
            user_uuid=user_uuid,
        )
        return True
```

## GraphQL Schemas

- Schemas are defined last in each slice's `graphql.py` module.
- Use `lib.graphql.make_schema` to create the schema.
- Each schema includes the `Query` and `Mutation` classes defined in the slice.
- Once defined, the schemas are integrated into the main GraphQL API in `config/graphql.py`.
- Define types that the schema owns for federation purposes

**Example:**

```python
from lib.graphql import make_schema

# ------------------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------------------

types = [User, Post]

schema = make_schema(
    query=Query,
    mutation=Mutation,
    types=types,
)
```

## Registering the Schema

- Each slice's schema should be registered in `core/graphql.py` to be included in the main GraphQL API.:

```python
# core/graphql.py
# <slice> is the name of the slice being registered
from django.urls import path
from lib.graphql import AsyncGraphQLView

from .<slice> import graphql as <slice>

urls = [
    path("<slice>/", AsyncGraphQLView.as_view(schema=<slice>.schema), name="graphql-core-<slice>"),
]
```
