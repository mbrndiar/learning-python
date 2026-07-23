# Idiomatic capstone specification: data ingestion and reporting pipeline

## Status and interpretation

This is the learner contract for the required Python idiomatic capstone. It is
equal in weight to the comparative SQLite key/value capstone. The observable
commands, data rules, errors, milestones, and acceptance criteria below are
normative. Package layering and internal class/function decomposition are not;
learners may choose any clear design that preserves the public boundaries.

The removed connected Task projects are historical material. They are distinct
from the current required
[Task REST API and clients project](../../projects/tasks/README.md).

## Bounded problem

Build an offline-first CLI that imports operational event records from:

1. one fixed CSV dialect;
2. UTF-8 JSON Lines; and
3. an injected or loopback-only paginated HTTP source.

The program validates and normalizes records, streams accepted records and
rejects into a domain-specific SQLite database, suppresses duplicate events,
and produces deterministic aggregate reports.

An event is an observation, not a mutable task or arbitrary key/value entry.
The project has no update/delete event commands, revisions, compare-and-set, or
generic storage API.

## Learning goals and course mapping

| Course material | Capstone outcome |
| --- | --- |
| [Modules 1–4](../../lessons/README.md) | Expressions, control flow, functions, mappings, sets, comprehensions, counting, and stable sorting implement normalization and reports. |
| [Module 6: modules and packages](../../lessons/06_modules_and_packages/README.md) | Organize modules and packages, guard entry points, and declare a small public API. |
| [Module 7: exceptions, files, and paths](../../lessons/07_exceptions_files_and_paths/README.md) | Own UTF-8 text and binary files and context-managed resources; handle narrow, chained exceptions deliberately. |
| [Module 8: structured data and time](../../lessons/08_structured_data_and_time/README.md) | Validate JSON boundaries and normalize timestamps to UTC. |
| [Module 9: objects and data models](../../lessons/09_object_oriented_programming/README.md) | Use immutable dataclasses and cohesive application/domain objects without building a framework. |
| [Module 10: iteration, decorators, and contexts](../../lessons/10_iteration_decorators_and_contexts/README.md) | Use iterators, generators, and decorators for streaming reports. |
| [Module 11: typing, protocols, and dependency injection](../../lessons/11_typing_protocols_and_di/README.md) | Use strict type hints and `Protocol`-based capabilities for dependency injection. |
| [Module 12: automated testing](../../lessons/12_testing/README.md) | Test normal, boundary, and failure behavior with `unittest`, pytest, fakes, and temporary resources. |
| [Module 13: debugging and CLIs](../../lessons/13_debugging_and_cli/README.md) | Provide an `argparse` CLI, custom validators, subcommands, and useful logging. |
| [Module 14: environments, processes, and packaging](../../lessons/14_environments_processes_and_packaging/README.md) | Own subprocesses and streams, satisfy strict mypy coverage, Ruff compliance, and measured tests, and package a documented public API. |
| [Module 15: SQL and SQLite](../../lessons/15_sql_and_sqlite/README.md) | Own connections, use schema constraints and parameterized SQL, map rows, control transactions, and satisfy one repository contract with multiple adapters. |
| [Module 16: REST APIs and HTTP clients](../../lessons/11_rest_apis_and_clients/README.md) | Keep HTTP parsing and response validation behind injected boundaries, require finite timeouts, and test without public network access. |
| [Required Task REST API and clients project](../../projects/tasks/README.md) | Combine domain, repository, server, and client adapters while preserving dependency direction and one HTTP contract. |
| [Module 17: concurrency](../../lessons/12_concurrency/README.md) | Fetch independent HTTP pages with bounded threads, deterministic collection, cancellation, and explicit cleanup. |

## Normative event model

### Input record

Every source yields the same logical object:

```json
{
  "id": "evt-001",
  "occurred_at": "2026-07-16T08:00:00+00:00",
  "source": "checkout",
  "category": "request",
  "duration_ms": 125,
  "status": "success"
}
```

Rules:

- `id`: string matching `[A-Za-z0-9][A-Za-z0-9._:-]{0,63}`;
- `occurred_at`: RFC 3339 timestamp with `Z` or an explicit numeric offset;
  naive timestamps, leap seconds, and non-string timestamps are rejected;
