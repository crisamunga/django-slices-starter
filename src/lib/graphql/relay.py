import dataclasses
import inspect
from collections.abc import Awaitable, Callable, Coroutine, Iterable, Mapping, Sequence
from typing import Annotated, Any, Self, TypeVar
from uuid import UUID

import strawberry
import strawberry.annotation
from asgiref.sync import async_to_sync
from django.conf import settings
from django.db.models import QuerySet
from strawberry import extensions, relay
from strawberry.types import arguments, field

from lib.pagination import paginate

from .info import Info
from .schema import make_schema

T = TypeVar("T")
DEFAULT_LIMIT = settings.API_PAGINATION_MAX_LIMIT


GlobalID = relay.GlobalID

GlobalIDValueError = relay.GlobalIDValueError


@strawberry.type
class PageInfo:
    start_cursor: str | None = strawberry.federation.field(
        description="The first cursor to start with.", default=None, shareable=True
    )
    end_cursor: str | None = strawberry.federation.field(
        description="The next cursor to continue with.", default=None, shareable=True
    )
    has_next_page: bool = strawberry.federation.field(
        description="Whether there are more pages to fetch.", default=False, shareable=True
    )
    has_previous_page: bool = strawberry.federation.field(
        description="Whether there are previous pages to fetch.", default=False, shareable=True
    )


@strawberry.type
class Edge[T]:
    cursor: str
    node: T


@strawberry.type
class Connection[T]:
    edges: list[Edge[T]] = strawberry.field(description="The edges of the connection.")
    page_info: PageInfo = strawberry.field(description="The information about the page.")


# Borrowed argument structure from official strawberry repo:
#   https://github.com/strawberry-graphql/strawberry/blob/main/strawberry/relay/fields.py
#   MIT License
#   Last updated this code snippet on: 2024-08-26


class PaginationExtension(extensions.FieldExtension):
    def __init__(self, sorting_field: str = "id") -> None:
        self._sorting_field = sorting_field
        super().__init__()

    def apply(self, field: field.StrawberryField) -> None:
        field.arguments.extend(
            [
                arguments.StrawberryArgument(
                    python_name="before",
                    graphql_name=None,
                    type_annotation=strawberry.annotation.StrawberryAnnotation(str | None),
                    description="Returns the items in the list that come before the specified cursor.",
                    default=None,
                ),
                arguments.StrawberryArgument(
                    python_name="after",
                    graphql_name=None,
                    type_annotation=strawberry.annotation.StrawberryAnnotation(str | None),
                    description="Returns the items in the list that come after the specified cursor.",
                    default=None,
                ),
                arguments.StrawberryArgument(
                    python_name="first",
                    graphql_name=None,
                    type_annotation=strawberry.annotation.StrawberryAnnotation(int | None),
                    description="Returns the first n items from the list.",
                    default=None,
                ),
                arguments.StrawberryArgument(
                    python_name="last",
                    graphql_name=None,
                    type_annotation=strawberry.annotation.StrawberryAnnotation(int | None),
                    description="Returns the items in the list that come after the specified cursor.",
                    default=None,
                ),
            ]
        )

    def resolve(
        self,
        next_: Callable[..., QuerySet[Any]],
        source: Any,
        info: strawberry.Info,
        *,
        before: str | None = None,
        after: str | None = None,
        first: int | None = None,
        last: int | None = None,
        **kwargs: Any,
    ) -> Any:
        return async_to_sync(self.resolve_async)(
            next_, source, info, before=before, after=after, first=first, last=last, **kwargs
        )

    async def resolve_async(
        self,
        next_: Callable[..., Awaitable[QuerySet[Any]]] | Callable[..., QuerySet[Any]],
        source: Any,
        info: strawberry.Info,
        *,
        before: str | None = None,
        after: str | None = None,
        first: int | None = None,
        last: int | None = None,
        **kwargs: Any,
    ) -> Any:
        source = next_(source, info, **kwargs)
        if inspect.isawaitable(source):
            source = await source

        cursor = after or before
        forward = not bool(before)
        limit = first or last or DEFAULT_LIMIT

        return await paginate(
            source,
            cursor=cursor,
            limit=limit,
            forward=forward,
        )


@strawberry.federation.interface(keys=["id", "uuid"], description="A Node in the GraphQL schema.")
class Node:
    uuid: UUID = strawberry.federation.field(description="The unique identifier of the object.")

    @strawberry.federation.field
    def id(self, info: Any) -> GlobalID:
        return GlobalID(self.__class__.__name__, str(self.uuid))

    @classmethod
    def is_type_of(cls, obj: Any, info: Info) -> bool:
        return isinstance(obj, cls)

    @classmethod
    def resolve_reference(cls, info: Info, id: str | None = None, uuid: str | None = None) -> "Any":  # noqa: A002 # Need parameter to be named `id` for relay`
        if uuid:
            return cls(uuid=UUID(uuid))
        if id:
            global_id = GlobalID.from_id(id)
            if global_id.type_name == "User":
                return cls(uuid=UUID(global_id.node_id))
        return None

    @classmethod
    def resolve_node(cls, node_id: str, *, info: Info, required: bool) -> "Self":
        return cls(uuid=UUID(node_id))


