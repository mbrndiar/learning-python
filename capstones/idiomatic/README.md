# Idiomatic Python capstone: ingestion and reporting

Build the offline-first pipeline defined by [`SPEC.md`](SPEC.md). The project
combines immutable values, streaming iterators, structural protocols, SQLite,
an injected paginated HTTP boundary, bounded threads, and deterministic reports.
Runtime code uses only the Python standard library.

## Choose a source root

Both roots expose the same `ingest_report` package and commands:

- [`starter/ingest_report/`](starter/ingest_report/) is compileable and strictly
  typed. Search it for `TODO(m1)` through `TODO(m5)` and complete one milestone
  at a time.
- [`solution/ingest_report/`](solution/ingest_report/) is the complete reference
  implementation. Read it only after attempting the matching starter milestone.

Tests select a root through `CAPSTONE_IMPLEMENTATION=starter|solution`; no task
code is copied into the harness.

## Guided milestones

1. **Domain:** implement field validation, UTC millisecond normalization,
   immutable events/rejects, and stable single-pass deduplication.
2. **Sources and application boundary:** stream exact CSV and JSONL formats,
   close iterators on every exit, inject the repository/clock, and classify CLI
   errors.
3. **SQLite:** initialize only empty databases, validate schema version 1,
   preserve first event identities, and commit each import atomically.
4. **Reporting:** combine inclusive filters with `AND`, aggregate totals and
   groups, then render stable JSON and the documented text headings.
5. **HTTP and integration:** fetch page 1 first, schedule at most `workers`
   calls, collect by page number, join on cancellation, and implement
   strict/partial semantics.

Run a milestone against the selected tree:

```bash
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_m1_*.py' -v
```

Advance the pattern through `test_m5_*.py`. The untouched starter intentionally
raises `IncompleteImplementationError`; CI only compiles and type-checks it and
runs its harness smoke test.

## Run the reference CLI

```bash
PYTHONPATH=capstones/idiomatic/solution \
  python -m ingest_report --db events.db ingest \
  --import-id csv-001 --format csv \
  --input capstones/idiomatic/tests/fixtures/events-valid.csv

PYTHONPATH=capstones/idiomatic/solution \
  python -m ingest_report --db events.db report --output text
```

HTTP imports accept only unauthenticated loopback `http://` URLs. Page transport
is injectable through `PageFetcher`, and worker creation is injectable through
`ExecutorFactory`, so tests need neither DNS nor public services.

## Public boundaries

- `ingest_report.cli.main(argv) -> int`;
- immutable `Event`, `RejectedRecord`, `ImportResult`, and `Report`;
- `RecordSource`, `EventRepository`, `Clock`, and `PageFetcher` protocols;
- `CSVSource`, `JSONLinesSource`, `URLPageFetcher`, and
  `SQLiteEventRepository` reference adapters.

Expected failures use stable codes and exit categories. Add `--json-errors` for
the semantic error envelope documented in the specification.

## Quality commands

```bash
python -m compileall -q capstones/idiomatic/starter
mypy --strict capstones/idiomatic/starter/ingest_report
mypy
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py' -v
CAPSTONE_IMPLEMENTATION=solution coverage run -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py'
coverage report
ruff format --check .
ruff check .
```

Fixtures live under [`tests/fixtures/`](tests/fixtures/), including equivalent
CSV/JSONL data, mixed rejects, golden reports, and three HTTP page payloads.
