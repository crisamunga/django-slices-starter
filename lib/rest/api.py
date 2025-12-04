import logging
from typing import Any

import ninja.errors
from django.http import HttpRequest
from django.utils.translation import gettext as _
from ninja import NinjaAPI
from ninja.security import HttpBearer

import lib.errors

from . import error_handlers
from .stoplight import StoplightElements

logger = logging.getLogger(__name__)


class BearerMiddlewareAuthenticator(HttpBearer):
    def __call__(self, request: HttpRequest) -> Any:
        return self.authenticate(request=request)

    def authenticate(self, request: HttpRequest, token: str | None = None) -> Any:
        # We will replace this eventually
        if request.user and request.user.is_authenticated:
            if not request.user.is_active:
                raise lib.errors.UnauthenticatedError(
                    code="account_deactivated",
                    message=_("Your account has been deactivated."),
                )
            return request.user
        raise lib.errors.UnauthenticatedError


def create_api(
    *,
    app_name: str,
    urls_namespace: str = "api",
) -> NinjaAPI:
    """Create the API instance with the BearerMiddlewareAuthenticator."""
    app = NinjaAPI(
        auth=BearerMiddlewareAuthenticator(),
        urls_namespace=urls_namespace,
        title=app_name,
        docs=StoplightElements(),
    )

    app.add_exception_handler(ExceptionGroup, error_handlers.error_group)
    app.add_exception_handler(ninja.errors.ValidationError, error_handlers.invalid_input)
    app.add_exception_handler(lib.errors.BaseError, error_handlers.standard_error)
    app.add_exception_handler(Exception, error_handlers.unexpected_error)

    return app