- `source` and `category`: trimmed strings of 1–64 Unicode scalar values, with
  no C0/C1 control characters;
- `duration_ms`: JSON/CSV base-10 integer from `0` through `86_400_000`;
  booleans, fractions, exponent notation in CSV, and leading `+` are rejected;
- `status`: exactly `success`, `warning`, or `failure`;
- unknown JSON properties and unknown/missing CSV columns are rejected;
- duplicate JSON object member names are rejected as `invalid_shape`.

Normalized timestamps are UTC with millisecond precision:
`YYYY-MM-DDTHH:MM:SS.sssZ`. An input with finer precision is truncated, not
rounded. CSV uses this exact header and comma dialect:

```text
id,occurred_at,source,category,duration_ms,status
```

Files are UTF-8 without BOM. Blank JSONL lines are ignored; every other physical
line must contain exactly one JSON object. CSV blank records are rejected.

### Accepted, duplicate, and rejected records

The event identity is `(source, id)`. The first valid occurrence wins across all
imports. A later record with the same identity is a duplicate even if other
fields differ; it is counted but is not a reject and does not replace data.
HTTP source order is page number ascending, then item position, regardless of
fetch completion order.

A reject has this machine-readable shape:

```json
{
  "source_name": "fixture.csv",
  "record_number": 4,
  "code": "invalid_duration",
  "field": "duration_ms",
  "message": "duration_ms must be an integer from 0 through 86400000",
  "raw": {"duration_ms": "-1"}
}
```

`record_number` is one-based data-row number for CSV, physical line number for
JSONL, and item position within a page for HTTP. Required reject codes are:
`invalid_shape`, `missing_field`, `unknown_field`, `invalid_id`,
`invalid_timestamp`, `invalid_text`, `invalid_duration`, and `invalid_status`.
Messages are stable English fixture strings; callers classify by `code`.

### Persistence invariants

- The database has an explicit schema version and supports only version `1`.
- One import records its `import_id`, source kind/name, start time supplied by
  `Clock`, completion state, accepted/duplicate/rejected counts, and page issues.
- `import_id` matches `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` and is unique.
- Accepted events, rejects, and final import metadata commit atomically.
- Reusing a completed `import_id` returns `import_exists` without changing data.
- Unsupported/newer schemas and malformed database state fail closed; the
  program never silently drops or recreates user data.
- SQL table names and repository class layout are intentionally not normative.

## Observable commands

Commands run from the repository root. `<impl>` is `starter` or `solution`:

```bash
PYTHONPATH=capstones/idiomatic/<impl> \
  python -m ingest_report --db PATH ingest \
  --import-id ID --format csv --input FILE

PYTHONPATH=capstones/idiomatic/<impl> \
  python -m ingest_report --db PATH ingest \
  --import-id ID --format jsonl --input FILE

PYTHONPATH=capstones/idiomatic/<impl> \
  python -m ingest_report --db PATH ingest \
  --import-id ID --format http --url URL [--workers N] [--allow-partial]

PYTHONPATH=capstones/idiomatic/<impl> \
  python -m ingest_report --db PATH report \
  [--from TIMESTAMP] [--to TIMESTAMP] [--category VALUE] \
  [--status VALUE] [--output json|text]
```

Global `--json-errors` makes command failures use the error envelope below.
`--workers` is `1..16`, default `4`. File imports are streaming and do not use
the worker pool.

The public Python boundary also includes:

- `ingest_report.cli.main(argv: Sequence[str] | None = None) -> int`;
- immutable `Event`, `RejectedRecord`, `ImportResult`, and `Report` values;
- structural `RecordSource`, `EventRepository`, `Clock`, and `PageFetcher`
  protocols suitable for third-party fakes;
- no requirement that concrete implementation classes or helper functions have
  prescribed names.

### HTTP page contract

The required solution never needs public internet. `PageFetcher` receives the
base URL and page number. The loopback adapter requests `GET` with a `page=N`
query parameter and accepts:

```json
{
  "page": 1,
  "page_count": 3,
  "items": [
    {
      "id": "evt-001",
      "occurred_at": "2026-07-16T08:00:00Z",
      "source": "api",
      "category": "request",
      "duration_ms": 125,
      "status": "success"
    }
  ]
}
```

