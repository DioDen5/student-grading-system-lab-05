"""Streaming JSON serialization with transactional atomic replacement."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import Literal, Protocol, TextIO

from .exceptions import DataExportError
from .models import GradeRecord


class Exporter(Protocol):
    def write(
        self, records: Iterable[GradeRecord], path: Path, *, passing_grade: float
    ) -> int: ...


class AtomicTextWriter:
    """Transaction-like context manager: replace target only after success."""

    def __init__(self, path: Path, *, backup_existing: bool = False) -> None:
        self.path = path
        self.backup_existing = backup_existing
        self.temporary = path.with_suffix(path.suffix + ".tmp")
        self.backup = path.with_suffix(path.suffix + ".bak")
        self._file: TextIO | None = None

    def __enter__(self) -> TextIO:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._file = self.temporary.open("w", encoding="utf-8", newline="")
        except OSError as error:
            raise DataExportError(f"Cannot create temporary output: {self.temporary}") from error
        return self._file

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if self._file is not None:
            self._file.close()
        if exc_type is not None:
            self.temporary.unlink(missing_ok=True)
            return False
        try:
            if self.backup_existing and self.path.exists():
                self.backup.unlink(missing_ok=True)
                self.path.replace(self.backup)
            self.temporary.replace(self.path)
        except OSError as error:
            self.temporary.unlink(missing_ok=True)
            if self.backup.exists() and not self.path.exists():
                self.backup.replace(self.path)
            raise DataExportError(f"Cannot commit output: {self.path}") from error
        return False


class JsonExporter:
    def __init__(self, *, backup_existing: bool = False) -> None:
        self.backup_existing = backup_existing

    def write(
        self,
        records: Iterable[GradeRecord],
        path: Path,
        *,
        passing_grade: float,
    ) -> int:
        count = 0
        try:
            with AtomicTextWriter(path, backup_existing=self.backup_existing) as file:
                file.write("[\n")
                for record in records:
                    if count:
                        file.write(",\n")
                    json.dump(
                        record.to_dict(passing_grade=passing_grade),
                        file,
                        ensure_ascii=False,
                        indent=2,
                    )
                    count += 1
                file.write("\n]\n")
        except DataExportError:
            raise
        except (OSError, TypeError, ValueError) as error:
            raise DataExportError(f"Cannot serialize output: {path}") from error
        return count


def write_summary(path: Path, summary: dict[str, int]) -> None:
    try:
        with AtomicTextWriter(path) as file:
            json.dump(summary, file, ensure_ascii=False, indent=2)
            file.write("\n")
    except DataExportError:
        raise
    except (OSError, TypeError, ValueError) as error:
        raise DataExportError(f"Cannot write summary: {path}") from error
