import logging
import os

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

MONITORING_OTLP_TRACING_ENDPOINT = os.getenv("MONITORING_OTLP_TRACING_ENDPOINT")
MONITORING_OTLP_TRACING_PROTOCOL = os.getenv("MONITORING_OTLP_TRACING_PROTOCOL")
MONITORING_OTLP_LOGS_ENDPOINT = os.getenv("MONITORING_OTLP_LOGS_ENDPOINT")
MONITORING_OTLP_LOGS_PROTOCOL = os.getenv("MONITORING_OTLP_LOGS_PROTOCOL")
MONITORING_OTLP_METRICS_ENDPOINT = os.getenv("MONITORING_OTLP_METRICS_ENDPOINT")
MONITORING_OTLP_METRICS_PROTOCOL = os.getenv("MONITORING_OTLP_METRICS_PROTOCOL")


if MONITORING_OTLP_TRACING_PROTOCOL == "http":
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
else:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore


if MONITORING_OTLP_LOGS_PROTOCOL == "http":
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
else:
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter  # type: ignore

if MONITORING_OTLP_METRICS_PROTOCOL == "http":
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
else:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter  # type: ignore


APP_NAME = os.environ["APP_NAME"]

logging.basicConfig(level=logging.DEBUG)
# Optional: metrics and logs can be added here too

# Set up resource to tag the service
resource = Resource(attributes={SERVICE_NAME: APP_NAME})

# Set up tracing
tracer_provider = TracerProvider(resource=resource)
tracing_exporter = OTLPSpanExporter(endpoint=MONITORING_OTLP_TRACING_ENDPOINT)
span_processor = BatchSpanProcessor(tracing_exporter)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

# Setup logs
logger_provider = LoggerProvider(resource=resource)
logger_exporter = OTLPLogExporter(endpoint=MONITORING_OTLP_LOGS_ENDPOINT)
log_processor = BatchLogRecordProcessor(logger_exporter)
set_logger_provider(logger_provider)

# Setup metrics
metric_exporter = OTLPMetricExporter(endpoint=MONITORING_OTLP_METRICS_ENDPOINT)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)


DjangoInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()
PsycopgInstrumentor().instrument(enable_commenter=True, commenter_options={})
RequestsInstrumentor().instrument()
