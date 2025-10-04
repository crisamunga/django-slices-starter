from dataclasses import dataclass
from typing import Protocol

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.signing import b64_decode, b64_encode
from django.db.models import QuerySet

from lib.models import BaseModel

DEFAULT_LIMIT = settings.API_PAGINATION_MAX_LIMIT


def encode_cursor(data: str) -> str:
    return b64_encode(data.encode()).decode()


def decode_cursor(cursor: str) -> str:
    return b64_decode(cursor.encode()).decode()


class PageInput(Protocol):
    first: int | None = None
    after: str | None = None
    last: int | None = None
    before: str | None = None


@dataclass
class PageInfo:
    count: int
    start_cursor: str | None = None
    end_cursor: str | None = None
    has_next_page: bool = False
    has_previous_page: bool = False


@dataclass
class Node[T]:
    cursor: str
    node: T


@dataclass
class Page[T]:
    edges: list[Node[T]]
    page_info: PageInfo


@sync_to_async
def paginate[T: BaseModel](
    queryset: QuerySet[T],
    *,
    cursor: str | None = None,
    limit: int = DEFAULT_LIMIT,
    forward: bool = True,
    sorting_field: str = "id",
    include_more: bool = True,
) -> Page[T]:
    if cursor:
        cursor = decode_cursor(cursor)

    queryset = queryset.order_by(sorting_field if forward else f"-{sorting_field}")

    selector = "gt" if forward else "lt"
    query = {f"{sorting_field}__{selector}": cursor} if cursor else {}

    original_queryset = queryset
    if cursor:
        queryset = queryset.filter(**query)

    items = list(queryset[: limit + 1])

    has_more = len(items) > limit
    if has_more:
        items = items[:-1]

    if not items:
        return Page(
            edges=[],
            page_info=PageInfo(
                count=0,
                start_cursor=None,
                end_cursor=None,
                has_next_page=False,
                has_previous_page=False,
            ),
        )

    if not forward and items:
        items = list(reversed(items))

    start_cursor = None
    end_cursor = None
    if items:
        start_cursor = getattr(items[0], sorting_field)
        end_cursor = getattr(items[-1], sorting_field)

    # Executing 1 more db query to get the first and last items to avoid using count() on the queryset
    # count() on postgres is an expensive operation for large

    if include_more:
        has_next_page = (
            has_more if forward else original_queryset.filter(**{f"{sorting_field}__gt": end_cursor}).exists()
        )
        has_previous_page = (
            has_more if not forward else original_queryset.filter(**{f"{sorting_field}__lt": start_cursor}).exists()
        )
    else:
        has_next_page = False
        has_previous_page = False

    if start_cursor:
        start_cursor = encode_cursor(str(start_cursor))

    if end_cursor:
        end_cursor = encode_cursor(str(end_cursor))

    edges = [
        Node(
            cursor=encode_cursor(str(getattr(item, sorting_field))),
            node=item,
        )
        for item in items
    ]

    return Page(
        edges=edges,
        page_info=PageInfo(
            count=len(edges),
            start_cursor=start_cursor,
            end_cursor=end_cursor,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
        ),
    )
