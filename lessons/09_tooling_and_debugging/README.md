# 🛠️ Module 9: Tooling and Debugging

The everyday tools that make writing, running and fixing Python code
easier - beyond the language itself.

## 🎯 Learning objectives

After this module, you should be able to isolate dependencies, invoke `pip`
reliably, interpret tracebacks, investigate state with a debugger, design a
command-line interface, and write concise `pytest` tests.

## 📦 Environments and dependencies

A virtual environment isolates one interpreter's installed packages. Create
one per project and install from a recorded dependency file. Prefer
`python -m pip` so `pip` is guaranteed to belong to the selected interpreter:

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -m pip list
```

Do not commit `.venv`. A dependency declaration states direct requirements;
a lock file, when a project uses one, records a reproducible resolved set.
Installing and importing are distinct: distribution names and import package
names can differ.

The built-in workflow is the portable baseline, not the only option. Tools such
as uv can also install Python, create environments, and install dependencies;
mise and asdf can select tool versions across several programming languages.
These tools automate parts of the workflow but do not remove the need to
understand interpreters, isolated environments, direct dependencies, and lock
files. See the [setup guide](../../docs/SETUP.md#optional-modern-setup-with-uv)
for an optional uv workflow.

## 🐞 A debugging method

1. Reproduce the smallest failing case.
2. Read the exception type and message at the traceback's end.
3. Find the first relevant frame in your own code.
4. Inspect assumptions and values at that point.
5. Form one hypothesis and test one change.
6. Add a regression test after fixing the defect.

`breakpoint()` pauses execution in `pdb`. Useful commands include `n` (next
line), `s` (step into), `c` (continue), `p expression` (print), `l` (list
source), and `q` (quit). Temporary print statements are useful, but structured
`logging` is better for persistent diagnostics because it supports levels,
destinations, and formatting.

## ⌨️ Command-line programs

`input()` is appropriate for an interactive conversation. `argparse` is better
for repeatable commands, validates input, generates help, and returns a
namespace. Define arguments in a parser, parse once near the application
boundary, and pass ordinary values into core logic. Send diagnostics to
standard error and use nonzero exit status for failure.

## 🧪 `pytest`

`pytest` discovers `test_*.py` files and `test_*` functions, rewrites plain
assertions to display useful differences, and provides fixtures for setup:

```python
import pytest

@pytest.mark.parametrize(("value", "expected"), [(2, 4), (-3, 9)])
def test_square(value, expected):
    assert value * value == expected
```

Fixtures are requested by parameter name and can use `yield` for cleanup.
Use `pytest.raises` for exceptions and `tmp_path` for isolated filesystem
tests. Keep production logic independent of the test framework.

## 📋 Logging and quality tools

Use `logging` for persistent diagnostics instead of scattering `print()` calls
through reusable code. Log levels let callers decide how much detail to retain.

`ruff check` finds common defects and style problems, `ruff format` applies
consistent formatting, `mypy` checks annotations without running the program,
and coverage reports which lines tests executed. These tools complement one
another; none proves that requirements or assertions are correct.

## 📚 Concepts covered

- **`01_virtual_environments_and_pip.py`** - what virtual environments are
  and why to use them, `pip` as Python's package installer, and how to
  check whether you're currently running inside a virtual environment.
- **`02_debugging_and_tracebacks.py`** - reading tracebacks, common
  exception types, and basic use of the interactive debugger (`pdb`).
- **`03_command_line_arguments.py`** - getting input interactively with
  `input()`, and parsing command-line arguments with `argparse`.
- **`04_pytest_basics.py`** - an introduction to `pytest`, the most
  widely used third-party testing framework, as an alternative to
  `unittest` (module 8). *Requires an optional dependency* - install it
  with `pip install -r requirements-dev.txt` from the repository root.
- **`05_logging_and_quality_tools.py`** - logging levels and the repository's
  Ruff, mypy and coverage workflow.

## ▶️ Running

```bash
python lessons/09_tooling_and_debugging/01_virtual_environments_and_pip.py
python lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py
python lessons/09_tooling_and_debugging/03_command_line_arguments.py
pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
python lessons/09_tooling_and_debugging/05_logging_and_quality_tools.py
```

Once you've read through all four files, practice what you learned in
[`exercises/09_tooling_and_debugging/`](../../exercises/09_tooling_and_debugging/README.md).

## ⚠️ Common mistakes

- Installing packages globally or through a different Python's `pip`.
- Reading only the first traceback line rather than the final exception.
- Changing several things before rerunning a failing case.
- Putting business logic directly inside argument-parsing branches.
- Giving tests shared access to real user files or network services.
- Logging secrets or using the root logger as an unstructured print substitute.
- Treating a clean linter or high coverage number as proof of correctness.

## ❓ Review questions

1. What problem does a virtual environment solve?
2. Why is `python -m pip` safer than an unqualified `pip`?
3. Which part of a traceback should you inspect first?
4. What belongs in CLI parsing versus core application logic?
5. How do parameterization and fixtures reduce test duplication?
6. How do linting, type checking, testing and coverage provide different
   feedback?
