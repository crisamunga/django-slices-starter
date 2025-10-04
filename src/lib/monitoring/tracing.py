from collections.abc import Awaitable, Callable
from functools import wraps

from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def trace_function[**P, T](name: str | None = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with tracer.start_as_current_span(span_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def trace_async_function[**P, T](
    name: str | None = None,
    metadata: dict[str, str | int | bool] | None = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with tracer.start_as_current_span(span_name, kind=trace.SpanKind.SERVER) as span:
                if metadata:
                    span.set_attributes(metadata)
                return await func(*args, **kwargs)

        return wrapper

    return decorator
