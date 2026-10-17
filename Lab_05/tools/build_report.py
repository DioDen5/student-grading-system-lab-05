"""Generate the complete DOCX report for laboratory work 5, variant 7."""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report" / "report.docx"
MEMORY_RESULTS = json.loads(
    (ROOT / "docs" / "experiments" / "memory_results.json").read_text(encoding="utf-8")
)

QA = [
    ("Що таке exception?", "Об’єкт, який сигналізує про ненормальну ситуацію та передає керування механізму обробки помилок."),
    ("Для чого використовується try?", "Для позначення ділянки коду, під час якої очікуються контрольовані exceptions."),
    ("Для чого except?", "Для обробки конкретного типу exception, що виник у відповідному try."),
    ("Коли виконується else після try?", "Коли блок try завершився без exception."),
    ("Коли виконується finally?", "Завжди після try/except, незалежно від успіху, exception або return."),
    ("Для чого використовується raise?", "Для явного створення або передавання exception вище по call stack."),
    ("Що означає raise без аргументів?", "Повторне підняття поточного exception зі збереженням traceback."),
    ("Чому не рекомендується except: pass?", "Він приховує помилки, втрачає diagnostics і може залишити application у некоректному стані."),
    ("Чому потрібно перехоплювати конкретні exception types?", "Щоб обробляти лише очікувані failures і не маскувати programming errors."),
    ("Що таке exception hierarchy?", "Система base і specialized exception classes, яка дає змогу обробляти помилки за рівнями abstraction."),
    ("Для чого створювати custom exceptions?", "Щоб надати помилці domain meaning, context і стабільний контракт для callers."),
    ("Що таке exception chaining?", "Зв’язок між новим domain exception і початковою low-level причиною."),
    ("Що означає raise ... from ...?", "Явно встановлює original exception як __cause__ нового exception."),
    ("Яку перевагу дає chaining для debugging?", "Traceback показує і зрозумілу domain error, і технічну першопричину."),
    ("Що означає EAFP?", "Спочатку виконати операцію, а очікувану невдачу обробити через exception."),
    ("Що означає LBYL?", "Перевірити передумови до виконання операції."),
    ("Що таке fail-fast?", "Негайне завершення підготовки, коли критичні configuration або invariants некоректні."),
    ("Де доцільно застосовувати fail-fast?", "Під час startup validation конфігурації, залежностей і обов’язкових input resources."),
    ("Що таке context manager?", "Об’єкт або generator, що керує входом і гарантованим завершенням resource lifecycle."),
    ("Для чого використовується with?", "Для автоматичного виклику context manager та гарантованого cleanup навіть при exception."),
    ("Які methods утворюють context manager protocol?", "__enter__() і __exit__()."),
    ("Що робить __enter__()?", "Готує ресурс і повертає значення, доступне після as."),
    ("Що робить __exit__()?", "Завершує lifecycle, звільняє ресурс і за потреби визначає, чи suppress exception."),
    ("Чи закриває with файл при exception?", "Так, __exit__() викликається і файл закривається."),
    ("Для чого contextlib.contextmanager?", "Для побудови простого context manager із generator без окремого class."),
    ("Яку роль має yield у generator-based context manager?", "Передає керування тілу with; код після yield виконує cleanup або final logging."),
    ("Що таке pathlib.Path?", "Об’єктний, portable interface для файлових шляхів та операцій із ними."),
    ("Чому pathlib кращий за ручну конкатенацію шляхів?", "Коректно враховує OS separators, дає читабельний API і типізовані операції."),
    ("Для чого задається encoding=\"utf-8\"?", "Щоб результат не залежав від локального default encoding операційної системи."),
    ("Що таке CSV?", "Текстовий табличний формат, у якому записи подано рядками, а поля розділено delimiter."),
    ("Для чого csv.reader?", "Для читання CSV як послідовності списків значень."),
    ("Для чого csv.DictReader?", "Для читання рядків як mappings, де keys походять із header."),
    ("Чим DictReader зручний для structured data?", "Дозволяє звертатися до fields за змістовними назвами, а не індексами."),
    ("Для чого csv.DictWriter?", "Для запису mappings у CSV у визначеному порядку fieldnames."),
    ("Що таке JSON?", "Текстовий формат обміну структурованими даними на основі objects, arrays і scalar values."),
    ("Що таке serialization?", "Перетворення program object або data structure у формат для зберігання чи передавання."),
    ("Що таке deserialization?", "Відновлення data structure з external serialized representation."),
    ("Чим json.dump() відрізняється від json.dumps()?", "dump записує у file-like object, dumps повертає string."),
    ("Чим json.load() відрізняється від json.loads()?", "load читає file-like object, loads обробляє string/bytes."),
    ("Що таке JSONDecodeError?", "Specialized ValueError із позицією помилки синтаксису JSON."),
    ("Для чого використовується YAML?", "Для читабельної людиною configuration та вкладених структур."),
    ("Чому рекомендується yaml.safe_load()?", "Він не створює довільні Python objects із недовіреного YAML."),
    ("Які типові сценарії використання JSON?", "API, machine-to-machine exchange, structured exports, caches і web configuration."),
    ("Які типові сценарії використання YAML?", "Human-edited configuration, CI/CD manifests і вкладені settings."),
    ("Що таке configuration file?", "Зовнішній файл параметрів, який змінює behavior без редагування source code."),
    ("Чому configuration краще не hard-code у Python?", "Її можна змінювати для різних environments без rebuild і code changes."),
    ("Що потрібно перевіряти у configuration?", "Structure, types, ranges, allowed values, schema version і доступність critical paths."),
    ("Що таке logging?", "Систематичний запис подій application із level, timestamp, source і context."),
    ("Чим logging відрізняється від print()?", "Logging має levels, handlers, formatting, rotation і може спрямовувати події у кілька destinations."),
    ("Які існують logging levels?", "DEBUG, INFO, WARNING, ERROR і CRITICAL."),
    ("Для чого logger.info()?", "Для нормальних значущих подій життєвого циклу application."),
    ("Для чого logger.warning()?", "Для проблеми, після якої application може контрольовано продовжити роботу."),
    ("Для чого logger.error()?", "Для failure операції, що потребує уваги, але не обов’язково завершує весь process."),
    ("Для чого logger.exception()?", "Для ERROR message разом із traceback поточного exception усередині except."),
    ("Що містить traceback?", "Послідовність stack frames, calls, source locations і exception message."),
    ("Чому secrets не можна записувати в logs?", "Logs часто довго зберігаються й широко доступні; витік secret дає несанкціонований доступ."),
    ("Що таке streaming I/O?", "Послідовна обробка невеликих частин data без завантаження всього dataset у RAM."),
    ("Яка перевага streaming для великих files?", "Peak memory майже не залежить від кількості records."),
    ("Що таке eager file loading?", "Повне materialization data у memory до processing."),
    ("Чому list(reader) може бути небажаним?", "Memory usage зростає пропорційно dataset і може перевищити доступну RAM."),
    ("Що таке strict validation mode?", "Перший invalid record піднімає exception і припиняє pipeline."),
    ("Що таке tolerant mode?", "Invalid record логується, враховується у statistics, пропускається, а processing продовжується."),
    ("Коли доцільно використовувати strict mode?", "Коли dataset має бути повністю коректним і частковий результат недопустимий."),
    ("Коли tolerant mode?", "Для великих batch imports, де корисно прийняти valid records та окремо виправити errors."),
    ("Що таке atomic write?", "Запис у temporary file з одним replace target лише після повного успіху."),
    ("Для чого використовується temporary file?", "Щоб незавершений або пошкоджений content не став final output."),
    ("Що може статися при звичайному output write та аварійному завершенні?", "Final file може залишитися частково перезаписаним або порожнім."),
    ("Навіщо видаляти temporary file після error?", "Щоб не залишати сміття й не сплутати incomplete artifact із valid output."),
    ("Що таке JSON Lines?", "Формат, у якому кожний рядок є незалежним JSON object."),
    ("Чому JSON Lines зручний для streaming?", "Records можна читати й декодувати по одному без materialization усього array."),
]


