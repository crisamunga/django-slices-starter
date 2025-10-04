import logging
from typing import Any

from lib import jsonutils as json


class JSONFormatter(logging.Formatter):
    def _get_extras(self, record: logging.LogRecord) -> dict[str, Any]:
        default_keys = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "taskName",
        }
        extras = {}
        for key, value in record.__dict__.items():
            if key not in default_keys:
                extras[key] = value
        return extras

    def format(self, record: logging.LogRecord) -> str:
        # Convert the LogRecord to a dictionary
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "logger": record.name,
            # Include additional log attributes if needed
            "pathname": record.pathname,
            "lineno": record.lineno,
            "exc_info": self.formatException(record.exc_info) if record.exc_info else None,
        } | self._get_extras(record)
        return json.dumps(log_record)
