"""Structured logging configuration for Oqteris.

Provides rotating file logs and console logging with automatic scrubbing
of potential credentials, private keys, and passwords.
"""

from __future__ import annotations

import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from oqteris.platform.storage import get_storage_manager

# Redaction patterns for sensitive data
SENSITIVE_PATTERNS = [
    re.compile(r"(password\s*[:=]\s*)['\"]?([^'\"\s]+)['\"]?", re.IGNORECASE),
    re.compile(r"(pin\s*[:=]\s*)['\"]?([^'\"\s]+)['\"]?", re.IGNORECASE),
    re.compile(r"(private_key\s*[:=]\s*)['\"]?([^'\"\s]+)['\"]?", re.IGNORECASE),
    re.compile(r"(BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY[\s\S]+?END\s+(?:RSA\s+)?PRIVATE\s+KEY)", re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Filters log records to prevent leaking passwords, keys, or credentials."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in SENSITIVE_PATTERNS:
                msg = pattern.sub(r"\1[REDACTED]", msg)
            record.msg = msg
        return True


def setup_logging(
    log_level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 5,
) -> None:
    """Configure rotating file and console logging."""
    storage = get_storage_manager()
    log_file = storage.logs_dir / "oqteris.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if called multiple times
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sensitive_filter = SensitiveDataFilter()

    # Rotating file handler
    try:
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not initialize file logger: {e}", file=sys.stderr)

    # Console stream handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)

    logging.getLogger("oqteris").info("Logging initialized. Log file: %s", log_file)
