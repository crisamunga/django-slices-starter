from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise


def get_message(*, code: str, message: "str | _StrPromise", **format_kwargs: Any) -> "Message":
    """
    Create a message with a given message and code.
    """
    if format_kwargs:
        message = message.format(**format_kwargs)
    return Message(
        message=str(message),
        code=code,
    )


@dataclass(frozen=True)
class Message:
    message: str
    code: str


__all__ = ["Message", "get_message"]
