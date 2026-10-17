"""Reusable operation context manager with timing and exception diagnostics."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from collections.abc import Iterator
from time import perf_counter

logger = logging.getLogger(__name__)


@contextmanager
def logged_operation(name: str) -> Iterator[None]:
    logger.info("%s started", name)
    start = perf_counter()
    try:
        yield
    except Exception:
        logger.exception("%s failed", name)
        raise
    else:
        logger.info("%s finished in %.6f s", name, perf_counter() - start)

