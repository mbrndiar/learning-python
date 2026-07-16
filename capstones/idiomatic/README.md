# Idiomatic Python capstone: ingestion and reporting

Build the offline-first data-ingestion and reporting pipeline defined in
[`SPEC.md`](SPEC.md). It complements the comparative key/value store with
Python-focused iterators, immutable dataclasses, protocols, SQLite, injected
HTTP, bounded concurrency, and deterministic reporting.

## Source roots and launcher

Both roots expose the `ingest_report` package:

```bash
PYTHONPATH=capstones/idiomatic/starter \
  python -m ingest_report --db events.db report --output json

PYTHONPATH=capstones/idiomatic/solution \
  python -m ingest_report --db events.db report --output json
```

The current scaffold parses documented command shapes and then raises
`IncompleteImplementationError`. It performs no file, network, or database
work.

Stable public boundaries:

- `ingest_report.cli.build_parser() -> argparse.ArgumentParser`;
- `ingest_report.cli.main(argv: Sequence[str] | None = None) -> int`;
- immutable `Event`, `RejectedRecord`, `ImportResult`, and `Report` values in
  `ingest_report.models`; and
- structural `RecordSource`, `EventRepository`, `Clock`, and `PageFetcher`
  protocols in `ingest_report.protocols`.

The starter and solution must keep those module and signature boundaries
identical while their internal implementations evolve.

## Selecting shared tests

```bash
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/idiomatic/tests -v

CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -v
```

`tests/implementation.py` validates the target and inserts exactly one source
root. The current smoke test covers imports, CSV/JSONL/HTTP/report parser
shapes, and the intentional incomplete boundary. Add future behavioral tests as
`test_m1_*.py` through `test_m5_*.py`; use fakes and loopback resources through
the specified protocols rather than patching private helpers.