def add_field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    text = OxmlElement("w:instrText")
    text.set(qn("xml:space"), "preserve")
    text.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    display = OxmlElement("w:t")
    display.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend((begin, text, separate, display, end))


def heading(doc: Document, text: str, level: int = 1) -> None:
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.add_run(text)


def code(doc: Document, value: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.6)
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.line_spacing = 1.0
    paragraph.paragraph_format.space_before = Pt(3)
    paragraph.paragraph_format.space_after = Pt(5)
    run = paragraph.add_run(value.strip())
    run.font.name = "DejaVu Sans Mono"
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "DejaVu Sans Mono")
    run.font.size = Pt(8.3)


def bullet(doc: Document, value: str) -> None:
    paragraph = doc.add_paragraph(style="List Bullet")
    paragraph.add_run(value)


def shade(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    props.append(element)


def set_cell_margins(cell, top: int = 90, start: int = 100, bottom: int = 90, end: int = 100) -> None:
    props = cell._tc.get_or_add_tcPr()
    margins = props.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        props.append(margins)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
    item = doc.add_table(rows=1, cols=len(headers))
    item.alignment = WD_TABLE_ALIGNMENT.CENTER
    item.style = "Table Grid"
    header_props = item.rows[0]._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    header_props.append(repeat)
    for index, text in enumerate(headers):
        cell = item.rows[0].cells[index]
        cell.text = text
        shade(cell, "D9EAF7")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(cell)
        for run in cell.paragraphs[0].runs:
            run.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row_index, values in enumerate(rows):
        cells = item.add_row().cells
        row_props = item.rows[-1]._tr.get_or_add_trPr()
        no_split = OxmlElement("w:cantSplit")
        row_props.append(no_split)
        for index, text in enumerate(values):
            cells[index].text = text
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cells[index])
            cells[index].paragraphs[0].paragraph_format.first_line_indent = Cm(0)
            cells[index].paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.CENTER if index == 0 else WD_ALIGN_PARAGRAPH.LEFT
            )
            if row_index % 2:
                shade(cells[index], "F5F8FA")
    if widths:
        for row in item.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def figure(doc: Document, path: Path, caption: str, width: float = 6.35) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.keep_with_next = True
    image = paragraph.add_run().add_picture(str(path), width=Inches(width))
    image._inline.docPr.set("descr", caption)
    caption_paragraph = doc.add_paragraph(caption)
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_paragraph.paragraph_format.first_line_indent = Cm(0)
    caption_paragraph.paragraph_format.space_after = Pt(6)


