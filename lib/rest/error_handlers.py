import logging

import ninja.errors
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext as _

import lib.errors

from . import resources

logger = logging.getLogger(__name__)


def standard_error(request: HttpRequest, exc: lib.errors.BaseError | type[lib.errors.BaseError]) -> HttpResponse:
    error_mapping: dict[type[lib.errors.BaseError], int] = {
        lib.errors.UnauthenticatedError: 401,
        lib.errors.AuthorizationError: 403,
        lib.errors.NotFoundError: 404,
        lib.errors.InputError: 422,
        lib.errors.UserError: 400,
    }
    code = next((code for type_, code in error_mapping.items() if isinstance(exc, type_)), 500)
    logger.info(exc, extra={"user": str(request.user)})
    detail = resources.ErrorResponse(
        errors=[
            resources.ErrorMessage(
                code=exc.code,
                message=exc.message,
                path=exc.path if isinstance(exc, lib.errors.InputError) else None,
            )
        ]
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(detail, status=code)


def unexpected_error(request: HttpRequest, exc: Exception | type[Exception]) -> HttpResponse:
    logger.error(exc, extra={"user": str(request.user)}, stack_info=True)
    detail = resources.ErrorResponse(
        errors=[
            resources.ErrorMessage(
                code="internal_error",
                message=_("An unexpected error occurred."),
                path=None,
            )
        ]
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=500,
    )


def invalid_input(
    request: HttpRequest, exc: ninja.errors.ValidationError | type[ninja.errors.ValidationError]
) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    errors = []
    for error in exc.errors:
        errors.append(
            resources.ErrorMessage(
                code=error["type"],
                message=error["msg"],
                path=error["loc"],
            )
        )
    detail = resources.ErrorResponse(
        errors=errors,
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=422,
    )


def error_group(request: HttpRequest, exc: ExceptionGroup | type[ExceptionGroup]) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})

    def get_errors_from_group(exc: ExceptionGroup) -> list[resources.ErrorMessage]:
        errors: list[resources.ErrorMessage] = []
        for error in exc.exceptions:
            if isinstance(error, ExceptionGroup):
                errors.extend(get_errors_from_group(error))
                continue
            errors.append(
                resources.ErrorMessage(
                    code=error.code if isinstance(error, lib.errors.BaseError) else "error",
                    message=error.message if isinstance(error, lib.errors.BaseError) else str(error),
                    path=error.path if isinstance(error, lib.errors.InputError) else None,
                )
            )
        return errors

    errors = get_errors_from_group(exc)  # type: ignore # ExceptionGroup type ambiguous for django ninja handler registration

    detail = resources.ErrorResponse(
        errors=errors,
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=422,
    )
