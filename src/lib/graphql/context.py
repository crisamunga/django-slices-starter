from dataclasses import dataclass

from django.http import HttpResponse

from lib.types import AuthenticatedRequest


@dataclass(frozen=True)
class Context:
    request: AuthenticatedRequest
    response: HttpResponse
