# Comparative capstone: versioned configuration store

Implement the frozen
[`comparative-kv` 1.0.0 specification](spec/SPEC.md) as the
`comparative_kv` Python package. Observable commands, JSON envelopes, SQLite
rules, fixtures, and process behavior come from the shared specification;
Python module design stays language-specific.

## Source roots and launcher

`starter/` and `solution/` expose identical public imports. Select one as the
Python source root:

```bash
PYTHONPATH=capstones/comparative/starter \
  python -m comparative_kv --db state.db list

PYTHONPATH=capstones/comparative/solution \
  python -m comparative_kv --db state.db list
```

The scaffold parses the command and then raises
`IncompleteImplementationError`. No database is opened. Replace that
intentional boundary milestone by milestone; do not add provisional output that
could be mistaken for conformance.

Stable Python boundaries:

- `comparative_kv.cli.build_parser() -> argparse.ArgumentParser`;
- `comparative_kv.cli.main(argv: Sequence[str] | None = None) -> int`;
- immutable result values in `comparative_kv.models`;
- the structural `comparative_kv.store.Store` protocol; and
- `comparative_kv.store.open_store(path)`.

Starter and solution may use different internals later, but these public module
and signature boundaries must remain aligned.

## Shared tests

Tests import `tests/implementation.py` first. It validates
`CAPSTONE_IMPLEMENTATION`, inserts exactly one source root, and gives every
future milestone test a stable `comparative_kv` import:

```bash
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/comparative/tests -v

CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/comparative/tests -v
```

The current smoke test checks imports, all four canonical parser shapes, and the
intentional incomplete execution boundary only. Future milestone tests should
be named `test_m1_*.py` through `test_m5_*.py` and must not inspect
implementation-private state.

## Specification integrity

Do not edit one language's shared spec copy independently. Verify the frozen
tree with:

```bash
(cd capstones/comparative/spec && sha256sum -c MANIFEST.sha256)
```
