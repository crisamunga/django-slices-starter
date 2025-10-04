import logging
from typing import Any

import ninja.errors
from django.utils.translation import gettext_lazy as _
from ninja import NinjaAPI
from ninja.security import HttpBearer

import lib.errors
import lib.messages
from lib.types import Request

from . import error_handlers
from .stoplight import StoplightElements

logger = logging.getLogger(__name__)


class BearerMiddlewareAuthenticator(HttpBearer):
    def __call__(self, request: Request) -> Any:  # type: ignore
        return self.authenticate(request=request)

    def authenticate(self, request: Request, token: str | None = None) -> Any:  # type: ignore
        # We will replace this eventually
        if request.user and request.user.is_authenticated:
            if not request.user.is_active:
                raise lib.errors.UnauthenticatedError(
                    message=lib.messages.get_message(
                        code="account_deactivated",
                        message=_("Your account has been deactivated."),
                    )
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

    app.add_exception_handler(lib.errors.UnauthenticatedError, error_handlers.not_authenticated)
    app.add_exception_handler(lib.errors.AuthorizationError, error_handlers.authorization_failed)
    app.add_exception_handler(lib.errors.InputError, error_handlers.invalid_input_single)
    app.add_exception_handler(lib.errors.InputErrorGroup, error_handlers.invalid_input_group)
    app.add_exception_handler(ninja.errors.ValidationError, error_handlers.invalid_input)
    app.add_exception_handler(lib.errors.NotFoundError, error_handlers.not_found)
    app.add_exception_handler(lib.errors.UserError, error_handlers.user_error)
    app.add_exception_handler(Exception, error_handlers.unexpected_error)

    return app
