# 🛠️ Exercises: Module 9 - Tooling and Debugging

Practice problems for [`lessons/09_tooling_and_debugging/`](../../lessons/09_tooling_and_debugging/README.md):
virtual environments, debugging, CLI and process boundaries, packaging,
documentation, logging, and [pytest](https://docs.pytest.org/en/stable/).

## 🧩 Tasks in `exercises.py`

- `build_arg_parser()` - build an `argparse.ArgumentParser` with a
  required positional argument and an optional flag.
- `build_command_parser()` - add `add` and `list` subcommands.
- `positive_int(text)` - implement a reusable argparse validator.
- `safe_int(text)` - catch only the conversion error you can handle.
- `configure_logger(verbose)` - select an appropriate logging level.
- `parse_process_timeout(environment)` - validate text configuration from a
  supplied environment mapping without mutating ambient process state.
- `build_child_command(message)` / `run_child_process(...)` - keep untrusted
  text as one subprocess argument and invoke the current Python interpreter
  without a shell.

## ▶️ How to work through it

1. Read [`lessons/09_tooling_and_debugging/`](../../lessons/09_tooling_and_debugging/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/09_tooling_and_debugging/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.

## 🔧 Guided tooling lab

The functions above practice program design. This lab practices the surrounding
developer flow without leaving deliberately broken files in the repository.
Install the development dependencies first by following
[`docs/SETUP.md`](../../docs/SETUP.md).

### 1. Reproduce and inspect a runtime failure

Lesson 9.2 intentionally calls `average([])` and catches the resulting exception:

```bash
python lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py
python -m pdb lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py
```

In `pdb`, run `break average`, `continue`, `p numbers`, `p len(numbers)`,
`where`, and `quit`. State the failed assumption before imagining a fix.

### 2. Run the narrowest relevant test

```bash
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py -v
```

Notice how [pytest](https://docs.pytest.org/en/stable/) reports each
parameterized case and supplies a separate `tmp_path` directory.

### 3. Apply and verify static checks

```bash
ruff format exercises/09_tooling_and_debugging
ruff check exercises/09_tooling_and_debugging
mypy
```

[Ruff](https://docs.astral.sh/ruff/) formats and lints the selected files.
[mypy](https://mypy.readthedocs.io/en/stable/) reads `pyproject.toml` and checks
the configured capstone solution packages; it does not check every lesson or
exercise. CI separately checks both starter packages with `mypy --strict`.

### 4. Measure the configured capstone coverage

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

[Coverage.py](https://coverage.readthedocs.io/en/stable/) can reveal unexecuted
configured code, but you must still judge whether tests contain useful
assertions and cover the right requirements. The cleanup script also removes
parallel subprocess data left by an interrupted earlier run.

### 5. Compare local checks with CI

Open [`.github/workflows/lessons.yml`](../../.github/workflows/lessons.yml) and
match each local command to the corresponding
[GitHub Actions](https://docs.github.com/en/actions) step. The goal is to find
problems before pushing, not to discover a different workflow after opening a
pull request.

### 6. Build and inspect the example distribution

The development requirements include
[build](https://build.pypa.io/en/stable/). Exercise the same isolated packaging
boundary that CI verifies:

```bash
python -m pip install -e lessons/09_tooling_and_debugging/example_distribution
python -m pydoc packaging_public_api_example
python -m build lessons/09_tooling_and_debugging/example_distribution
```

The editable install is for development. Inspect the generated wheel and sdist
under `dist/`, then remove generated `dist/`, `build/`, and `*.egg-info`
directories rather than committing them. The source of truth remains
`pyproject.toml` plus the package under `src/`.
