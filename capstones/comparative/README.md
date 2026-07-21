# ⚖️ Comparative capstone: versioned configuration store

Implement the frozen [`comparative-kv` 1.0.0 specification](spec/SPEC.md) as
the standard-library `comparative_kv` package. The shared contract fixes the CLI,
JSON envelopes, SQLite schema, migration, revisions, compare-and-set behavior,
and independent-process contention; the Python module design remains local.
This is one of the course's
[two completed, equally required capstones](../README.md).
Begin after Modules 1–12 and the required
[Task REST API and clients project](../../projects/tasks/README.md).

## 🗂️ Choose a source root

Both roots expose the same public package:

- [`starter/comparative_kv/`](starter/comparative_kv/) is a compileable,
  strictly typed guide. Search for `TODO(m1)` through `TODO(m5)` and implement
  one boundary at a time.
- [`solution/comparative_kv/`](solution/comparative_kv/) is the complete Python
  3.11 through 3.14 reference implementation using `argparse`, `json`, and
  `sqlite3`.

Run either launcher from the repository root:

```bash
PYTHONPATH=capstones/comparative/starter \
  python -m comparative_kv --db state.db list

PYTHONPATH=capstones/comparative/solution \
  python -m comparative_kv --db state.db list
```

The untouched starter parses the documented command and raises
`IncompleteImplementationError` before opening storage. It never emits
provisional output that could be confused with conformance.

## 🪜 Guided milestones

1. **Domain:** keys, expectations, safe revisions, restricted JSON,
   exact-decimal integral checks, depth/byte limits, duplicates, and surrogates.
2. **CLI:** exact grammar, validation precedence, compact envelopes, stderr
   discipline, and exit-code mapping.
3. **SQLite:** literal paths, WAL configuration, exact v1 initialization,
   invariant checks, and atomic v0 migration.
4. **Mutations:** global revisions, any/absent/exact CAS, immediate
   transactions, ordering, exhaustion, and failure accounting.
5. **Processes:** initialization and migration races, writer/CAS/delete
   contention, busy waiting and timeout, integrity checks, and sidecar cleanup.

The shared tests select a source root with
`CAPSTONE_IMPLEMENTATION=starter|solution`. Run the next starter milestone as a
deliberately red target:

```bash
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/comparative/tests -p 'test_m1_*.py' -v
```

Advance through `test_m5_*.py`. CI runs only the starter smoke test; it runs all
five suites against the solution.

## 🛡️ Public boundaries

- `comparative_kv.cli.build_parser() -> argparse.ArgumentParser`;
- `comparative_kv.cli.main(argv) -> int`;
- immutable results in `comparative_kv.models`;
- domain helpers in `comparative_kv.domain`;
- the structural `comparative_kv.store.Store` protocol; and
- `comparative_kv.store.open_store(path)`.

## ✅ Quality and conformance commands

```bash
(cd capstones/comparative/spec && sha256sum -c MANIFEST.sha256)
python -m compileall -q \
  capstones/comparative/starter capstones/comparative/solution
mypy --strict capstones/comparative/starter/comparative_kv
mypy
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/comparative/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/comparative/tests -p 'test_*.py' -v
ruff format --check .
ruff check .
```

Milestone 5 launches real child interpreters through argument lists, not shell
strings. Its barrier actors, independent lock helper, required fixture repeats,
timeouts, and explicit database/WAL cleanup follow
[`spec/SCENARIOS.md`](spec/SCENARIOS.md).
