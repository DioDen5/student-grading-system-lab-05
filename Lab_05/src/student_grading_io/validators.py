"""Boundary validation and conversion to the domain model."""

from __future__ import annotations

from math import isfinite

from .exceptions import RecordValidationError
from .models import GradeRecord, RawRecord


def _error(
    message: str,
    *,
    line_number: int,
    field: str,
    raw_record: RawRecord,
    cause: Exception | None = None,
) -> RecordValidationError:
    error = RecordValidationError(
        message,
        line_number=line_number,
        field=field,
        raw_record=dict(raw_record),
    )
    if cause is not None:
        error.__cause__ = cause
    return error


def parse_grade_record(
    raw: RawRecord,
    *,
    line_number: int,
    allowed_disciplines: tuple[str, ...],
) -> GradeRecord:
    try:
        student_id = int(raw["student_id"])
    except (KeyError, TypeError, ValueError) as cause:
        raise _error(
            "student_id must be an integer",
            line_number=line_number,
            field="student_id",
            raw_record=raw,
            cause=cause,
        ) from cause
    if student_id <= 0:
        raise _error(
            "student_id must be positive",
            line_number=line_number,
            field="student_id",
            raw_record=raw,
        )

    name = str(raw.get("name", "")).strip()
    if not name or len(name.split()) < 2:
        raise _error(
            "name must contain at least two words",
            line_number=line_number,
            field="name",
            raw_record=raw,
        )

    discipline = str(raw.get("discipline", "")).strip()
    if discipline not in allowed_disciplines:
        raise _error(
            f"discipline must be one of: {', '.join(allowed_disciplines)}",
            line_number=line_number,
            field="discipline",
            raw_record=raw,
        )

    try:
        grade = float(raw["grade"])
    except (KeyError, TypeError, ValueError) as cause:
        raise _error(
            "grade must be numeric",
            line_number=line_number,
            field="grade",
            raw_record=raw,
            cause=cause,
        ) from cause
    if not isfinite(grade) or not 0 <= grade <= 100:
        raise _error(
            "grade must be a finite number between 0 and 100",
            line_number=line_number,
            field="grade",
            raw_record=raw,
        )

    return GradeRecord(student_id, name, discipline, grade)

