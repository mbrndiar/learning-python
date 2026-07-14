# 🛠️ Exercises: Module 9 - Tooling and Debugging

Practice problems for [`lessons/09_tooling_and_debugging/`](../../lessons/09_tooling_and_debugging/README.md):
virtual environments, debugging, CLI arguments, logging, and
[pytest](https://docs.pytest.org/en/stable/).

## 🧩 Tasks in `exercises.py`

- `build_arg_parser()` - build an `argparse.ArgumentParser` with a
  required positional argument and an optional flag.
- `build_command_parser()` - add `add` and `list` subcommands.
- `positive_int(text)` - implement a reusable argparse validator.
- `safe_int(text)` - catch only the conversion error you can handle.
- `configure_logger(verbose)` - select an appropriate logging level.

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
the configured typed files in `project/`; it does not currently check every
lesson or exercise.

### 4. Measure the configured project coverage

```bash
coverage run -m unittest \
  project.task_rest_api.test_api \
  project.task_rest_client.test_client \
  project.task_manager.test_task_manager
coverage report
```

[Coverage.py](https://coverage.readthedocs.io/en/stable/) can reveal unexecuted
configured code, but you must still judge whether tests contain useful
assertions and cover the right requirements.

### 5. Compare local checks with CI

Open [`.github/workflows/lessons.yml`](../../.github/workflows/lessons.yml) and
match each local command to the corresponding
[GitHub Actions](https://docs.github.com/en/actions) step. The goal is to find
problems before pushing, not to discover a different workflow after opening a
pull request.
