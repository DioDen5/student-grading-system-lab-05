"""Immutable records and configuration models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class GradeRecord:
    student_id: int
    name: str
    discipline: str
    grade: float

    @property
    def passed(self) -> bool:
        """Compatibility helper; the configured threshold is applied in services."""
        return self.grade >= 60

    def to_dict(self, *, passing_grade: float) -> dict[str, object]:
        result = asdict(self)
        result["passed"] = self.grade >= passing_grade
        return result


@dataclass(frozen=True, slots=True)
class InputConfig:
    path: Path
    format: str


@dataclass(frozen=True, slots=True)
class OutputConfig:
    path: Path
    backup_existing: bool
    summary_path: Path


@dataclass(frozen=True, slots=True)
class ProcessingConfig:
    allowed_disciplines: tuple[str, ...]
    passing_grade: float
    skip_invalid: bool


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str
    path: Path
    error_records_path: Path
    max_bytes: int
    backup_count: int


@dataclass(frozen=True, slots=True)
class AppConfig:
    schema_version: int
    input: InputConfig
    output: OutputConfig
    processing: ProcessingConfig
    logging: LoggingConfig


@dataclass(slots=True)
class ImportStatistics:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    passed: int = 0
    failed: int = 0
    exported: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


RawRecord = dict[str, Any]

