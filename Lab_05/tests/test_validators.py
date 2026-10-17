from __future__ import annotations

import pytest

from student_grading_io.exceptions import RecordValidationError
from student_grading_io.validators import parse_grade_record

ALLOWED = ("Professional Python", "Databases")


def test_parse_valid_record_and_exception_chaining() -> None:
    record = parse_grade_record(
        {"student_id": "7", "name": "Denys Zastavnyi", "discipline": ALLOWED[0], "grade": "95"},
        line_number=2,
        allowed_disciplines=ALLOWED,
    )
    assert record.student_id == 7
    assert record.grade == 95
    assert record.to_dict(passing_grade=60)["passed"] is True
    assert record.passed is True

    with pytest.raises(RecordValidationError) as caught:
        parse_grade_record(
            {"student_id": "bad", "name": "A B", "discipline": ALLOWED[0], "grade": "80"},
            line_number=9,
            allowed_disciplines=ALLOWED,
        )
    assert isinstance(caught.value.__cause__, ValueError)
    assert caught.value.line_number == 9
    assert caught.value.field == "student_id"


@pytest.mark.parametrize(
    ("raw", "field"),
    [
        ({"student_id": "0", "name": "A B", "discipline": "Databases", "grade": "80"}, "student_id"),
        ({"student_id": "1", "name": "Anna", "discipline": "Databases", "grade": "80"}, "name"),
        ({"student_id": "1", "name": "A B", "discipline": "Networks", "grade": "80"}, "discipline"),
        ({"student_id": "1", "name": "A B", "discipline": "Databases", "grade": "bad"}, "grade"),
        ({"student_id": "1", "name": "A B", "discipline": "Databases", "grade": "101"}, "grade"),
        ({"student_id": "1", "name": "A B", "discipline": "Databases", "grade": "nan"}, "grade"),
    ],
)
def test_invalid_records(raw: dict[str, str], field: str) -> None:
    with pytest.raises(RecordValidationError) as caught:
        parse_grade_record(raw, line_number=4, allowed_disciplines=ALLOWED)
    assert caught.value.field == field
    assert caught.value.raw_record == raw