Page 1 is fetched first. `page_count` is `1..100`; pages 2 through
`page_count` may then be fetched concurrently. Each response is at most 1 MiB,
contains at most 1,000 items, has matching `page`, and has the same
`page_count`. Redirects, authentication, cookies, and retries are not required.

Without `--allow-partial`, any page transport/protocol failure rolls back the
import. With it, successful pages commit, failed page numbers are recorded,
the import state is `partial`, and the process still exits with the source I/O
failure code so automation cannot mistake partial data for complete data.

### Success output

`ingest` writes one JSON object to stdout:

```json
{
  "import_id": "run-001",
  "state": "complete",
  "accepted": 8,
  "duplicates": 1,
  "rejected": 2,
  "failed_pages": []
}
```

`report --output json` writes:

```json
{
  "filters": {
    "from": null,
    "to": null,
    "category": null,
    "status": null
  },
  "totals": {
    "events": 8,
    "duration_ms": 950,
    "rejected": 2
  },
  "by_category": [
    {"category": "request", "events": 8, "duration_ms": 950}
  ],
  "by_status": [
    {"status": "success", "events": 7, "duration_ms": 800},
    {"status": "warning", "events": 1, "duration_ms": 150}
  ],
  "rejects_by_code": [
    {"code": "invalid_duration", "count": 2}
  ]
}
```

Arrays sort by category/status/code using Python Unicode code-point order.
Filter bounds are inclusive. `from > to` is invalid. JSON is compared
semantically; indentation and object-member order are not contractual.
Reject totals/grouping cover all stored rejects because rejected records do not
necessarily have a valid timestamp/category/status to which event filters could
be applied.
Text output contains the same values in documented headings and is golden-tested.
Diagnostics go to stderr; successful stdout contains data only.

### Failure behavior

With `--json-errors`, stderr contains exactly one semantic envelope:

```json
{"error":{"code":"invalid_input","message":"...","details":{}}}
```

Required exit categories:

| Exit | Category | Example codes |
| --- | --- | --- |
| `0` | completed | complete import/report; rejects alone are data |
| `2` | CLI or user input | `invalid_argument`, `invalid_filter`, `invalid_import_id` |
| `3` | source content/protocol | `invalid_csv_header`, `invalid_jsonl`, `invalid_page` |
| `4` | source I/O or partial import | `source_unreadable`, `page_fetch_failed`, `partial_import` |
| `5` | database | `import_exists`, `unsupported_schema`, `database_error` |
| `130` | cancellation | `cancelled` |

Unexpected exceptions must not produce a traceback unless an explicit debug
option is used. Failed strict imports leave no accepted/rejected rows.

## Five guided milestones

### Milestone 1 — records and validation

Implement the immutable domain values, pure parser/normalizer, deduplication over
an iterable, and reject codes.

Acceptance:

- valid CSV-shaped and JSON-shaped dictionaries normalize identically;
- every field rule has normal, boundary, and failure tests;
- an iterator is consumed once without materializing the whole source;
- duplicate selection is stable and input ordered;
- `test_m1_domain.py` passes against the selected implementation.

### Milestone 2 — streaming application boundary

Implement CSV/JSONL sources, protocols, CLI parsing, import coordination, and
stable output without SQLite.

Acceptance:

- a fake repository proves records are passed incrementally;
- file handles close on success, parse failure, and cancellation;
- stdout/stderr and exit categories match the contract;
- `python -m compileall -q capstones/idiomatic/starter` succeeds even while later
  operations remain explicitly incomplete;
- `test_m2_sources_cli.py` passes.

### Milestone 3 — relational persistence

Implement schema initialization/version checks, transactional imports,
idempotent identities, reject persistence, and report queries.

Acceptance:

- reopen round trips preserve normalized values;
- duplicate imports and duplicate events do not mutate stored events;
- an injected mid-import failure rolls back all import rows;
- a newer/corrupt schema is reported without destructive recovery;
- SQL values are parameterized; `test_m3_repository.py` passes.

### Milestone 4 — reporting completeness

Implement filters, totals, grouped metrics, reject summaries, and text/JSON
renderers.

Acceptance:

- filters combine with logical AND and inclusive time bounds;
- empty reports contain zero totals and empty arrays;
- ordering is stable regardless of insertion order;
- renderer tests compare semantic JSON and golden text;
- `test_m4_reporting.py` passes.

### Milestone 5 — HTTP, concurrency, and integration

