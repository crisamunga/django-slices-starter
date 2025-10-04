from collections.abc import Awaitable, Callable
from functools import wraps

from opentelemetry import trace

from lib.errors.base import AuthorizationError


def permission[**P](func: Callable[P, Awaitable[bool]]) -> Callable[P, Awaitable[None]]:
    """
    This decorates a function that returns a boolean indicating whether the user has permission to perform an action.
    If the user does not have permission, it raises an `AuthorizationError`.

    Raises:
        AuthorizationError: If the original function returns anything other than True.
    """

    @wraps(func)
    async def _fn(*args: P.args, **kwargs: P.kwargs) -> None:
        span_name = f"permission:{func.__module__}.{func.__name__}"
        with trace.get_tracer(__name__).start_as_current_span(span_name, kind=trace.SpanKind.SERVER):
            result = await func(*args, **kwargs)

        if result is not True:
            raise AuthorizationError(
                "User is not authorized to perform this action",
                permission_required=func.__name__,
            )

    return _fn
