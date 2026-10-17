"""Streaming and structured importers with automatic format selection."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Protocol, cast

import yaml

from .exceptions import DataImportError
from .models import RawRecord


class Importer(Protocol):
    def read(self, path: Path) -> Iterator[tuple[int, RawRecord]]: ...


class CsvImporter:
    """Read CSV one record at a time without materializing the dataset."""

    def read(self, path: Path) -> Iterator[tuple[int, RawRecord]]:
        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames is None:
                    raise DataImportError("CSV header is missing")
                for line_number, row in enumerate(reader, start=2):
                    yield line_number, dict(row)
        except DataImportError:
            raise
        except (OSError, UnicodeError, csv.Error) as error:
            raise DataImportError(f"Cannot read CSV file: {path}") from error


class JsonLinesImporter:
    """Stream newline-delimited JSON objects."""

    def read(self, path: Path) -> Iterator[tuple[int, RawRecord]]:
        try:
            with path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if not line.strip():
                        continue
                    try:
                        value = json.loads(line)
                    except json.JSONDecodeError as error:
                        raise DataImportError(
                            f"Invalid JSON at line {line_number}"
                        ) from error
                    if not isinstance(value, dict):
                        raise DataImportError(f"JSON line {line_number} must be an object")
                    yield line_number, cast(RawRecord, value)
        except DataImportError:
            raise
        except (OSError, UnicodeError) as error:
            raise DataImportError(f"Cannot read JSON Lines file: {path}") from error


class StructuredImporter:
    """Read a JSON/YAML array; intended for moderate structured documents."""

    def __init__(self, format_name: str) -> None:
        self._format_name = format_name

    def read(self, path: Path) -> Iterator[tuple[int, RawRecord]]:
        try:
            with path.open("r", encoding="utf-8") as file:
                data: Any = json.load(file) if self._format_name == "json" else yaml.safe_load(file)
        except (json.JSONDecodeError, yaml.YAMLError) as error:
            raise DataImportError(f"Invalid {self._format_name.upper()} document") from error
        except (OSError, UnicodeError) as error:
            raise DataImportError(f"Cannot read input file: {path}") from error
        if not isinstance(data, list):
            raise DataImportError("Structured input must contain an array of records")
        for position, value in enumerate(data, start=1):
            if not isinstance(value, dict):
                raise DataImportError(f"Record {position} must be an object")
            yield position, cast(RawRecord, value)


def importer_for(path: Path, configured_format: str = "auto") -> Importer:
    format_name = configured_format
    if format_name == "auto":
        format_name = path.suffix.lower().lstrip(".")
    if format_name == "csv":
        return CsvImporter()
    if format_name == "jsonl":
        return JsonLinesImporter()
    if format_name in {"json", "yaml", "yml"}:
        return StructuredImporter("yaml" if format_name in {"yaml", "yml"} else "json")
    raise DataImportError(f"Unsupported input format: {format_name or '<none>'}")

