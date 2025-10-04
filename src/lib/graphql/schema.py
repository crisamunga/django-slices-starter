from collections.abc import Iterable

import strawberry
from strawberry.extensions.tracing import OpenTelemetryExtension
from strawberry.schema.config import StrawberryConfig

from .authentication import AuthenticationExtension
from .info import Info


def make_schema(
    *,
    query: type,
    mutation: type | None = None,
    types: Iterable[type] | None = None,
) -> strawberry.Schema:
    return strawberry.federation.Schema(
        query=query,
        mutation=mutation,
        types=types or (),
        # strawberry-federation specific
        extensions=[AuthenticationExtension(), OpenTelemetryExtension()],
        config=StrawberryConfig(info_class=Info),
        enable_federation_2=True,
    )
