"""Domain-specific exception hierarchy for reliable data processing."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base exception for controlled application failures."""


class ConfigurationError(ApplicationError):
    """Configuration is missing, malformed, or violates its contract."""


class DataError(ApplicationError):
    """Base exception for import, validation, and export errors."""


class DataImportError(DataError):
    """Input data cannot be opened or decoded."""


class RecordValidationError(DataError):
    """A single external record violates the domain schema."""

    def __init__(
        self,
        message: str,
        *,
        line_number: int | None = None,
        field: str | None = None,
        raw_record: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.field = field
        self.raw_record = raw_record


class DataExportError(DataError):
    """Output cannot be serialized or atomically committed."""