def build() -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(1.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.space_after = Pt(1)
    for style_name in ("Title", "Heading 1", "Heading 2", "Heading 3"):
        style = doc.styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True
        style.paragraph_format.first_line_indent = Cm(0)
        style.paragraph_format.keep_with_next = True
    doc.styles["Heading 1"].font.size = Pt(14)
    doc.styles["Heading 1"].paragraph_format.space_before = Pt(9)
    doc.styles["Heading 1"].paragraph_format.space_after = Pt(3)
    doc.styles["Heading 2"].font.size = Pt(13)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(footer, "PAGE")

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.add_run("ЛЬВІВСЬКИЙ НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ\nІМЕНІ ІВАНА ФРАНКА").bold = True
    doc.add_paragraph("\n\n\n")
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    run = paragraph.add_run("ЗВІТ\nДО ЛАБОРАТОРНОЇ РОБОТИ №5")
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0, 0, 0)
    paragraph = doc.add_paragraph("«Обробка помилок, файли та серіалізація»")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph = doc.add_paragraph(
        "з курсу «Професійний Python»\n"
        "Варіант №7 — «Імпорт та експорт системи оцінювання студентів»"
    )
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    doc.add_paragraph("\n\n")
    for value in (
        "Студент: Заставний Денис",
        "Група: ФеП-32",
        "Предмет: professional_python",
        "Лабораторна робота: Lab_05",
        "Варіант: 7",
        "Перевірив: Свелеба Сергій Андрійович",
        "Дата: 18.10.2026",
    ):
        paragraph = doc.add_paragraph(value)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.paragraph_format.first_line_indent = Cm(0)
    doc.add_paragraph("\n\n")
    paragraph = doc.add_paragraph("Львів — 2026")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    doc.add_page_break()

    heading(doc, "1. Тема, мета та результат роботи")
    doc.add_paragraph(
        "Тема: обробка помилок, файли та серіалізація. Мета роботи — створити надійний модуль імпорту, validation, обробки та export зовнішніх даних, який передбачувано працює з некоректними записами й file I/O failures. Реалізований pipeline використовує custom exceptions, exception chaining, context managers, pathlib, logging, CSV/JSON/YAML, streaming I/O, strict/tolerant policy і atomic output."
    )

    heading(doc, "2. Варіант №7 і постановка задачі")
    doc.add_paragraph(
        "Індивідуальне завдання — імпорт та експорт системи оцінювання студентів. Поля: student_id, name, discipline, grade. Student ID має бути додатним integer, ПІБ — непорожнім і складатися щонайменше з двох слів, discipline — належати до configured list, grade — бути finite number у межах 0–100. YAML задає allowed disciplines, passing threshold і validation mode; valid records експортуються у JSON, invalid records потрапляють у application log та окремий error CSV."
    )

    heading(doc, "3. Input data schema та приклад CSV")
    table(
        doc,
        ["Поле", "Тип після parsing", "Правило"],
        [
            ["student_id", "int", "Додатне значення"],
            ["name", "str", "Щонайменше два слова"],
            ["discipline", "str", "Значення з YAML allowed_disciplines"],
            ["grade", "float", "Finite, 0 ≤ grade ≤ 100"],
        ],
        [1.25, 1.45, 3.65],
    )
    code(
        doc,
        """
student_id,name,discipline,grade
1,Anna Koval,Professional Python,91.5
2,Oleh Melnyk,Databases,84
3,Iryna Bondar,Algorithms,57.5
abc,Maria Boyko,Databases,85
7,Andrii Lytvyn,Networks,88
""",
    )

    heading(doc, "4. Структура й архітектура проєкту")
    code(
        doc,
        """
Lab_05/
├── config.yaml                ├── report/report.docx
├── data/grades.csv            ├── tests/
├── docs/experiments/          ├── tools/run_experiments.py
├── logs/                      ├── main.py
├── output/                    └── pyproject.toml
└── src/student_grading_io/
    ├── config.py  exceptions.py  models.py  readers.py
    ├── validators.py  services.py  exporters.py
    ├── error_report.py  logging_config.py  operations.py
    └── main.py
""",
    )
    code(
        doc,
        """
config.yaml → load_config() → validate_config()
       ↓
input file → Importer → streaming rows → parse/validate
                                      ↙             ↘
                                  valid          invalid
                                    ↓          log + error CSV
                              statistics       skip / raise
                                    ↓
                              JSON serialization
                                    ↓
                           temporary → atomic replace
""",
    )

    heading(doc, "5. Exception hierarchy і custom exceptions")
    code(
        doc,
        """
ApplicationError
├── ConfigurationError
└── DataError
    ├── DataImportError
    ├── RecordValidationError(line_number, field, raw_record)
    └── DataExportError
""",
    )
    doc.add_paragraph(
        "Hierarchy відділяє configuration, import, validation та export failures. Main перехоплює ApplicationError і повертає controlled exit code 1; неочікувані programming errors не маскуються загальним except. RecordValidationError зберігає line number, field і raw record для diagnostics."
    )

    heading(doc, "6. Exception chaining")
    code(
        doc,
        """
try:
    student_id = int(raw["student_id"])
except (KeyError, TypeError, ValueError) as cause:
    raise RecordValidationError(
        "student_id must be an integer",
        line_number=line_number,
        field="student_id",
        raw_record=dict(raw),
    ) from cause
""",
    )
    doc.add_paragraph(
        "У strict experiment значення abc спричинило ValueError, після якого traceback показав explicit cause RecordValidationError. Так зберігається технічна першопричина разом із domain context."
    )

    heading(doc, "7. YAML configuration та loader")
    code(
        doc,
        """
schema_version: 1
input: {path: data/grades.csv, format: auto}
output:
  path: output/valid_grades.json
  backup_existing: true
  summary_path: output/summary.json
processing:
  allowed_disciplines: [Professional Python, Databases, Algorithms]
  passing_grade: 60
  skip_invalid: true
logging:
  level: INFO
  path: logs/application.log
  error_records_path: logs/invalid_records.csv
  max_bytes: 1000000
  backup_count: 3
""",
    )
    code(
        doc,
        """
try:
    with path.open("r", encoding="utf-8") as file:
        raw_object = yaml.safe_load(file)
except FileNotFoundError as error:
    raise ConfigurationError(f"Configuration file not found: {path}") from error
except yaml.YAMLError as error:
    raise ConfigurationError("Invalid YAML configuration") from error
""",
    )

    heading(doc, "8. Validation configuration і fail-fast")
    doc.add_paragraph(
        "До запуску pipeline перевіряються schema_version, input format, наявність input file, непорожній allowed discipline list, passing_grade 0..100, logging level і rotation parameters. Paths відносно config.yaml перетворюються на absolute Path. Підтримуються безпечні overrides SG_INPUT_PATH, SG_OUTPUT_PATH, SG_PASSING_GRADE і SG_SKIP_INVALID."
    )
    code(
        doc,
        """
if config.schema_version != 1:
    raise ConfigurationError("Unsupported configuration schema_version")
if not config.input.path.is_file():
    raise ConfigurationError(f"Input file not found: {config.input.path}")
if not 0 <= config.processing.passing_grade <= 100:
    raise ConfigurationError("passing_grade must be between 0 and 100")
""",
    )

    heading(doc, "9. Logging configuration та error log")
    doc.add_paragraph(
        "Application використовує RotatingFileHandler із configured max_bytes/backup_count та console handler. Invalid records мають WARNING level без конфіденційних даних; operation failure реєструється через logger.exception() із traceback. Окремий invalid_records.csv містить line_number, field, message і raw record."
    )
    code(
        doc,
        """
file_handler = RotatingFileHandler(
    config.path, maxBytes=config.max_bytes,
    backupCount=config.backup_count, encoding="utf-8",
)
logging.basicConfig(
    level=getattr(logging, config.level),
    handlers=[file_handler, logging.StreamHandler()], force=True,
)
""",
    )
    figure(doc, ROOT / "report" / "assets" / "log_fragment.png", "Рисунок 1 — Фрагмент application log")

    heading(doc, "10. Streaming reader та multiple formats")
    code(
        doc,
        """
class Importer(Protocol):
    def read(self, path: Path) -> Iterator[tuple[int, RawRecord]]: ...

class CsvImporter:
    def read(self, path: Path) -> Iterator[tuple[int, RawRecord]]:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for line_number, row in enumerate(reader, start=2):
                yield line_number, dict(row)
""",
    )
    doc.add_paragraph(
        "CSV і JSON Lines читаються streaming. JSON/YAML arrays підтримуються через StructuredImporter для moderate documents. importer_for() автоматично вибирає CSV, JSON, YAML/YML або JSONL за configured format чи file extension."
    )

    heading(doc, "11. Validation records")
    code(
        doc,
        """
discipline = str(raw.get("discipline", "")).strip()
if discipline not in allowed_disciplines:
    raise RecordValidationError("discipline is not allowed", field="discipline", ...)

grade = float(raw["grade"])
if not isfinite(grade) or not 0 <= grade <= 100:
    raise RecordValidationError("grade must be between 0 and 100", field="grade", ...)
""",
    )

    heading(doc, "12. Strict і tolerant processing")
    code(
        doc,
        """
except RecordValidationError as error:
    statistics.invalid += 1
    logger.warning("Invalid record at line %s, field=%s: %s", ...)
    errors.write(error)
    if skip_invalid:
        continue
    raise
""",
    )
    doc.add_paragraph(
        "Політика задається лише configuration. Tolerant mode зберігає valid records і продовжує processing; strict mode повторно піднімає той самий exception. Це EAFP: parsing виконується напряму, а очікувані conversion failures обробляються конкретно."
    )

    heading(doc, "13. Import statistics")
    table(
        doc,
        ["Лічильник", "Зміст", "Tolerant run"],
        [
            ["total", "Рядків отримано від importer", "9"],
            ["valid", "Створено GradeRecord", "5"],
            ["invalid", "Відхилено validation", "4"],
            ["passed", "grade ≥ 60", "4"],
            ["failed", "valid grade < 60", "1"],
            ["exported", "Атомарно записано у JSON", "5"],
        ],
        [1.2, 3.45, 1.6],
    )

    heading(doc, "14. JSON serialization і atomic export")
    code(
        doc,
        """
with AtomicTextWriter(path, backup_existing=True) as file:
    file.write("[\\n")
    for record in records:
        json.dump(record.to_dict(passing_grade=passing_grade), file,
                  ensure_ascii=False, indent=2)
    file.write("\\n]\\n")
""",
    )
    doc.add_paragraph(
        "AtomicTextWriter пише у target.json.tmp. Лише після успішного завершення with temporary file замінює target одним Path.replace(); попередній output за configuration переноситься у .bak. Якщо serialization або validation завершується exception, temporary file видаляється, а попередній valid output не пошкоджується."
    )

    heading(doc, "15. Власні context managers")
    code(
        doc,
        """
class AtomicTextWriter:
    def __enter__(self) -> TextIO:
        self._file = self.temporary.open("w", encoding="utf-8")
        return self._file

    def __exit__(self, exc_type, exc_value, traceback) -> Literal[False]:
        self._file.close()
        if exc_type is not None:
            self.temporary.unlink(missing_ok=True)
            return False
        self.temporary.replace(self.path)
        return False
""",
    )
    doc.add_paragraph(
        "Додатково ErrorCsvWriter гарантує закриття error report, а generator-based logged_operation() вимірює час, реєструє start/success і logger.exception() при failure."
    )

    heading(doc, "16. Результат виконання програми")
    figure(doc, ROOT / "report" / "assets" / "application_output.png", "Рисунок 2 — Виконання tolerant pipeline")

    heading(doc, "17. Експеримент strict проти tolerant")
    table(
        doc,
        ["Параметр", "Strict", "Tolerant"],
        [
            ["Оброблено записів", "5 до першої помилки", "9"],
            ["Valid", "4", "5"],
            ["Invalid", "1", "4"],
            ["Exported", "0", "5"],
            ["Завершення", "Controlled exit code 1", "Успіх, exit code 0"],
            ["Output", "Попередній файл збережено; .tmp очищено", "Атомарно замінено"],
        ],
        [1.55, 2.35, 2.35],
    )
    doc.add_paragraph(
        "Strict mode доцільний для all-or-nothing import і audit-sensitive data. Tolerant mode корисний для batch processing, коли частковий valid result має цінність, а помилки виправляються за окремим error report."
    )

    heading(doc, "18. Експеримент streaming проти eager")
    memory_rows = [
        [
            f"{item['records']:,}".replace(",", " "),
            f"{item['eager_time_seconds']:.6f} s",
            f"{item['streaming_time_seconds']:.6f} s",
            f"{item['eager_peak_mib']:.3f} MiB",
            f"{item['streaming_peak_mib']:.3f} MiB",
        ]
        for item in MEMORY_RESULTS
    ]
    table(
        doc,
        ["Records", "Eager time", "Streaming time", "Eager peak RAM", "Streaming peak RAM"],
        memory_rows,
        [0.9, 1.2, 1.35, 1.35, 1.55],
    )
    doc.add_paragraph(
        "Вимірювання виконано tracemalloc із повним проходом обох readers. При 500 000 records eager materialization досягла 187,247 MiB, а streaming залишився на 0,046 MiB. У цьому запуску streaming був також трохи швидшим, однак головна гарантована перевага — майже сталий peak memory."
    )

    heading(doc, "19. Експерименти configuration errors та atomic output")
    table(
        doc,
        ["Сценарій", "Очікувана контрольована поведінка"],
        [
            ["Відсутній config.yaml", "ConfigurationError із path; exit code 1"],
            ["Некоректний YAML", "YAMLError → ConfigurationError через chaining"],
            ["Немає input section/key", "ConfigurationError про structure/value"],
            ["passing_grade = 150", "Fail-fast до відкриття output"],
            ["Input file відсутній", "Fail-fast Input file not found"],
            ["Output directory відсутній", "Створюється parents=True"],
            ["Exception під час export", "Попередній output збережено, .tmp видалено"],
        ],
        [2.15, 4.2],
    )

    heading(doc, "20. Додаткові можливості підвищеної складності")
    for item in (
        "CSV, JSON, YAML і JSON Lines input через єдиний Importer Protocol;",
        "Exporter Protocol і автоматичний вибір input format за extension;",
        "окремий CSV error report і configurable rotating logging;",
        "nested configuration, schema version та SG_* environment overrides;",
        "atomic export, cleanup temporary file і backup existing output;",
        "streaming JSON Lines та streaming JSON array output;",
        "progress/final statistics і окремий summary.json;",
        "transaction-like AtomicTextWriter та logged_operation context managers.",
    ):
        bullet(doc, item)

    heading(doc, "21. Автоматизовані перевірки")
    doc.add_paragraph(
        "30 pytest tests перевіряють configuration failures, environment overrides, усі import formats, malformed data, exception chaining, field validation, strict/tolerant policy, statistics, error CSV, JSON serialization, backup, rollback, controlled CLI exit, logging і context managers. Branch coverage становить 93,58%, що перевищує configured threshold 90%. Strict mypy не знаходить помилок у 20 source files."
    )
    code(
        doc,
        """
$ python -m pytest --cov=student_grading_io --cov-report=term-missing
30 passed
TOTAL 434 statements, 93.58% coverage

$ python -m mypy src tests tools/run_experiments.py main.py
Success: no issues found in 20 source files
""",
    )

    doc.add_page_break()
    heading(doc, "22. Відповіді на контрольні запитання")
    for number, (question, answer) in enumerate(QA, start=1):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.first_line_indent = Cm(0)
        paragraph.paragraph_format.space_after = Pt(2)
        run = paragraph.add_run(f"{number}. {question}")
        run.bold = True
        run.font.size = Pt(9)
        answer_run = paragraph.add_run(f" — {answer}")
        answer_run.font.size = Pt(9)

    doc.add_page_break()
    heading(doc, "23. Висновок")
    doc.add_paragraph(
        "У Lab_05 реалізовано надійний import/export pipeline варіанта №7 для системи оцінювання студентів. Зовнішні дані перетворюються на GradeRecord лише після validation; custom exception hierarchy і chaining зберігають зміст і першопричину failures. Strict/tolerant policy змінюється через YAML без редагування Python code. Context managers гарантують закриття resources, logging і error CSV забезпечують diagnostics, а atomic writer не залишає пошкоджений output. Реальний experiment показав майже сталу streaming memory навіть для 500 000 records. 30 tests, coverage 93,58% і strict mypy підтверджують коректність реалізації."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.core_properties.title = "Звіт до лабораторної роботи №5 — варіант 7"
    doc.core_properties.subject = "Обробка помилок, файли та серіалізація"
    doc.core_properties.author = "Заставний Денис"
    doc.core_properties.keywords = "Lab_05, variant 7, professional_python"
    doc.save(OUTPUT)


if __name__ == "__main__":
    build()
