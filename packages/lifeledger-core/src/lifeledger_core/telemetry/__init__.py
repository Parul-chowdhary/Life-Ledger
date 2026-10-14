"""
LifeLedger Structured Telemetry & Audit Logger.
Generates structured JSON logs, redacts sensitive tokens/passwords,
and records auditable event entries.
"""
import json
import logging
import sys
import time
from typing import Any, Dict, Optional

SENSITIVE_KEYS = {"password", "secret", "token", "key", "authorization", "cookie", "mfa_secret"}


def redact_sensitive_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively redacts sensitive keys from log dictionaries."""
    sanitized = {}
    for k, v in data.items():
        if any(s in k.lower() for s in SENSITIVE_KEYS):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = redact_sensitive_dict(v)
        else:
            sanitized[k] = v
    return sanitized


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_entry["data"] = redact_sensitive_dict(record.extra_data)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def get_logger(name: str = "lifeledger") -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger("lifeledger.core")
