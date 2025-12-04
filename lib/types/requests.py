from typing import TYPE_CHECKING

from django.http import HttpRequest as _HttpRequest

if TYPE_CHECKING:
    from core.models import AnonymousUser, User  # pragma: no cover


class Request(_HttpRequest):
    user: "User| AnonymousUser"
    auth: "User| AnonymousUser"


class AuthenticatedRequest(Request):
    user: "User"
    auth: "User"
