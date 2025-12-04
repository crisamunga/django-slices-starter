from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from .base import NotFoundError


@contextmanager
def not_found_on_error(resource: str, error_type: type[Exception] = ObjectDoesNotExist) -> Generator[None, Any]:
    """A context manager that modifies the specified `error_type` error to a `NotFoundError`.

    Different approach from Django's built in `get_object_or_404` to keep original method signatures
    that offer static type safety with mypy

    Args:
        resource (str): The name of the resource that was not found
        error_type (type[Exception]): The original error type to catch. Should be a class e.g. `ValueError`.
            Defaults to `ObjectDoesNotExist`.

    Raises:
        NotFoundError: In case `error_type` is raised

    Yields:
        Generator[None, Any, None]: A generator that yields the context manager
    """
    try:
        yield
    except error_type as e:
        raise NotFoundError(f"{resource} not found.") from e
