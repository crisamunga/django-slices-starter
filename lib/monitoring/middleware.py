from collections.abc import Awaitable, Callable
from time import time

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.http import HttpRequest, HttpResponse
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

tracer = trace.get_tracer(__name__)


class TelemetryMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response: Callable[[HttpRequest], Awaitable[HttpResponse]]) -> None:
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)
        # One-time configuration and initialization.

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        ctx = None

        if "Traceparent" in request.headers:
            carrier = {"traceparent": request.headers["Traceparent"]}
            ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

        with tracer.start_as_current_span(f"HTTP {request.method}", kind=trace.SpanKind.SERVER, context=ctx) as span:
            span.set_attribute("http.request.method", request.method or "UNKNOWN")
            span.set_attribute("http.route", request.path)
            span.set_attribute("http.request.url", request.build_absolute_uri())
            span.set_attribute("http.request.header.user_agent", request.headers.get("User-Agent", ""))
            start_time = time()
            response = await self.get_response(request)
            duration = time() - start_time
            span.set_attribute(
                "user.uuid",
                str(request.user.uuid) if request.user and request.user.is_authenticated else "anonymous",
            )
            span.set_attribute("http.response.duration", duration)
            span.set_attribute("http.response.status_code", response.status_code)

        return response
