from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Field, Schema
from ninja.pagination import AsyncPaginationBase
from pydantic import model_validator

from lib.models import BaseModel
from lib.pagination import paginate

from .urls import set_query_params

DEFAULT_LIMIT = settings.API_PAGINATION_MAX_LIMIT


class PageInfo(Schema):
    count: int
    next: str | None
    previous: str | None
    first: str | None
    last: str | None


class CursorPagination[T: BaseModel](AsyncPaginationBase):
    # only `skip` param, defaults to 5 per page

    class Input(Schema):
        first: int | None = Field(
            None,
            alias="pagination[first]",
            description=(
                "Number of items to return. Used when paginating forwards. Can't be used with 'last' and 'before'"
            ),
        )
        after: str | None = Field(
            None,
            alias="pagination[after]",
            description="Cursor to use when paginating forwards. Can only be used with 'first'",
        )
        last: int | None = Field(
            None,
            alias="pagination[last]",
            description=(
                "Number of items to return. Used when paginating backwards. Can't be used with 'first' and 'after'"
            ),
        )
        before: str | None = Field(
            None,
            alias="pagination[before]",
            description="Cursor to use when paginating backwards. Can only be used with 'last'",
        )

        @model_validator(mode="after")
        def validate_data(self: "CursorPagination.Input") -> "CursorPagination.Input":
            if self.first is not None and self.last is not None:
                raise ValueError("Cannot use both 'first' and 'last' at the same time.")
            if self.after is not None and self.before is not None:
                raise ValueError("Cannot use both 'after' and 'before' at the same time.")
            if self.first is not None and self.before is not None:
                raise ValueError("Cannot use both 'first' and 'before' at the same time.")
            if self.last is not None and self.after is not None:
                raise ValueError("Cannot use both 'last' and 'after' at the same time.")
            if self.first is not None and self.first <= 0:
                raise ValueError("Value for 'first' must be greater than 0.")
            if self.last is not None and self.last <= 0:
                raise ValueError("Value for 'last' must be greater than 0.")
            return self

    class Output(Schema):
        link: str
        data: list[Any]
        pagination: PageInfo

    items_attribute: str = "data"

    def paginate_queryset(self, queryset: QuerySet[T], pagination: Any, request: HttpRequest, **params: Any) -> Any:
        pass  # pragma: no cover

    async def apaginate_queryset(
        self, queryset: QuerySet[T], pagination: Input, request: HttpRequest, **params: Any
    ) -> dict[str, Any]:
        url = request.path
        params = request.GET
        result = await paginate(
            queryset,
            cursor=pagination.after or pagination.before,
            limit=pagination.first or pagination.last or DEFAULT_LIMIT,
            forward=pagination.last is None,
        )
        records = [e.node for e in result.edges]
        limit = pagination.first or pagination.last or DEFAULT_LIMIT

        count = result.page_info.count
        next_ = (
            set_query_params(
                url,
                params=params
                | {
                    "pagination[first]": limit,
                    "pagination[after]": result.page_info.end_cursor,
                    "pagination[last]": None,
                    "pagination[before]": None,
                },
            )
            if result.page_info.has_next_page
            else None
        )
        previous = (
            set_query_params(
                url,
                params=params
                | {
                    "pagination[last]": limit,
                    "pagination[before]": result.page_info.start_cursor,
                    "pagination[first]": None,
                    "pagination[after]": None,
                },
            )
            if result.page_info.has_previous_page
            else None
        )
        first = (
            set_query_params(
                url,
                params=params
                | {
                    "pagination[first]": limit,
                    "pagination[after]": None,
                    "pagination[last]": None,
                    "pagination[before]": None,
                },
            )
            if result.page_info.count > 0
            else None
        )
        last = (
            set_query_params(
                url,
                params=params
                | {
                    "pagination[last]": limit,
                    "pagination[before]": None,
                    "pagination[first]": None,
                    "pagination[after]": None,
                },
            )
            if result.page_info.count > 0
            else None
        )

        return {
            "link": url,
            "data": records,
            "pagination": {
                "count": count,
                "next": next_,
                "previous": previous,
                "first": first,
                "last": last,
            },
        }
