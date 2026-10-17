from __future__ import annotations

import logging
from pathlib import Path

import pytest

from student_grading_io.logging_config import configure_logging
from student_grading_io.main import main, run
from student_grading_io.models import LoggingConfig
from student_grading_io.operations import logged_operation


def write_project(tmp_path: Path, *, skip_invalid: bool = True) -> Path:
    (tmp_path / "data.csv").write_text(
        "student_id,name,discipline,grade\n"
        "1,Anna Koval,Databases,80\n"
        "bad,Wrong Id,Databases,70\n"
        "2,Oleh Melnyk,Databases,50\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.yaml"
    config.write_text(
        f"""
schema_version: 1
input: {{path: data.csv, format: auto}}
output:
  path: output.json
  backup_existing: true
  summary_path: summary.json
processing:
  allowed_disciplines: [Databases]
  passing_grade: 60
  skip_invalid: {str(skip_invalid).lower()}
logging:
  level: INFO
  path: app.log
  error_records_path: errors.csv
  max_bytes: 10000
  backup_count: 1
""",
        encoding="utf-8",
    )
    return config


def test_full_run_and_cli_return_codes(tmp_path: Path) -> None:
    config = write_project(tmp_path)
    stats = run(config)
    assert stats.total == 3
    assert stats.valid == 2
    assert stats.invalid == 1
    assert stats.exported == 2
    assert main(["--config", str(config)]) == 0
    assert main(["--config", str(tmp_path / "missing.yaml")]) == 1


def test_strict_run_fails_controlled(tmp_path: Path) -> None:
    config = write_project(tmp_path, skip_invalid=False)
    assert main(["--config", str(config)]) == 1
    assert not (tmp_path / "output.json.tmp").exists()


def test_logging_and_operation_context(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    config = LoggingConfig("INFO", tmp_path / "app.log", tmp_path / "errors.csv", 1000, 1)
    configure_logging(config)
    with logged_operation("success"):
        pass
    assert (tmp_path / "app.log").exists()

    with pytest.raises(ValueError):
        with logged_operation("failure"):
            raise ValueError("boom")
    logging.shutdown()