def connection(  # noqa: PLR0913 - Allow > 10 arguments for this case
    graphql_type: type[Node],
    *,
    resolver: Callable[..., Coroutine[Any, Any, Any]] | Callable[..., Awaitable[Any]] | None = None,
    name: str | None = None,
    description: str | None = None,
    deprecation_reason: str | None = None,
    default: Any = dataclasses.MISSING,
    default_factory: Callable[..., object] | object = dataclasses.MISSING,
    metadata: Mapping[Any, Any] | None = None,
    directives: Sequence[object] | None = (),
    extensions: list[extensions.FieldExtension] | None = None,
    tags: Iterable[str] | None = None,
    shareable: bool = False,
) -> Any:
    extensions = (extensions or []) + [PaginationExtension()]

    return strawberry.federation.field(
        graphql_type=Connection[graphql_type],  # type: ignore # Mypy doesn't like runtime types on generics
        resolver=resolver,  # type: ignore # There is an overload to support None which mypy doesn't see
        name=name,
        description=description,
        deprecation_reason=deprecation_reason,
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        directives=directives,
        extensions=extensions,
        tags=tags,
        shareable=shareable,
    )


@strawberry.type
class NodeQuery:
    """Non-federated relay node query"""

    @strawberry.federation.field(
        graphql_type=Node | None,
        name="node",
        description="Fetches an object given its ID.",
    )  # type: ignore # Untyped decorator from strawberry
    def node(
        self,
        info: Info,
        id_: Annotated[relay.GlobalID, strawberry.argument(name="id", description="The ID of the object.")],
    ) -> Any:
        type_def = info.schema.get_type_by_name(id_.type_name)
        origin: Any = getattr(type_def, "origin", None)
        if origin is None:
            raise relay.GlobalIDValueError(
                f"Cannot resolve. GlobalID requires a GraphQL Node type, received `{id_.type_name}`."
            )
        origin = origin.resolve_type if isinstance(origin, strawberry.LazyType) else origin
        if not issubclass(origin, Node):
            raise relay.GlobalIDValueError(
                f"Cannot resolve. GlobalID requires a GraphQL Node type, received `{id_.type_name}`."
            )
        return origin.resolve_node(id_.node_id, info=info, required=True)


def create_federated_node_schema(types: list[type]) -> strawberry.Schema:
    """Creates a schema for the node query in a federated graphql api

    Args:
        types (list[type]): List of types that the node query should resolve

    Raises:
        relay.GlobalIDValueError: When there isn't a proper federated type to be resolved

    Returns:
        strawberry.Schema: The created schema
    """

    @strawberry.type
    class Query:
        @strawberry.federation.field(
            graphql_type=Node | None,
            name="node",
            description="Fetches an object given its ID.",
        )  # type: ignore # Untyped decorator from strawberry
        def node(
            self,
            info: Info,
            id_: Annotated[relay.GlobalID, strawberry.argument(name="id", description="The ID of the object.")],
        ) -> Any:
            type_def = info.schema.get_type_by_name(id_.type_name)
            origin: Any = getattr(type_def, "origin", None)
            if origin is None:
                raise relay.GlobalIDValueError(
                    f"Cannot resolve. GlobalID requires a GraphQL Node type, received `{id_.type_name}`."
                )
            return origin(uuid=UUID(id_.node_id))

    return_types: dict[str, type] = {"Node": Node}

    def create_type(from_type: Any) -> tuple[str, type] | tuple[None, None]:
        if not issubclass(from_type, Node):
            return None, None
        type_def = getattr(from_type, "__strawberry_definition__", None)
        if type_def is None:
            return None, None
        raw_type_ = type(type_def.name, (Node,), {})
        type_ = strawberry.federation.type(
            raw_type_, name=type_def.name, keys=["id", "uuid"], description=f"A {type_def.name} resource."
        )
        return type_def.name, type_

    def create_types_from_list(from_types: Iterable[type], return_types: dict[str, type]) -> dict[str, type]:
        for from_type in from_types:
            type_name, type_ = create_type(from_type)
            if type_name and type_:
                return_types[type_name] = type_
        return return_types

    return_types = create_types_from_list(types, return_types)

    return make_schema(
        query=Query,
        types=list(return_types.values()),
    )
