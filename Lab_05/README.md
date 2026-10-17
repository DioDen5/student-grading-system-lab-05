# Лабораторна робота №5 — варіант 7

**Тема:** «Обробка помилок, файли та серіалізація»  
**Предметна область:** система оцінювання студентів  
**Студент:** Заставний Денис, ФеП-32

## Реалізовані вимоги

- схема варіанта `student_id`, `name`, `discipline`, `grade`;
- `pathlib.Path` для всіх шляхів і явне `encoding="utf-8"`;
- потоковий CSV importer на `csv.DictReader` без `list(reader)`;
- підтримка CSV, JSON, YAML та JSON Lines через єдиний `Importer` Protocol;
- автоматичний вибір importer за розширенням;
- YAML configuration з версією схеми, переліком дисциплін і порогом успішності;
- fail-fast validation configuration та environment overrides `SG_*`;
- повна validation записів, включно з finite grade у межах 0–100;
- custom exception hierarchy та `raise ... from ...`;
- strict і tolerant processing без зміни program logic;
- статистика total/valid/invalid/passed/failed/exported;
- configurable rotating application log і окремий CSV invalid-record report;
- JSON serialization та streaming JSON output;
- transaction-like власний context manager `AtomicTextWriter`;
- atomic replace, cleanup `.tmp` і backup наявного output;
- власний generator-based context manager `logged_operation`;
- summary report у JSON;
- controlled exit code при critical errors;
- відтворюваний eager/streaming experiment для 10 000, 100 000 і 500 000 записів;
- pytest suite, branch coverage понад 90% і strict static type checking.

## Структура

```text
Lab_05/
├── config.yaml
├── data/grades.csv
├── docs/experiments/memory_results.json
├── logs/
├── output/
├── report/report.docx
├── src/student_grading_io/
│   ├── config.py
│   ├── error_report.py
│   ├── exceptions.py
│   ├── exporters.py
│   ├── logging_config.py
│   ├── main.py
│   ├── models.py
│   ├── operations.py
│   ├── readers.py
│   ├── services.py
│   └── validators.py
├── tests/
├── tools/run_experiments.py
├── main.py
└── pyproject.toml
```

## Встановлення і запуск

```bash
cd Lab_05
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m student_grading_io --config config.yaml
```

За замовчуванням увімкнено tolerant mode (`skip_invalid: true`). Для strict mode потрібно змінити це значення на `false` у `config.yaml` — Python code не змінюється.

## Перевірки

```bash
python -m pytest --cov=student_grading_io --cov-report=term-missing
python -m mypy src tests tools/run_experiments.py main.py
python tools/run_experiments.py
```

## Reliability guarantees

Вхідні дані перевіряються на system boundary до створення domain object. У tolerant mode невалідний запис фіксується у двох журналах і пропускається; у strict mode той самий `RecordValidationError` негайно припиняє pipeline. Експорт спочатку виконується у `.tmp`, тому exception не пошкоджує попередній valid output. Оригінальна причина parse/config/I/O failure зберігається через exception chaining.
