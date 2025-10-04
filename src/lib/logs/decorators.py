import inspect
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from lib.errors import BaseError


def log_error(logger_name: str | None = None) -> Callable[..., Any]:
    """Logs an error if an exception is raised in the decorated function.

    Only works for sync functions. For async functions, use `log_async_error_wrapper`.

    Args:
        logger_name (str | None, optional): Name of the logger to use when logging. Defaults to None.

    Returns:
        Callable[..., Any]: The decorated function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def _log_error(logger_name_: str | None, e: Exception, args: Any, kwargs: Any) -> None:
            logger = logging.getLogger(logger_name_)
            e.add_note(f"Parameters: {args=}, {kwargs=}")
            if isinstance(e, BaseError):
                e.add_note(f"Code: {e.message.code}")
                e.add_note(f"Metadata: {e.metadata}")
            logger.error(e, stack_info=True)

        if inspect.iscoroutinefunction(func) or inspect.iscoroutinefunction(getattr(func, "__call__", None)):  # noqa: B004

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger_name_ = logger_name or func.__module__
                    _log_error(logger_name_, e, args, kwargs)
                    raise

            return wrapper

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger_name_ = logger_name or func.__module__
                _log_error(logger_name_, e, args, kwargs)
                raise

        return wrapper

    return decorator
