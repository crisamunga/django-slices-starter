from dataclasses import dataclass

from django.http import HttpRequest, HttpResponse


@dataclass(frozen=True)
class Context:
    request: HttpRequest
    response: HttpResponse
