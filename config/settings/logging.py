# ------------------------------------------------------------------------------------------------
# LOGGING SETTINGS
#
# Environment variables used:
#   LOG_FILE        - Path to the log file (if using file logging)
#   LOG_HANDLERS    - Comma-separated list of log handlers ('console', 'file')
#   LOG_FORMAT      - Log format ('json' or 'verbose')
#   LOG_LEVEL       - Minimum logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
# ------------------------------------------------------------------------------------------------

import os

from opentelemetry._logs import get_logger_provider

from .deployment import BASE_DIR

LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))
LOG_HANDLERS = (os.getenv("LOG_METHOD") or "console").split(",")
LOG_FORMAT = os.getenv("LOG_FORMAT", "verbose")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": LOG_FORMAT,
        },
        "file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": LOG_FILE,
            "formatter": LOG_FORMAT,
        },
        "otel": {
            "class": "opentelemetry.sdk._logs.LoggingHandler",
            "logger_provider": get_logger_provider(),
            "formatter": "json",
        },
    },
    "root": {
        "handlers": LOG_HANDLERS,
        "level": LOG_LEVEL,
    },
    "loggers": {
        "asyncio": {
            "level": "WARNING",  # Suppress overly verbose logs from asyncio
        },
    },
    "formatters": {
        "json": {
            "()": "lib.logs.JSONFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "verbose": {
            "()": "lib.logs.VerboseFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
}


__all__ = ["LOGGING"]
