"""Create terminal-style screenshots from the real Lab 05 execution evidence."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "report" / "assets"
FONT = Path("/System/Library/Fonts/Menlo.ttc")


def terminal_image(title: str, lines: list[tuple[str, str]], output: Path) -> None:
    width = 1500
    line_height = 35
    height = 92 + line_height * len(lines) + 36
    image = Image.new("RGB", (width, height), "#0d1117")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 58), fill="#1f2630")
    draw.ellipse((24, 20, 42, 38), fill="#ff5f57")
    draw.ellipse((52, 20, 70, 38), fill="#febc2e")
    draw.ellipse((80, 20, 98, 38), fill="#28c840")
    title_font = ImageFont.truetype(str(FONT), 23)
    body_font = ImageFont.truetype(str(FONT), 22)
    draw.text((122, 16), title, font=title_font, fill="#c9d1d9")
    y = 78
    colors = {
        "command": "#56d4dd",
        "info": "#7ee787",
        "warning": "#f2cc60",
        "plain": "#c9d1d9",
        "result": "#a5d6ff",
    }
    for kind, text in lines:
        draw.text((28, y), text, font=body_font, fill=colors[kind])
        y += line_height
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> None:
    terminal_image(
        "student-grading-io — tolerant run",
        [
            ("command", "$ python -m student_grading_io --config config.yaml"),
            ("info", "INFO | Student grading import/export started"),
            ("warning", "WARNING | line 6, student_id: must be an integer"),
            ("warning", "WARNING | line 7, name: must contain at least two words"),
            ("warning", "WARNING | line 8, discipline: value is not allowed"),
            ("warning", "WARNING | line 9, grade: must be between 0 and 100"),
            ("info", "INFO | Student grading import/export finished in 0.002929 s"),
            ("result", "Total=9 valid=5 invalid=4 passed=4 failed=1 exported=5"),
            ("plain", "Output: output/valid_grades.json"),
            ("plain", "Errors: logs/invalid_records.csv"),
        ],
        ASSETS / "application_output.png",
    )
    terminal_image(
        "application.log — controlled diagnostics",
        [
            ("info", "2026-10-18 01:49:10 | INFO | import/export started"),
            ("warning", "2026-10-18 01:49:10 | WARNING | line 6 | student_id"),
            ("warning", "2026-10-18 01:49:10 | WARNING | line 7 | name"),
            ("warning", "2026-10-18 01:49:10 | WARNING | line 8 | discipline"),
            ("warning", "2026-10-18 01:49:10 | WARNING | line 9 | grade"),
            ("info", "2026-10-18 01:49:10 | INFO | finished in 0.002929 s"),
            ("result", "Total=9 valid=5 invalid=4 passed=4 failed=1 exported=5"),
        ],
        ASSETS / "log_fragment.png",
    )


if __name__ == "__main__":
    main()

