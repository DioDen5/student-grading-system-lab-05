"""Fail-fast YAML configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import yaml

from .exceptions import ConfigurationError
from .models import (
    AppConfig,
    InputConfig,
    LoggingConfig,
    OutputConfig,
    ProcessingConfig,
)

SUPPORTED_FORMATS = {"auto", "csv", "json", "jsonl", "yaml", "yml"}
LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"Configuration section '{name}' must be a mapping")
    return cast(dict[str, Any], value)


def _resolve(base: Path, value: object) -> Path:
    path = Path(str(value)).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def _parse_bool(value: object, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    raise ConfigurationError(f"{name} must be a boolean")


def load_config(path: Path, *, environ: dict[str, str] | None = None) -> AppConfig:
    """Load YAML, apply safe environment overrides, and validate eagerly."""
    env = os.environ if environ is None else environ
    try:
        with path.open("r", encoding="utf-8") as file:
            raw_object = yaml.safe_load(file)
    except FileNotFoundError as error:
        raise ConfigurationError(f"Configuration file not found: {path}") from error
    except (OSError, UnicodeError) as error:
        raise ConfigurationError(f"Cannot read configuration: {path}") from error
    except yaml.YAMLError as error:
        raise ConfigurationError("Invalid YAML configuration") from error

    root = _mapping(raw_object, "root")
    try:
        input_raw = _mapping(root["input"], "input")
        output_raw = _mapping(root["output"], "output")
        processing_raw = _mapping(root["processing"], "processing")
        logging_raw = _mapping(root["logging"], "logging")
        base = path.resolve().parent
        disciplines_raw = processing_raw["allowed_disciplines"]
        if not isinstance(disciplines_raw, list):
            raise ConfigurationError("allowed_disciplines must be a list")

        input_path_value = env.get("SG_INPUT_PATH", str(input_raw["path"]))
        output_path_value = env.get("SG_OUTPUT_PATH", str(output_raw["path"]))
        passing_value = env.get("SG_PASSING_GRADE", str(processing_raw["passing_grade"]))
        skip_value: object = env.get("SG_SKIP_INVALID", processing_raw["skip_invalid"])
        config = AppConfig(
            schema_version=int(root.get("schema_version", 1)),
            input=InputConfig(
                path=_resolve(base, input_path_value),
                format=str(input_raw.get("format", "auto")).lower(),
            ),
            output=OutputConfig(
                path=_resolve(base, output_path_value),
                backup_existing=_parse_bool(
                    output_raw.get("backup_existing", False), "backup_existing"
                ),
                summary_path=_resolve(base, output_raw["summary_path"]),
            ),
            processing=ProcessingConfig(
                allowed_disciplines=tuple(str(item).strip() for item in disciplines_raw),
                passing_grade=float(passing_value),
                skip_invalid=_parse_bool(skip_value, "skip_invalid"),
            ),
            logging=LoggingConfig(
                level=str(logging_raw.get("level", "INFO")).upper(),
                path=_resolve(base, logging_raw["path"]),
                error_records_path=_resolve(base, logging_raw["error_records_path"]),
                max_bytes=int(logging_raw.get("max_bytes", 1_000_000)),
                backup_count=int(logging_raw.get("backup_count", 3)),
            ),
        )
    except ConfigurationError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigurationError("Configuration structure or value is invalid") from error

    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    if config.schema_version != 1:
        raise ConfigurationError("Unsupported configuration schema_version")
    if config.input.format not in SUPPORTED_FORMATS:
        raise ConfigurationError(f"Unsupported input format: {config.input.format}")
    if not config.input.path.is_file():
        raise ConfigurationError(f"Input file not found: {config.input.path}")
    if not config.processing.allowed_disciplines or any(
        not item for item in config.processing.allowed_disciplines
    ):
        raise ConfigurationError("allowed_disciplines must contain non-empty values")
    if not 0 <= config.processing.passing_grade <= 100:
        raise ConfigurationError("passing_grade must be between 0 and 100")
    if config.logging.level not in LOG_LEVELS:
        raise ConfigurationError(f"Unsupported logging level: {config.logging.level}")
    if config.logging.max_bytes <= 0 or config.logging.backup_count < 0:
        raise ConfigurationError("Logging rotation values are invalid")

