# Setting Up Your Environment

Before starting the lessons, get Python installed and a project workspace
ready. This only needs to be done once.

## 1. Install Python

1. Download Python 3.11 or newer from https://www.python.org/downloads/
   (on Linux, use your package manager, e.g. `sudo apt install python3`).
2. Verify the installation:

   ```bash
   python3 --version
   ```

   On Windows the command is usually `python --version`.

   If several Python versions are installed, prefer invoking tools through the
   selected interpreter, for example `python3 -m pip`, rather than relying on a
   separate `pip` command that may belong to another installation.

## 2. Get the code

Clone this repository (or download it as a ZIP) and open a terminal in the
project's root directory:

```bash
git clone https://github.com/mbrndiar/learning-python.git
cd learning-python
```

## 3. Create a virtual environment

A virtual environment keeps this project's Python packages isolated from
the rest of your system. Modules 1–10, Module 11's HTTP fundamentals lesson,
Module 12, and both capstones use only the standard library. Module 11's
framework/client comparisons and the required Task project use project-local
runtime dependencies. A virtual environment keeps those and the development
tools isolated.

```bash
# Create the environment (creates a .venv/ folder)
python3 -m venv .venv

# Activate it
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate.bat       # Windows Command Prompt
.venv\Scripts\Activate.ps1      # Windows PowerShell
```

Once activated, your shell prompt is usually prefixed with `(.venv)`. To
leave the virtual environment, run `deactivate`.

## 4. Install dependencies

The development requirements add
[pytest](https://docs.pytest.org/en/stable/),
[Ruff](https://docs.astral.sh/ruff/),
[mypy](https://mypy.readthedocs.io/en/stable/), and
[Coverage.py](https://coverage.readthedocs.io/en/stable/) so you can practice
testing, formatting, linting, static type checking, and coverage measurement:

```bash
python -m pip install -r requirements-dev.txt
```

Before running all of Module 11 or the required applied project, install its
runtime dependencies too:

```bash
python -m pip install -r projects/tasks/requirements.txt
```

## 5. Choose an editor

Any text editor works. If you are looking for a recommendation, both
[VS Code](https://code.visualstudio.com/) (with the Python extension) and
[PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/)
are free and beginner-friendly.

## 6. Run your first lesson

```bash
python lessons/01_basics/01_hello_world.py
```

If you see `Hello, World!` printed, you're ready to start. Continue to the
[course guide in the README](../README.md).

Near the end of the course, follow the required order: Module 10 SQL/SQLite,
Module 11 REST APIs and clients, the
[Task REST API and clients project](../projects/tasks/README.md), Module 12
concurrency, then both capstones.

## Optional modern setup with uv

The `venv` and `pip` workflow above is built into Python, widely available, and
worth understanding. [uv](https://docs.astral.sh/uv/) is a Python-focused
third-party tool that can install Python versions, create environments, install
packages, and run commands in the selected environment.

After following the official
[uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/),
run from the repository root:

```bash
uv python install 3.14
uv venv --python 3.14
uv pip install -r requirements-dev.txt
uv pip install -r projects/tasks/requirements.txt
source .venv/bin/activate
python lessons/01_basics/01_hello_world.py
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
ruff format .
ruff check .
mypy
```

On Windows, use the activation command from section 3. The explicit `uv venv`
and `uv pip install` commands mirror the course's existing dependency-file
workflow; they do not convert this repository into a packaged project or
introduce a lockfile.

`uv pip sync` is intentionally not used here. Syncing is appropriate when the
input already describes the complete resolved environment. This repository's
`requirements-dev.txt` lists direct development requirements and relies on the
installer to resolve their transitive dependencies.

## Daily development flow

Start narrow: reproduce the behavior you changed before running every check.
For example:

```bash
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py -v
```

Then apply formatting and run the configured static checks:

```bash
ruff format .
ruff check .
mypy
mypy --strict \
  capstones/comparative/starter/comparative_kv \
  capstones/idiomatic/starter/ingest_report
python scripts/check_markdown_links.py
```

Ruff's formatter command changes files. Continuous integration uses
`ruff format --check .` to verify that formatting has already been applied.
`ruff check --fix .` can apply supported lint fixes, but review those changes
instead of treating automatic repair as proof that behavior is correct.

Compile both source roots, verify the frozen comparative fixtures, and smoke
test both untouched starters:

```bash
python -m compileall -q \
  capstones/comparative/starter capstones/comparative/solution \
  capstones/idiomatic/starter capstones/idiomatic/solution
(cd capstones/comparative/spec && sha256sum -c MANIFEST.sha256)
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/comparative/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_harness.py' -v
```

Course completion requires both reference suites. Measure their configured
branch coverage together:

```bash
coverage erase
CAPSTONE_IMPLEMENTATION=solution CAPSTONE_SUBPROCESS_COVERAGE=1 \
  coverage run --parallel-mode -m unittest \
    discover -s capstones/comparative/tests -p 'test_*.py'
CAPSTONE_IMPLEMENTATION=solution coverage run --parallel-mode -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py'
coverage combine
coverage report
```

After uv creates and populates `.venv`, the activated daily commands are
deliberately identical. The tool has changed how Python and packages reached the
environment, not what Ruff, mypy, pytest, or Coverage.py are responsible for.

The repository's
[GitHub Actions workflow](https://docs.github.com/en/actions) runs these checks
in a clean environment. Running them locally first shortens the feedback loop;
CI confirms that the result does not depend on unrecorded local state.

The predecessor Task examples have been removed and do not define any
development gates. The [migration guide](CAPSTONE_MIGRATION.md) maps their
concepts to the two required capstones and records where to inspect the removed
source in Git history. The current
[`projects/tasks/`](../projects/tasks/README.md) applied project is a new,
required course stage rather than a restored legacy path.

## Troubleshooting

### `python` or `python3` is not found

Close and reopen the terminal after installation. On Windows, ensure the
installer's **Add Python to PATH** option was selected. You can also try the
Python launcher: `py --version` and `py -m venv .venv`.

### Activating the environment is blocked in PowerShell

PowerShell execution policy may block `Activate.ps1`. You can still use the
environment without activation:

```powershell
.\.venv\Scripts\python.exe lessons\01_basics\01_hello_world.py
```

Activation is a convenience; it mainly puts the environment's executables
first on `PATH`.

### `pip` installs into the wrong Python

Run `python -m pip --version` and check the displayed path. It should point
inside `.venv` while the environment is active.

For uv, run `uv python find` to inspect the selected interpreter and
`uv pip list` to inspect the environment.

### Leaving or recreating an environment

Run `deactivate` to leave it. A virtual environment contains generated files,
so it is safe to delete `.venv` and recreate it from
`requirements-dev.txt`; do not commit `.venv` to version control.

With uv, recreate the environment with:

```bash
uv venv --python 3.14 --clear
uv pip install -r requirements-dev.txt
```
