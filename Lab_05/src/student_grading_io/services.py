"""Strict/tolerant processing policy and streaming statistics."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

from .error_report import ErrorCsvWriter
from .exceptions import RecordValidationError
from .models import GradeRecord, ImportStatistics
from .readers import Importer
from .validators import parse_grade_record

logger = logging.getLogger(__name__)


def import_grade_records(
    importer: Importer,
    input_path: Path,
    *,
    allowed_disciplines: tuple[str, ...],
    passing_grade: float,
    skip_invalid: bool,
    statistics: ImportStatistics,
    errors: ErrorCsvWriter,
) -> Iterator[GradeRecord]:
    for line_number, raw in importer.read(input_path):
        statistics.total += 1
        try:
            record = parse_grade_record(
                raw,
                line_number=line_number,
                allowed_disciplines=allowed_disciplines,
            )
        except RecordValidationError as error:
            statistics.invalid += 1
            logger.warning(
                "Invalid record at line %s, field=%s: %s",
                error.line_number,
                error.field,
                error,
            )
            errors.write(error)
            if skip_invalid:
                continue
            raise
        statistics.valid += 1
        if record.grade >= passing_grade:
            statistics.passed += 1
        else:
            statistics.failed += 1
        yield record

