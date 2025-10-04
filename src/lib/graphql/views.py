from typing import Any

from django.http import HttpRequest, HttpResponse
from graphql import GraphQLError
from strawberry.django import views
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from lib.errors import BaseError, InputError, InputErrorGroup
from lib.monitoring import trace_async_function
from lib.types import AuthenticatedRequest

from .context import Context


class AsyncGraphQLView(views.AsyncGraphQLView):
    async def get_context(self, request: AuthenticatedRequest, response: HttpResponse) -> Context:  # type: ignore
        return Context(
            request=request,
            response=response,
        )

    async def process_result(self, request: AuthenticatedRequest, result: ExecutionResult) -> GraphQLHTTPResponse:  # type: ignore
        for error in result.errors or []:
            if not error.original_error:
                continue
            if not error.extensions:
                error.extensions = {}
            if isinstance(error.original_error, GraphQLError):
                error.extensions["code"] = "graphql_error"
                error.extensions["message"] = "A graphql error occurred."
                error.extensions["original_error"] = error.message
                error.extensions["original_error_code"] = type(error.original_error).__name__
            elif not isinstance(error.original_error, BaseError) and not isinstance(
                error.original_error, InputErrorGroup
            ):
                error.extensions["code"] = "unexpected_error"
                error.extensions["message"] = "An unexpected error occurred."
                error.extensions["originalError"] = error.message
                error.extensions["originalErrorCode"] = type(error.original_error).__name__
                error.message = "An unexpected error occurred."
            if isinstance(error.original_error, BaseError):
                error.message = error.original_error.message.message
                error.extensions["code"] = error.original_error.message.code
                error.extensions["message"] = error.original_error.message.message
            if isinstance(error.original_error, InputError):
                error.extensions["fields"] = [
                    {
                        "path": error.original_error.path,
                        "message": error.original_error.message.message,
                        "code": error.original_error.message.code,
                    }
                ]
            if isinstance(error.original_error, InputErrorGroup):
                fields = []
                for input_error in error.original_error.exceptions:
                    fields.append(
                        {
                            "path": input_error.path,
                            "message": input_error.message.message,
                            "code": input_error.message.code,
                        }
                    )
                error.extensions["fields"] = fields
                error.extensions["code"] = "invalid_input"
                error.extensions["message"] = "Invalid input."

        return await super().process_result(request, result)

    @trace_async_function(name="graphql.dispatch")
    async def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        return await super().dispatch(request, *args, **kwargs)
