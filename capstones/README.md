# 🏆 Capstones

This course ends with two completed, equally required projects:

- [`comparative/`](comparative/README.md) implements the same versioned SQLite
  key/value contract as the other language courses.
- [`idiomatic/`](idiomatic/README.md) builds a Python-focused data-ingestion and
  reporting pipeline.

Start them after Modules 1–12 and the required
[Task REST API and clients project](../projects/tasks/README.md). In particular,
Module 10 supplies SQL/SQLite, Module 11 supplies HTTP boundaries, the applied
project combines those skills, and Module 12 supplies concurrency.

Each track has a `starter/` and a `solution/` source root with the same public
package boundary. The shared tests choose one root with
`CAPSTONE_IMPLEMENTATION=starter|solution`; they never copy code between the
two implementations.

| Track | Learner guide | Contract and fixtures |
| --- | --- | --- |
| Comparative | [`comparative/README.md`](comparative/README.md) | [`SPEC.md`](comparative/spec/SPEC.md), [`SCENARIOS.md`](comparative/spec/SCENARIOS.md), and [`fixtures/`](comparative/spec/fixtures/) |
| Idiomatic | [`idiomatic/README.md`](idiomatic/README.md) | [`SPEC.md`](idiomatic/SPEC.md) and [`tests/fixtures/`](idiomatic/tests/fixtures/) |

## Included implementation

Both capstones contain complete standard-library reference solutions,
deterministic fixtures, and five milestone test groups. Their starters remain
compileable, strictly typed guides with progressive `TODO(m1)` through
`TODO(m5)` boundaries.

## Recommended workflow

1. Read the track README and specification.
2. Work in `starter/` one milestone at a time.
3. Run only that milestone's selected tests.
4. Run the complete starter suite before comparing with `solution/`.
5. Recreate useful ideas yourself rather than copying the reference source.

Run commands from the repository root. The current harness checks are:

```bash
python -m compileall -q \
  capstones/comparative/starter capstones/comparative/solution \
  capstones/idiomatic/starter capstones/idiomatic/solution
(cd capstones/comparative/spec && sha256sum -c MANIFEST.sha256)

CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/comparative/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/comparative/tests -p 'test_*.py' -v

CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py' -v
```

Repository quality checks also cover the scaffolding:

```bash
ruff format --check .
ruff check .
mypy
mypy --strict \
  capstones/comparative/starter/comparative_kv \
  capstones/idiomatic/starter/ingest_report
python scripts/check_markdown_links.py
```

Measure the two reference implementations together:

```bash
python scripts/erase_coverage_data.py
CAPSTONE_IMPLEMENTATION=solution CAPSTONE_SUBPROCESS_COVERAGE=1 \
  coverage run --parallel-mode -m unittest \
    discover -s capstones/comparative/tests -p 'test_*.py'
CAPSTONE_IMPLEMENTATION=solution CAPSTONE_SUBPROCESS_COVERAGE=1 \
  coverage run --parallel-mode -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py'
coverage combine
coverage report
```

The removed predecessor Task examples are historical material, not a third
capstone. They are separate from the current required Task REST API and clients
project. Use the
[migration guide](../docs/CAPSTONE_MIGRATION.md) to map their concepts and
commands to these two required capstones or inspect their Git revision.
