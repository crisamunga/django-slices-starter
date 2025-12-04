# ------------------------------------------------------------------------------------------------
# MONITORING SETTINGS
#
# Environment variables used:
#   MONITORING_PYROSCOPE_URL            - URL of the Pyroscope server for performance profiling
#   MONITORING_OTLP_LOGS_ENDPOINT       - OTLP endpoint for logs
#   MONITORING_OTLP_LOGS_PROTOCOL       - OTLP protocol for logs. Either 'http' or 'grpc'.
#   MONITORING_OTLP_TRACING_ENDPOINT    - OTLP endpoint for traces
#   MONITORING_OTLP_TRACING_PROTOCOL    - OTLP protocol for traces. Either 'http' or 'grpc'.
# ------------------------------------------------------------------------------------------------

import os

from . import deployment

MONITORING_PYROSCOPE_URL = os.getenv("MONITORING_PYROSCOPE_URL")

if MONITORING_PYROSCOPE_URL and not deployment.TESTING:
    import pyroscope

    pyroscope.configure(
        application_name=deployment.APP_NAME,
        server_address=MONITORING_PYROSCOPE_URL,
    )

__all__ = []
