import logging

import ninja.errors
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

import lib.errors
import lib.messages

from . import resources

logger = logging.getLogger(__name__)


def not_authenticated(
    request: HttpRequest, exc: lib.errors.UnauthenticatedError | type[lib.errors.UnauthenticatedError]
) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    detail = resources.Response401(message=exc.message).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=401,
    )


def authorization_failed(
    request: HttpRequest, exc: lib.errors.AuthorizationError | type[lib.errors.AuthorizationError]
) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    detail = resources.Response403(message=exc.message).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=403,
    )


def unexpected_error(request: HttpRequest, exc: Exception | type[Exception]) -> HttpResponse:
    logger.error(exc, extra={"user": str(request.user)}, stack_info=True)
    detail = resources.Response500(
        message=lib.messages.get_message(code="unexpected_error", message=_("An unexpected error occurred."))
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
            resources.ErrorDetail(
                code=error["type"],
                message=error["msg"],
                path=error["loc"],
            )
        )
    detail = resources.Response422(
        message=lib.messages.get_message(code="invalid_input", message=_("Invalid input.")),
        errors=errors,
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=422,
    )


def invalid_input_single(
    request: HttpRequest, exc: lib.errors.InputError | type[lib.errors.InputError]
) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    errors = [
        resources.ErrorDetail(
            code=exc.message.code,
            message=exc.message.message,
            path=exc.path,
        )
    ]
    detail = resources.Response422(
        message=lib.messages.get_message(code="invalid_input", message=_("Invalid input.")),
        errors=errors,
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=422,
    )


def invalid_input_group(
    request: HttpRequest, exc: lib.errors.InputErrorGroup | type[lib.errors.InputErrorGroup]
) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    errors = []
    for error in exc.exceptions:
        errors.append(
            resources.ErrorDetail(
                code=error.message.code,
                message=error.message.message,
                path=error.path,
            )
        )
    detail = resources.Response422(
        message=lib.messages.get_message(code="invalid_input", message=_("Invalid input.")),
        errors=errors,
    ).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=422,
    )


def not_found(request: HttpRequest, exc: lib.errors.NotFoundError | type[lib.errors.NotFoundError]) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    detail = resources.Response404(message=exc.message).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=404,
    )


def user_error(request: HttpRequest, exc: lib.errors.UserError | type[lib.errors.UserError]) -> HttpResponse:
    logger.info(exc, extra={"user": str(request.user)})
    detail = resources.Response400(message=exc.message, errors=None).model_dump(mode="json", exclude_none=True)
    return JsonResponse(
        detail,
        status=400,
    )
