from dataclasses import dataclass

from django.urls import URLPattern, path
from strawberry import Schema

from .views import AsyncGraphQLView


@dataclass(frozen=True)
class GraphQLEndpoint:
    name: str
    path: str
    types: tuple[type, ...]
    schema: Schema


@dataclass(frozen=True)
class GraphQLAPI:
    """Centralized GraphQL API schema and types aggregation."""

    endpoints: tuple[GraphQLEndpoint, ...] = ()

    @property
    def urls(self) -> list[URLPattern]:
        """Aggregate URLs from all GraphQL endpoints."""
        urls: list[URLPattern] = []
        for endpoint in self.endpoints:
            urls.append(
                path(
                    endpoint.path, AsyncGraphQLView.as_view(schema=endpoint.schema), name=f"graphql-api:{endpoint.name}"
                )
            )
        return urls

    @property
    def types(self) -> tuple[type, ...]:
        """Aggregate types from all GraphQL endpoints."""
        all_types: list[type] = []
        for endpoint in self.endpoints:
            all_types += endpoint.types
        return tuple(all_types)

    def __add__(self, other: "GraphQLAPI") -> "GraphQLAPI":
        """Combine two GraphQLAPI instances."""
        return GraphQLAPI(endpoints=self.endpoints + other.endpoints)


__all__ = ["GraphQLAPI", "GraphQLEndpoint"]
