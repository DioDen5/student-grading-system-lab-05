"""Application composition root and command-line entry point."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from collections.abc import Sequence

from .config import load_config
from .error_report import ErrorCsvWriter
from .exceptions import ApplicationError
from .exporters import JsonExporter, write_summary
from .logging_config import configure_logging
from .models import ImportStatistics
from .operations import logged_operation
from .readers import importer_for
from .services import import_grade_records

logger = logging.getLogger(__name__)


def run(config_path: Path) -> ImportStatistics:
    config = load_config(config_path)
    configure_logging(config.logging)
    statistics = ImportStatistics()
    importer = importer_for(config.input.path, config.input.format)
    exporter = JsonExporter(backup_existing=config.output.backup_existing)

    with logged_operation("Student grading import/export"):
        with ErrorCsvWriter(config.logging.error_records_path) as error_writer:
            records = import_grade_records(
                importer,
                config.input.path,
                allowed_disciplines=config.processing.allowed_disciplines,
                passing_grade=config.processing.passing_grade,
                skip_invalid=config.processing.skip_invalid,
                statistics=statistics,
                errors=error_writer,
            )
            statistics.exported = exporter.write(
                records,
                config.output.path,
                passing_grade=config.processing.passing_grade,
            )
        write_summary(config.output.summary_path, statistics.to_dict())
    logger.info(
        "Total=%s valid=%s invalid=%s passed=%s failed=%s exported=%s",
        statistics.total,
        statistics.valid,
        statistics.invalid,
        statistics.passed,
        statistics.failed,
        statistics.exported,
    )
    return statistics


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reliable student grading importer")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    args = parser.parse_args(argv)
    try:
        run(args.config)
    except ApplicationError as error:
        logging.getLogger(__name__).error("Application error: %s", error)
        return 1
    return 0


def cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()

