# 🏆 Capstones

This course ends with two equally required projects:

- [`comparative/`](comparative/README.md) implements the same versioned SQLite
  key/value contract as the other language courses.
- [`idiomatic/`](idiomatic/README.md) builds a Python-focused data-ingestion and
  reporting pipeline.

Each track has a `starter/` and a `solution/` source root with the same public
package boundary. The shared tests choose one root with
`CAPSTONE_IMPLEMENTATION=starter|solution`; they never copy code between the
two implementations.

## Current scaffold status

Both source roots currently provide importable packages, typed public values and
protocols, command parsers, and explicit incomplete-operation errors. They do
not implement any milestone behavior yet. This is intentional: the harness can
be validated before either reference implementation is written.

## Recommended workflow

1. Read the track README and specification.
2. Work in `starter/` one milestone at a time.
3. Run only that milestone's selected tests as they are added.
4. Run the complete starter suite before comparing with `solution/`.
5. Recreate useful ideas yourself rather than copying the reference source.

Run commands from the repository root. The current harness checks are:

```bash
python -m compileall -q \
  capstones/comparative/starter capstones/comparative/solution \
  capstones/idiomatic/starter capstones/idiomatic/solution

for implementation in starter solution; do
  CAPSTONE_IMPLEMENTATION="$implementation" python -m unittest \
    discover -s capstones/comparative/tests -p 'test_*.py' -v
  CAPSTONE_IMPLEMENTATION="$implementation" python -m unittest \
    discover -s capstones/idiomatic/tests -p 'test_*.py' -v
done
```

Repository quality checks also cover the scaffolding:

```bash
ruff format --check .
ruff check .
mypy
mypy --strict \
  capstones/comparative/starter/comparative_kv \
  capstones/idiomatic/starter/ingest_report
```

The existing projects under [`../project/`](../project/README.md) remain in
place until both new capstones are fully implemented and pass all quality gates.
