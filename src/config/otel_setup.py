import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

APP_OTLP_COLLECTOR_ENDPOINT = os.getenv("APP_OTLP_COLLECTOR_ENDPOINT")

logging.basicConfig(level=logging.DEBUG)
# Optional: metrics and logs can be added here too

# Set up resource to tag the service
resource = Resource(attributes={SERVICE_NAME: "raconteury"})

# Set up tracer provider
tracer_provider = TracerProvider(resource=resource)

# Set up span exporter (OTLP -> Collector or backend like Jaeger)
otlp_exporter = OTLPSpanExporter(endpoint=f"{APP_OTLP_COLLECTOR_ENDPOINT}/v1/traces")  # default OTLP HTTP port

# Batch processor to send spans
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Set the default tracer provider
trace.set_tracer_provider(tracer_provider)

DjangoInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()
PsycopgInstrumentor().instrument(enable_commenter=True, commenter_options={})
RequestsInstrumentor().instrument()
