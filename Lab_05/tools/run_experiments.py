"""Reproducible strict/tolerant and eager/streaming experiments."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import tracemalloc
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from time import perf_counter
from typing import TypeVar

T = TypeVar("T")


def generate(path: Path, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("student_id", "name", "discipline", "grade"))
        for index in range(1, count + 1):
            writer.writerow((index, f"Student {index}", "Professional Python", index % 101))


def eager(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as file:
        return len(list(csv.DictReader(file)))


def streaming(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as file:
        return sum(1 for _ in csv.DictReader(file))


def measure(operation: Callable[[Path], int], path: Path) -> tuple[float, float, int]:
    tracemalloc.start()
    started = perf_counter()
    count = operation(path)
    elapsed = perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return elapsed, peak / (1024 * 1024), count


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[10_000, 100_000, 500_000])
    parser.add_argument("--output", type=Path, default=Path("docs/experiments/memory_results.json"))
    args = parser.parse_args(argv)
    temp = args.output.parent / "generated.csv"
    results: list[dict[str, float | int]] = []
    try:
        for size in args.sizes:
            generate(temp, size)
            eager_time, eager_peak, eager_count = measure(eager, temp)
            stream_time, stream_peak, stream_count = measure(streaming, temp)
            assert eager_count == stream_count == size
            results.append(
                {
                    "records": size,
                    "eager_time_seconds": round(eager_time, 6),
                    "streaming_time_seconds": round(stream_time, 6),
                    "eager_peak_mib": round(eager_peak, 3),
                    "streaming_peak_mib": round(stream_peak, 3),
                }
            )
    finally:
        temp.unlink(missing_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