Implement the page adapter, bounded thread ownership, strict/partial semantics,
subprocess tests, and complete quality gates.

Acceptance:

- no more than `workers` page calls are active;
- completion order cannot change persisted or rendered order;
- cancellation stops scheduling, joins workers, and closes the database;
- loopback fixtures cover body bounds, malformed pages, and partial failure;
- CLI subprocess and coverage tests pass without DNS or public services;
- `test_m5_integration.py` and all repository gates pass.

## Starter, solution, and test architecture

```text
capstones/idiomatic/
├── SPEC.md
├── starter/ingest_report/
├── solution/ingest_report/
└── tests/
    ├── implementation.py
    ├── fixtures/
    └── test_m1_domain.py ... test_m5_integration.py
```

Starter and solution expose identical imports and command syntax. The starter
contains complete types, protocols, docstrings, argument parsing, and explicit
`IncompleteImplementationError` failures only where a milestone is unfinished.
Tests select one source root through
`CAPSTONE_IMPLEMENTATION=starter|solution`; they do not copy behavior between
implementations. `pyproject.toml` includes the completed solution in strict
mypy and coverage scopes; CI also type-checks the starter strictly without
weakening the other required capstone.

## Deterministic fixtures and injection seams

Required fixture set:

- `events-valid.csv`, `events-mixed.csv`, `events-valid.jsonl`, and
  `events-mixed.jsonl`;
- semantic equivalents across CSV/JSONL;
- `report-expected.json` and one expected text report;
- page payloads `http/page-1.json` through `page-3.json`;
- an unsupported-schema database produced by test setup, not a checked-in
  platform-specific database file.

Required seams are `RecordSource`, `EventRepository`, `Clock`, `PageFetcher`,
and an executor/factory or equivalent injection point. Tests use fixed times,
`TemporaryDirectory`, temporary SQLite files, controlled futures/events, and
`ThreadingHTTPServer` bound only to `127.0.0.1`. Correctness tests contain no
wall-clock sleeps, random IDs, environment-specific paths, or network calls.

## Dependencies and supported runtime

- Supported Python: `3.11` through `3.14`, matching current CI endpoints.
- Runtime dependencies: Python standard library only.
- Existing development constraints remain exactly:
  `coverage>=7.9,<8`, `mypy>=1.16,<2`, `pytest>=8.4,<10`, and
  `ruff>=0.12,<1` from [`requirements-dev.txt`](../../requirements-dev.txt).
- The capstone tests use `unittest`; pytest remains permitted for the course but
  is not required by this capstone.
- Rejected: pandas, NumPy, SQLAlchemy/other ORMs, Pydantic/schema frameworks,
  requests/httpx, date parsing packages, retry packages, and concurrency
  frameworks. No new pin is proposed.

The required solution runs on Linux, macOS, and Windows wherever Python and
SQLite from the standard library are available. Fixture paths must use
`pathlib`; file permissions and POSIX-only signals are not acceptance criteria.

## Exclusions

No dashboards, web UI/server API, authentication, cloud storage, distributed
queue, cron daemon, arbitrary SQL, user-defined report language, updates or
deletes of events, exactly-once distributed delivery, or performance benchmark
is required. The HTTP adapter is an ingestion boundary, not a production client.

## Quality and coverage commands

Focused learner commands:

```bash
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_m1_*.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -v
```

The repository harness runs these commands for this completed capstone:

```bash
ruff format --check .
ruff check .
mypy
python -m compileall -q \
  capstones/idiomatic/starter capstones/idiomatic/solution
CAPSTONE_IMPLEMENTATION=solution coverage run -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py'
coverage report
```

Repository-wide coverage is branch-aware with an 85% minimum and combines this
suite with the equally required comparative capstone. The canonical combined
command is in the [capstone overview](../README.md).

## Reuse guidance

Reuse patterns, not the task domain:

- `Protocol` and dependency-injection style, strict untrusted-dictionary
  narrowing, and `argparse`/exit separation;
- SQLite connection/transaction and temporary database testing patterns;
- injected HTTP and response validation patterns, also practiced in the current
  [Task REST API and clients project](../../projects/tasks/README.md);
- atomic export, temporary paths, and loopback server test support where useful.

Do not rename Task fields into events or preserve Task CRUD/storage interfaces.
