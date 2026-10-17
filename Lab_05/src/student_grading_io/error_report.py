"""CSV error report used by tolerant processing."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, Protocol, TextIO

from .exceptions import RecordValidationError


class _CsvWriter(Protocol):
    def writerow(self, row: Iterable[Any]) -> Any: ...


class ErrorCsvWriter:
    """Context manager that guarantees closure of the invalid-record report."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._file: TextIO | None = None
        self._writer: _CsvWriter | None = None

    def __enter__(self) -> ErrorCsvWriter:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(("line_number", "field", "message", "raw_record"))
        return self

    def write(self, error: RecordValidationError) -> None:
        if self._writer is None:
            raise RuntimeError("ErrorCsvWriter must be used inside with")
        self._writer.writerow(
            (error.line_number, error.field, str(error), repr(error.raw_record or {}))
        )

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if self._file is not None:
            self._file.close()
        return False
