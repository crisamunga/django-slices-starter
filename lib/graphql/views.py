from typing import Any

from django.http import HttpRequest, HttpResponse
from graphql import GraphQLError
from strawberry.django import views
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from lib.errors import BaseError, InputError
from lib.monitoring import trace_async_function

from .context import Context


class AsyncGraphQLView(views.AsyncGraphQLView):
    async def get_context(self, request: HttpRequest, response: HttpResponse) -> Context:  # type: ignore # Need to return context
        return Context(
            request=request,
            response=response,
        )

    async def process_result(self, request: HttpRequest, result: ExecutionResult) -> GraphQLHTTPResponse:  # noqa: C901 # Necessary complexity due to unmarshalling ExceptionGroup
        if not result.errors:
            return await super().process_result(request, result)

        remove_errors: list[int] = []
        add_errors: list[GraphQLError] = []

        for index, error in enumerate(result.errors):
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
                error.original_error, ExceptionGroup
            ):
                error.extensions["code"] = "unexpected_error"
                error.extensions["message"] = "An unexpected error occurred."
                error.extensions["originalError"] = error.message
                error.extensions["originalErrorCode"] = type(error.original_error).__name__
                error.message = "An unexpected error occurred."
            if isinstance(error.original_error, BaseError):
                error.message = error.original_error.message
                error.extensions["code"] = error.original_error.code
                error.extensions["message"] = error.original_error.message
            if isinstance(error.original_error, InputError):
                error.extensions["fields"] = [
                    {
                        "path": error.original_error.path,
                        "message": error.original_error.message,
                        "code": error.original_error.code,
                    }
                ]
            if isinstance(error.original_error, ExceptionGroup):
                remove_errors.append(index)

                def get_errors(root_error: GraphQLError, exc: ExceptionGroup) -> list[GraphQLError]:
                    errors: list[GraphQLError] = []
                    for input_error in exc.exceptions:
                        if isinstance(input_error, ExceptionGroup):
                            errors.extend(get_errors(root_error, input_error))
                            continue
                        ge = GraphQLError(
                            message=input_error.message if isinstance(input_error, BaseError) else str(input_error),
                            nodes=root_error.nodes,
                            source=root_error.source,
                            positions=root_error.positions,
                            path=root_error.path,
                            original_error=input_error,
                        )
                        if isinstance(input_error, BaseError):
                            ge.extensions = {
                                "code": input_error.code,
                                "message": input_error.message,
                                "path": input_error.path if isinstance(input_error, InputError) else None,
                            }
                        errors.append(ge)
                    return errors

                add_errors.extend(get_errors(error, error.original_error))
        for index in sorted(remove_errors, reverse=True):
            del result.errors[index]
        result.errors.extend(add_errors)

        return await super().process_result(request, result)

    @trace_async_function(name="graphql.dispatch")
    async def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        return await super().dispatch(request, *args, **kwargs)
