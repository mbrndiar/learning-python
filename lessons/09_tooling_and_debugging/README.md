# 🛠️ Module 9: Tooling and Debugging

The everyday tools that turn editing a Python file into a repeatable development
workflow: isolate the project, reproduce a problem, inspect it, test the fix, and
run the same checks locally that continuous integration runs remotely.

## 🎯 Learning objectives

After this module, you should be able to isolate dependencies, invoke `pip`
through the intended interpreter, read a traceback, inspect state with `pdb`,
keep command-line parsing at the application boundary, write concise
[pytest](https://docs.pytest.org/en/stable/) tests, use logging deliberately,
cross environment/process/stream boundaries safely, distinguish an import
package from a distribution, document a public API, and explain what each
automated quality tool contributes.

## 🧭 One change, several kinds of feedback

Imagine you change a function that loads records. Running the program now raises
an exception. You first reproduce the smallest failure and read its traceback.
After inspecting the suspicious values in a debugger, you fix the function and
add a test that would have caught the defect. Only then do you run formatting,
linting, type checking, the wider test suite, and coverage. A pull request runs
the same checks in CI.

Each tool answers a different question:

| Tool | Question it answers | Typical command in this repository |
| --- | --- | --- |
| Traceback and `pdb` | What happened at runtime, and what values led there? | `python -m pdb path/to/script.py` |
| [Ruff formatter](https://docs.astral.sh/ruff/formatter/) | Is the code formatted consistently? | `ruff format .` |
| [Ruff linter](https://docs.astral.sh/ruff/linter/) | Does static inspection reveal likely defects or maintainability problems? | `ruff check .` |
| [mypy](https://mypy.readthedocs.io/en/stable/) | Are annotated values used consistently? | `mypy` |
| [pytest](https://docs.pytest.org/en/stable/) | Does observed behavior match test expectations? | `python -m pytest ...` |
| [Coverage.py](https://coverage.readthedocs.io/en/stable/) | Which configured code paths did the tests execute? | `coverage run ...` then `coverage report` |
| [build](https://build.pypa.io/en/stable/) | Can the example distribution produce an sdist and wheel through its declared backend? | `python -m build path/to/project` |
| [GitHub Actions](https://docs.github.com/en/actions) | Do the repository checks pass in a clean remote environment? | runs from `.github/workflows/lessons.yml` |

Passing one row does not imply the others pass. Formatting cannot prove
correctness, types cannot prove requirements, and high coverage cannot prove
that assertions are meaningful.

## 📦 Environments and dependencies

A virtual environment is a project-local Python installation directory. After
creating it, either activate it or invoke its interpreter explicitly before
installing packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip list
```

On Windows PowerShell, activate with
`.\.venv\Scripts\Activate.ps1`. Activation is only a shell convenience: it puts
the environment's `python` and installed commands first on `PATH`. Without
activation, you can use `.venv/bin/python` on Linux/macOS or
`.\.venv\Scripts\python.exe` on Windows.

Prefer `python -m pip` to a bare `pip`: the command is then executed by the same
interpreter named by `python`. Do not commit `.venv`; recreate generated
environments from dependency declarations.

These related files have different purposes:

- a dependency file such as `requirements-dev.txt` states packages this
  repository intentionally installs;
- transitive dependencies are packages those direct requirements need;
- `pip freeze` prints a snapshot of everything installed in one environment;
- a lock file, when a project adopts one, records a reproducible resolved set.

The built-in workflow is the portable baseline. The optional
[uv](https://docs.astral.sh/uv/) workflow in the
[setup guide](../../docs/SETUP.md#optional-modern-setup-with-uv) performs the
same responsibilities with a single Python-focused tool.

## 🖥️ Treat the process boundary as an interface

Environment variables are text configuration inherited by a process. Read and
validate only the names the application owns; do not log secrets merely because
they are available in `os.environ`. Standard input supplies data, standard
output carries normal results, standard error carries diagnostics, and the
integer exit status tells a caller whether the request succeeded.

When Python launches another program, pass an argument list to
`subprocess.run()` and use a finite timeout. `sys.executable` selects the same
Python interpreter that is running the parent. Capture output when the parent
must inspect it, use `check=True` when nonzero status is exceptional, and pass a
deliberately copied environment. Do not interpolate untrusted values into a
shell command; `shell=True` is not the default.

See the official [`subprocess`](https://docs.python.org/3/library/subprocess.html),
[`os`](https://docs.python.org/3/library/os.html), and
[`sys`](https://docs.python.org/3/library/sys.html) documentation.

## 📦 Build and document an installable distribution

An import package is a namespace loaded by Python. A distribution package is a
project installed by a packaging frontend and can provide one or more import
packages. The example in
[`example_distribution/`](example_distribution/README.md) uses the
recommended `src/` layout:

```text
example_distribution/
├── pyproject.toml
└── src/
    └── packaging_public_api_example/
        ├── __init__.py
        └── _greetings.py
```

`[build-system]` declares the build backend and its isolated requirements.
`[project]` contains backend-independent metadata such as the distribution name,
version, and supported Python versions. Install a local development checkout in
editable mode, then build both standard distribution artifacts:

```bash
python -m pip install -e lessons/09_tooling_and_debugging/example_distribution
python -m build lessons/09_tooling_and_debugging/example_distribution
```

Editable installation points the environment at working source; it is not the
release artifact. A wheel is built for installation, while an sdist contains
source from which a wheel can be built. Generated `dist/`, `build/`, and
metadata directories are outputs, not source files.

Docstrings describe public contracts. `help()` displays them interactively and
[`python -m pydoc`](https://docs.python.org/3/library/pydoc.html) renders them
from a terminal. Because `pydoc` imports a module, import-time side effects still
matter. Keep implementation rationale in selective comments rather than
promising it as public API.

Authoritative packaging references:

- [Python Packaging User Guide](https://packaging.python.org/)
- [packaging projects tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [pip local project installs](https://pip.pypa.io/en/stable/topics/local-project-installs/)
- [build](https://build.pypa.io/en/stable/)
- [setuptools `pyproject.toml` configuration](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)

## 🐞 Follow the failure, not a guess

Start with the final traceback line: it names the exception and gives the
immediate message. Then move upward to the deepest relevant frame in your code.
Frames describe the call path; they are not five independent errors.

Use this loop:

1. Reproduce the smallest failing input.
2. Read the final exception type and message.
3. Find the first relevant frame in your own code.
4. Inspect values and assumptions at that point.
5. State one hypothesis and change one thing.
6. Rerun the smallest case.
7. Add a regression test after the fix.

Lesson 9.2 deliberately calls `average([])`. Run it under the standard-library
debugger:

```bash
python -m pdb lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py
```

At the `(Pdb)` prompt, a short session might be:

```text
(Pdb) break average
(Pdb) continue
(Pdb) p numbers
[]
(Pdb) p len(numbers)
0
(Pdb) where
(Pdb) quit
```

Useful commands include `n` (next line), `s` (step into), `c` (continue),
`p expression` (evaluate an expression), `l` (list source), `where` (show the
stack), and `q` (quit). `breakpoint()` creates the same kind of pause from inside
code, but do not leave an unconditional breakpoint in committed code.

## ⌨️ Keep the CLI at the boundary

`input()` is useful for an interactive conversation. `argparse` is better for a
repeatable command because it validates input, generates `--help`, writes usage
errors to standard error, and exits nonzero for invalid arguments.

Parse once near the program boundary:

```python
def run(argv=None):
    args = build_parser().parse_args(argv)
    message = build_greeting(args.name, shout=args.shout)
    print(message)
    return 0
```

`build_greeting()` knows nothing about `argparse`, terminal output, or exit
codes. That separation makes the core behavior reusable from tests, another CLI,
or an HTTP handler.

## 🧪 Grow a test from one example

Start with one normal example, then identify what varies and what resources need
isolation:

```python
import pytest

@pytest.mark.parametrize(("value", "expected"), [(2, 4), (-3, 9)])
def test_square(value, expected):
    assert value * value == expected

def test_divide_by_zero_raises():
    with pytest.raises(ValueError, match="zero"):
        divide(10, 0)
```

Parameterization applies the same behavior to several inputs without a loop that
hides which case failed. Fixtures are requested by parameter name. The built-in
`tmp_path` fixture gives each test an isolated temporary directory; fixtures
using `yield` can release resources after the test. Production logic should not
import or depend on the test framework.

## 📋 Runtime diagnostics and automated checks

Use a temporary `print()` when exploring a tiny local value, `pdb` when you need
to pause and inspect control flow, and `logging` for diagnostics that should
remain in reusable or deployed code. A module logger created with
`logging.getLogger(__name__)` lets the application choose the level, formatting,
and destination. Log identifiers and useful context, but never passwords,
tokens, or other secrets.

After a code change, use a narrow-to-wide loop:

```bash
# Reproduce the relevant behavior first.
python lessons/09_tooling_and_debugging/05_logging_and_quality_tools.py
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py -v

# Apply formatting, then run static checks.
ruff format .
ruff check .
mypy

# Run both required capstone suites under configured coverage.
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

The repository cleanup script is restricted to the generated `.coverage-data/`
directory and removes both the primary database and parallel subprocess files.
The process-level capstone contracts cannot be measured correctly from the
parent test runner alone. Cleaning both forms prevents an interrupted earlier
run from contaminating the next `coverage combine`.

`ruff format .` changes files; CI uses `ruff format --check .` to verify that
formatting was already applied. The current mypy configuration checks the typed
application files listed in `pyproject.toml`, not every beginner lesson. The
coverage configuration measures both capstone reference implementations and
omits their launcher modules. Read tool output in that configured scope instead
of assuming it describes the entire repository.

## 📚 Concepts covered

- **`01_virtual_environments_and_pip.py`** - interpreters, virtual environments,
  reliable `pip` invocation, and dependency-file responsibilities.
- **`02_debugging_and_tracebacks.py`** - traceback frames, common exception
  types, and a guided `pdb` investigation.
- **`03_command_line_arguments.py`** - `input()`, `argparse`, subcommands, and
  separation between parsing and core logic.
- **`04_pytest_basics.py`** - plain assertions, parameterization,
  `pytest.raises`, and the `tmp_path` fixture. Install the optional development
  dependencies with `python -m pip install -r requirements-dev.txt`.
- **`05_logging_and_quality_tools.py`** - logging levels and the repository's
  Ruff, mypy, test, coverage, and CI workflow.
- **`06_os_processes_and_streams.py`** - environment validation, stdin/stdout/
  stderr, exit statuses, and safe portable child processes with
  `subprocess.run()`.
- **`07_packaging_and_public_apis.py`** - import packages versus distributions,
  `pyproject.toml`, `src/` layout, editable installs, wheels, sdists, docstrings,
  `help()`, and `pydoc`, using the adjacent example distribution.

## ▶️ Running

```bash
python lessons/09_tooling_and_debugging/01_virtual_environments_and_pip.py
python lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py
python lessons/09_tooling_and_debugging/03_command_line_arguments.py
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py -v
python lessons/09_tooling_and_debugging/05_logging_and_quality_tools.py
python lessons/09_tooling_and_debugging/06_os_processes_and_streams.py
python lessons/09_tooling_and_debugging/07_packaging_and_public_apis.py
```

Once you've read through all seven files, practice the complete flow in
[`exercises/09_tooling_and_debugging/`](../../exercises/09_tooling_and_debugging/README.md).

## ⚠️ Common mistakes

- Creating `.venv` but installing through the system interpreter.
- Treating `pip freeze` as a carefully maintained list of direct dependencies.
- Reading only the first traceback line rather than the final exception.
- Changing several things before rerunning the smallest failing case.
- Putting business logic directly inside argument-parsing branches.
- Logging environment values that may contain secrets.
- Building a shell command by interpolating untrusted text.
- Treating an editable install as the artifact that should be published.
- Confusing a distribution name with the import package it provides.
- Running substantial work when a module is imported for `help()` or `pydoc`.
- Giving tests shared access to real user files or network services.
- Logging secrets or using the root logger as an unstructured print substitute.
- Treating a clean linter, type checker, or high coverage number as proof of
  correctness.

## ❓ Review questions

1. What changes when a virtual environment is activated?
2. How do a dependency declaration, a frozen snapshot, and a lock file differ?
3. Which traceback frame and values would you inspect first?
4. What belongs in CLI parsing versus core application logic?
5. How do parameterization and fixtures reduce duplication and shared state?
6. When would you choose `print()`, `pdb`, or `logging`?
7. What information belongs on stdout, stderr, and the process exit status?
8. Why should subprocess arguments normally be passed as a list?
9. How do an import package, distribution package, editable install, wheel, and
   sdist differ?
10. Why can generating documentation expose import-time side effects?
11. How do formatting, linting, type checking, testing, coverage, and CI provide
   different feedback?
