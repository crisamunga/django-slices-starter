import logging
from typing import ClassVar

from lib import jsonutils as json

_default_keys = {
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


def _get_extras(record: logging.LogRecord) -> dict[str, str]:
    extras = {}
    for key, value in record.__dict__.items():
        if key not in _default_keys:
            extras[key] = str(value)
    return extras


class JSONFormatter(logging.Formatter):
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
        } | _get_extras(record)
        return json.dumps(log_record)


class VerboseFormatter(logging.Formatter):
    # Adapted from: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    # Posted by Sergey Pleshakov, modified by community. See post 'Timeline' for change history
    # Retrieved 2025-11-27, License - CC BY-SA 4.0
    grey = "\x1b[38;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_header = "\nLOG ENTRY: {asctime} | {levelname} | {name} | [ {pathname}:{lineno} ] "
    log_content = "\n{message}\n{extras}"

    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: grey + log_header + reset + log_content,
        logging.INFO: cyan + log_header + reset + log_content,
        logging.WARNING: yellow + log_header + reset + log_content,
        logging.ERROR: red + log_header + reset + log_content,
        logging.CRITICAL: bold_red + log_header + reset + log_content,
    }

    def format(self, record: logging.LogRecord) -> str:
        extras = _get_extras(record)
        extras_str = "\n".join(f"{key}: {value}" for key, value in extras.items())
        record.extras = extras_str
        log_format = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_format, style="{", datefmt=self.datefmt)
        return formatter.format(record)
