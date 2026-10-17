from __future__ import annotations

import json
from pathlib import Path

import pytest

from student_grading_io.exceptions import DataImportError
from student_grading_io.readers import (
    CsvImporter,
    JsonLinesImporter,
    StructuredImporter,
    importer_for,
)


def test_csv_streaming_reader(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("student_id,name,discipline,grade\n1,A B,Databases,80\n", encoding="utf-8")
    iterator = CsvImporter().read(path)
    assert iter(iterator) is iterator
    assert list(iterator) == [(2, {"student_id": "1", "name": "A B", "discipline": "Databases", "grade": "80"})]


def test_jsonl_and_invalid_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "data.jsonl"
    path.write_text('\n{"student_id": 1}\n', encoding="utf-8")
    assert list(JsonLinesImporter().read(path)) == [(2, {"student_id": 1})]
    path.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(DataImportError, match="line 1") as caught:
        list(JsonLinesImporter().read(path))
    assert caught.value.__cause__ is not None
    path.write_text("[]\n", encoding="utf-8")
    with pytest.raises(DataImportError, match="must be an object"):
        list(JsonLinesImporter().read(path))


@pytest.mark.parametrize("suffix", ["json", "yaml", "yml"])
def test_structured_importers_and_factory(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f"data.{suffix}"
    if suffix == "json":
        path.write_text(json.dumps([{"student_id": 1}]), encoding="utf-8")
    else:
        path.write_text("- student_id: 1\n", encoding="utf-8")
    assert list(importer_for(path).read(path)) == [(1, {"student_id": 1})]


def test_reader_errors(tmp_path: Path) -> None:
    with pytest.raises(DataImportError):
        list(CsvImporter().read(tmp_path / "missing.csv"))
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(DataImportError, match="header"):
        list(CsvImporter().read(empty))
    invalid = tmp_path / "bad.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(DataImportError, match="Invalid JSON"):
        list(StructuredImporter("json").read(invalid))
    scalar = tmp_path / "scalar.yaml"
    scalar.write_text("value", encoding="utf-8")
    with pytest.raises(DataImportError, match="array"):
        list(StructuredImporter("yaml").read(scalar))
    array = tmp_path / "array.json"
    array.write_text("[1]", encoding="utf-8")
    with pytest.raises(DataImportError, match="must be an object"):
        list(StructuredImporter("json").read(array))
    with pytest.raises(DataImportError, match="Unsupported"):
        importer_for(tmp_path / "data.xml")

