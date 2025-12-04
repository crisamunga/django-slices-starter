from typing import Any

from allauth.headless.tokens.sessions import SessionTokenStrategy
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest

# Override this to customize token creation / payload


class TokenStrategy(SessionTokenStrategy):
    def create_access_token(self, request: HttpRequest) -> Any | str:
        return super().create_access_token(request)

    def create_access_token_payload(self, request: HttpRequest) -> Any | dict[str, Any] | None:
        return super().create_access_token_payload(request)

    def create_session_token(self, request: HttpRequest) -> Any | str:
        return super().create_session_token(request)

    def lookup_session(self, session_token: str) -> Any | SessionBase | None:
        return super().lookup_session(session_token)
