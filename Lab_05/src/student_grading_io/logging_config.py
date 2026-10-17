"""Configurable rotating diagnostics."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from .models import LoggingConfig


def configure_logging(config: LoggingConfig) -> None:
    config.path.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler = RotatingFileHandler(
        config.path,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logging.basicConfig(
        level=getattr(logging, config.level),
        handlers=[file_handler, stream_handler],
        force=True,
    )

