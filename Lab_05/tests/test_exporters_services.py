from __future__ import annotations

import json
from pathlib import Path
from types import TracebackType

import pytest

from student_grading_io.error_report import ErrorCsvWriter
from student_grading_io.exceptions import DataExportError, RecordValidationError
from student_grading_io.exporters import AtomicTextWriter, JsonExporter, write_summary
from student_grading_io.models import GradeRecord, ImportStatistics, RawRecord
from student_grading_io.services import import_grade_records


class FakeImporter:
    def __init__(self, records: list[tuple[int, RawRecord]]) -> None:
        self.records = records

    def read(self, path: Path):  # type: ignore[no-untyped-def]
        yield from self.records


def rows() -> list[tuple[int, RawRecord]]:
    return [
        (2, {"student_id": "1", "name": "Anna Koval", "discipline": "Databases", "grade": "80"}),
        (3, {"student_id": "bad", "name": "Wrong Id", "discipline": "Databases", "grade": "70"}),
        (4, {"student_id": "2", "name": "Oleh Melnyk", "discipline": "Databases", "grade": "50"}),
    ]


def test_tolerant_and_strict_processing(tmp_path: Path) -> None:
    stats = ImportStatistics()
    with ErrorCsvWriter(tmp_path / "errors.csv") as errors:
        result = list(
            import_grade_records(
                FakeImporter(rows()),
                tmp_path / "ignored.csv",
                allowed_disciplines=("Databases",),
                passing_grade=60,
                skip_invalid=True,
                statistics=stats,
                errors=errors,
            )
        )
    assert [item.student_id for item in result] == [1, 2]
    assert stats.to_dict() == {"total": 3, "valid": 2, "invalid": 1, "passed": 1, "failed": 1, "exported": 0}
    assert "student_id must be an integer" in (tmp_path / "errors.csv").read_text(encoding="utf-8")

    strict_stats = ImportStatistics()
    with ErrorCsvWriter(tmp_path / "strict-errors.csv") as errors:
        with pytest.raises(RecordValidationError):
            list(
                import_grade_records(
                    FakeImporter(rows()),
                    tmp_path / "ignored.csv",
                    allowed_disciplines=("Databases",),
                    passing_grade=60,
                    skip_invalid=False,
                    statistics=strict_stats,
                    errors=errors,
                )
            )
    assert strict_stats.total == 2
    assert strict_stats.invalid == 1


def test_json_export_atomic_backup_and_summary(tmp_path: Path) -> None:
    target = tmp_path / "records.json"
    target.write_text("old", encoding="utf-8")
    records = [GradeRecord(1, "Anna Koval", "Databases", 80)]
    count = JsonExporter(backup_existing=True).write(records, target, passing_grade=60)
    assert count == 1
    assert json.loads(target.read_text(encoding="utf-8"))[0]["passed"] is True
    assert target.with_suffix(".json.bak").read_text(encoding="utf-8") == "old"
    write_summary(tmp_path / "summary.json", {"valid": 1})
    assert json.loads((tmp_path / "summary.json").read_text(encoding="utf-8")) == {"valid": 1}


def test_atomic_writer_rolls_back_on_exception(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    target.write_text("stable", encoding="utf-8")
    with pytest.raises(RuntimeError):
        with AtomicTextWriter(target) as file:
            file.write("partial")
            raise RuntimeError("boom")
    assert target.read_text(encoding="utf-8") == "stable"
    assert not target.with_suffix(".txt.tmp").exists()


def test_error_writer_requires_context(tmp_path: Path) -> None:
    writer = ErrorCsvWriter(tmp_path / "errors.csv")
    with pytest.raises(RuntimeError):
        writer.write(RecordValidationError("bad"))


def test_atomic_writer_wraps_open_error(tmp_path: Path) -> None:
    directory_target = tmp_path / "out.json"
    directory_target.mkdir()
    writer = AtomicTextWriter(directory_target / "child" / "file.json")
    # Parent creation is supported; a directory at the temporary-file path is not.
    writer.temporary.parent.mkdir(parents=True)
    writer.temporary.mkdir()
    with pytest.raises(DataExportError):
        writer.__enter__()

