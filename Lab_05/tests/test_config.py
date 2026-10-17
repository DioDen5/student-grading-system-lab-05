from __future__ import annotations

from pathlib import Path

import pytest

from student_grading_io.config import load_config, validate_config
from student_grading_io.exceptions import ConfigurationError
from student_grading_io.models import (
    AppConfig,
    InputConfig,
    LoggingConfig,
    OutputConfig,
    ProcessingConfig,
)


def make_yaml(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def valid_yaml(input_name: str = "input.csv") -> str:
    return f"""
schema_version: 1
input:
  path: {input_name}
  format: auto
output:
  path: out.json
  backup_existing: false
  summary_path: summary.json
processing:
  allowed_disciplines: [Professional Python, Databases]
  passing_grade: 60
  skip_invalid: true
logging:
  level: INFO
  path: app.log
  error_records_path: errors.csv
  max_bytes: 1000
  backup_count: 2
"""


def test_load_config_and_environment_overrides(tmp_path: Path) -> None:
    (tmp_path / "input.csv").write_text("student_id,name,discipline,grade\n", encoding="utf-8")
    (tmp_path / "other.csv").write_text("student_id,name,discipline,grade\n", encoding="utf-8")
    path = make_yaml(tmp_path, valid_yaml())
    config = load_config(
        path,
        environ={"SG_INPUT_PATH": "other.csv", "SG_PASSING_GRADE": "70", "SG_SKIP_INVALID": "false"},
    )
    assert config.input.path == (tmp_path / "other.csv").resolve()
    assert config.processing.passing_grade == 70
    assert config.processing.skip_invalid is False


def test_missing_and_invalid_yaml(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="not found"):
        load_config(tmp_path / "missing.yaml")
    bad = make_yaml(tmp_path, "input: [")
    with pytest.raises(ConfigurationError, match="Invalid YAML"):
        load_config(bad)


@pytest.mark.parametrize(
    "replacement",
    [
        "schema_version: 2",
        "format: xml",
        "allowed_disciplines: []",
        "passing_grade: 150",
        "level: TRACE",
        "max_bytes: 0",
    ],
)
def test_invalid_config_values(tmp_path: Path, replacement: str) -> None:
    (tmp_path / "input.csv").write_text("student_id,name,discipline,grade\n", encoding="utf-8")
    text = valid_yaml()
    old = {
        "schema_version: 2": "schema_version: 1",
        "format: xml": "format: auto",
        "allowed_disciplines: []": "allowed_disciplines: [Professional Python, Databases]",
        "passing_grade: 150": "passing_grade: 60",
        "level: TRACE": "level: INFO",
        "max_bytes: 0": "max_bytes: 1000",
    }[replacement]
    path = make_yaml(tmp_path, text.replace(old, replacement))
    with pytest.raises(ConfigurationError):
        load_config(path)


def test_validate_missing_input_and_bad_structure(tmp_path: Path) -> None:
    path = make_yaml(tmp_path, "[]")
    with pytest.raises(ConfigurationError, match="root"):
        load_config(path)
    path = make_yaml(tmp_path, "input: {}")
    with pytest.raises(ConfigurationError, match="structure"):
        load_config(path)

    config = AppConfig(
        1,
        InputConfig(tmp_path / "missing.csv", "csv"),
        OutputConfig(tmp_path / "out.json", False, tmp_path / "summary.json"),
        ProcessingConfig(("Databases",), 60, True),
        LoggingConfig("INFO", tmp_path / "app.log", tmp_path / "errors.csv", 100, 1),
    )
    with pytest.raises(ConfigurationError, match="Input file"):
        validate_config(config)

