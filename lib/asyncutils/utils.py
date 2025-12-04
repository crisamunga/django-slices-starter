from collections.abc import Iterable

from asgiref.sync import sync_to_async


@sync_to_async
def alist[T](iterable: Iterable[T]) -> list[T]:
    """Converts an iterable to a list asynchronously."""
    return list(iterable)
