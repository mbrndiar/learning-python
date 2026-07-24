# 🧰 Chapter 14: Environments, Processes, and Packaging

**Semantic ID:** `module.environments-processes-and-packaging` ·
**Prerequisites:** `module.debugging-and-cli`

## 📍 Where this fits

This is the last of the three tooling chapters. Chapter 12 gave you tests,
Chapter 13 gave you debugging and command-line boundaries, and this chapter
takes your programs across the remaining boundaries of a real project:
isolating dependencies in a virtual environment, reading configuration from
the environment, crossing the standard-stream and exit-status boundary,
owning a child process safely, running the automated quality gates that
guard the whole repository, and packaging code into a distribution with a
documented public API. After this chapter the course turns to applied
domains — SQL, HTTP, the Task project, and concurrency.

## 🎯 Learning objectives

After this chapter, you should be able to:

- explain why projects isolate dependencies and detect whether the current
  interpreter is inside a virtual environment;
- run `pip` through the intended interpreter with `python -m pip`;
- read configuration from environment variables without exposing secrets,
  send output to the correct standard stream, and report success or failure
  through an integer exit status;
- start a child process safely: `sys.executable`, an argument list (no
  shell), an explicit allowlisted environment, owned stdin, captured text
  output, a finite timeout, `check=True`, and a specific error taxonomy;
- explain what formatting, linting, type-checking, testing, coverage, and CI
  each prove and do not prove, and run each with a bounded command;
- distinguish an import package from a distribution package, read
  `pyproject.toml`, and document a public API; declare a console entry point
  with `[project.scripts]`.

## 🧠 Motivation and mental model

Every topic here is a boundary between your program and something outside
it. A **virtual environment** is the boundary around a project's installed
packages, so one project's versions cannot break another's. The
**environment and standard streams** are the boundary with the operating
system: environment variables carry configuration in, stdin carries data in,
stdout carries results out, stderr carries diagnostics out, and the exit
status carries a single pass/fail signal to whatever launched you. A
**subprocess** is a boundary with another program; crossing it carelessly
(interpolating text into a shell command) is a classic security hole, so you
pass an argument list and own every input and limit explicitly. The
**quality gates** are the boundary between "works on my machine" and "works
in a clean environment," and **packaging** is the boundary between your
source tree and an installable artifact other people import.

The recurring discipline is the same one from Chapter 13: keep pure logic in
functions that take plain arguments (a mapping, a message) and push the
messy, real-world edges (`os.environ`, `subprocess`, the network) to a thin
boundary you can reason about and test.

## 1️⃣ Virtual environments and pip

`sys.prefix` points at the active environment; `sys.base_prefix` points at
the base installation. They are equal outside a venv and differ exactly
when one is active -- a signal read from the interpreter itself, not from
a shell variable that might be stale or unset. `sys.executable` is the
interpreter actually running this process, so `python -m pip install ...`
guarantees packages land in *that* interpreter's environment, regardless
of what a bare `pip` on `PATH` might resolve to.

```python
def in_virtual_env() -> bool:
    """Return True if the current interpreter is running inside a venv."""
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)
```

```text
Python executable: /home/.../learning-python/.venv/bin/python
Python version: 3.11.13
Running inside a virtual environment? True
Standard library location: /home/.../cpython-3.11-linux-x86_64-gnu/lib/python3.11
```

A venv isolates installed third-party packages but reuses the base
interpreter's standard library, so `Standard library location:` still
resolves to a real path either way.

Run the complete companion:

```bash
python lessons/14_environments_processes_and_packaging/01_virtual_environments_and_pip.py
```

See
[`01_virtual_environments_and_pip.py`](01_virtual_environments_and_pip.py)
for the full sequence, including the printed venv-creation, activation,
and `pip install`/`list`/`freeze` commands -- **documented text the script
prints, not commands it executes**; nothing is created or installed by
running this lesson.

> **Try one change:** run the file once through `.venv/bin/python` (or
> with the venv activated) and once through a system `python3` outside
> any venv. Predict the difference: `in_virtual_env()` reports `True` in
> one run and `False` in the other, and `Standard library location:`
> changes to match each interpreter's own stdlib path -- no package is
> installed by either run.

## 2️⃣ Environment, standard streams, and exit status

`token_is_configured(environment)` reads from a **supplied mapping**, not
`os.environ` directly, so a test can pass its own dict; on an invalid
token it raises a `ValueError` naming the variable and the rule --
**never the value**. `print(...)` writes to stdout, for results a caller
might parse; `print(..., file=sys.stderr)` writes diagnostics, for a
human to read. `main()` returns an `int`, and `raise SystemExit(main())`
turns that return value into the actual process exit status, where `0`
means success.

```python
def token_is_configured(environment: Mapping[str, str]) -> bool:
    token = environment.get(TOKEN_VARIABLE)
    if token is None:
        return False
    if token != token.strip() or len(token) < 8:
        raise ValueError(f"{TOKEN_VARIABLE} must contain at least 8 characters")
    return True
```

```text
# stdout only (2>/dev/null):
LEARNING_PYTHON_API_TOKEN configured: False
stdin supplies input; this noninteractive lesson does not read it.
stdout carries normal program results.
Returning exit status 0 (zero means success).

# stderr only (2>&1 1>/dev/null):
stderr carries diagnostics.
```

Splitting the two streams like this shows they never mix by accident, and
that neither one ever contains a token value -- only whether one is
configured.

Run the complete companion (it deliberately uses a fixed, empty mapping so
ambient environment variables on your machine cannot change its output):

```bash
python lessons/14_environments_processes_and_packaging/02_environment_streams_and_exit_status.py
```

See
[`02_environment_streams_and_exit_status.py`](02_environment_streams_and_exit_status.py)
for the full sequence, including `run_from_process`, which is the real
application boundary that would supply `os.environ` instead of a fixed
mapping.

> **Try one change (a shell-level check, not a Python change):** run the
> script and inspect its real exit status directly:
>
> ```bash
> python lessons/14_environments_processes_and_packaging/02_environment_streams_and_exit_status.py; echo "exit status: $?"
> ```
>
> Then pass it an unexpected extra argument, e.g. `... 02_environment_streams_and_exit_status.py extra`. Predict the
> result: the usage message goes to stderr and the exit status becomes
> `2`, distinct from the `0` success path.

## 3️⃣ Owning a subprocess safely

Build the command as an **argument list**, `[sys.executable, "-c", code,
message]`, never an interpolated shell string -- `message` stays one
value even if it contains spaces or shell metacharacters, because there
is no shell to reinterpret it. Copy only the variables the child actually
needs into its environment instead of forwarding the full parent
environment. `stdin=subprocess.DEVNULL` guarantees the child can never
block waiting for input that will never arrive; `capture_output=True,
text=True` reads decoded stdout/stderr; a finite `timeout` and
`check=True` turn a hang or a nonzero exit into a specific exception
instead of a silently "successful" result.

```python
def build_child_command(message: str) -> list[str]:
    child_code = "import sys; print(sys.argv[1])"
    return [sys.executable, "-c", child_code, message]


def run_child(message: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        build_child_command(message),
        env=build_child_environment(),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=5,
        check=True,
    )
```

```text
child stdout: result from child
child exit status: 0 (zero means success)
```

Three distinct exceptions map to three distinct failure modes:
`subprocess.TimeoutExpired` (ran too long), `subprocess.CalledProcessError`
(ran, exited nonzero), and `OSError` (could not even start) -- `main()`
handles each separately instead of one broad `except`.

Run the complete companion:

```bash
python lessons/14_environments_processes_and_packaging/03_subprocess_ownership.py
```

See [`03_subprocess_ownership.py`](03_subprocess_ownership.py) for the
full sequence, including `main`'s three-way `except` block mapping each
subprocess failure to its own exit status.

> **Try one change:** without running anything, predict what would change
> if the call site passed a different string, e.g. `run_child("hello
> there")` instead of `run_child("result from child")`. Only the echoed
> `child stdout: ...` line changes; every other ownership decision
> (argument list, `stdin=DEVNULL`, `timeout=5`, `check=True`) stays the
> same regardless of the message's content -- exactly why passing it as
> one argument-list element, not a shell string, matters.

## 4️⃣ Format, lint, type, test, coverage, and CI

Formatting, linting, typing, testing, coverage, and CI each answer a
distinct question, and passing one never implies another. This
companion only **prints** its bounded commands; it never runs Ruff,
mypy, pytest, or coverage itself. This repository's actual formatting
gate is check-only: `ruff format --check <path>` reports whether files
already match the required style **without rewriting them**, unlike a
bare `ruff format <path>`, which rewrites files in place -- the
companion and this course's CI both use the check-only form. Bare `mypy`
reads `pyproject.toml`'s `[tool.mypy]` table, which lists specific
capstone/project packages under `files = [...]`; it does not type-check
every lesson or exercise. Coverage measures which configured lines
executed, never whether the assertions covering them are meaningful.

```python
QUALITY_GATES = (
    (
        "format check",
        "does this chapter match one consistent style?",
        "ruff format --check lessons/14_environments_processes_and_packaging "
        "exercises/14_environments_processes_and_packaging",
    ),
    ("type-check", "do the type annotations hold?", "mypy"),
    (
        "test (bounded)",
        "does observed behavior match expectations?",
        "python -m pytest lessons/12_testing/"
        "03_pytest_assertions_parameterization_and_fixtures.py -v",
    ),
)
```

```text
DEBUG __main__: calculating total for 3 prices
INFO __main__: calculated total 20.00
Total: 20.0

Automated quality gates (each answers a different question):
  format check: does this chapter match one consistent style?
    $ ruff format --check lessons/14_environments_processes_and_packaging exercises/14_environments_processes_and_packaging
  ...
  type-check: do the type annotations hold?
    $ mypy
```

Run the complete companion (this executes only the Python script above --
it does not itself invoke Ruff, mypy, pytest, or coverage):

```bash
python lessons/14_environments_processes_and_packaging/04_format_lint_type_test_coverage_ci.py
```

See
[`04_format_lint_type_test_coverage_ci.py`](04_format_lint_type_test_coverage_ci.py)
for the full sequence, including the `lint` and `coverage` gates and a
note pointing to `.github/workflows/course.yml`, where CI runs these same
kinds of gates in a clean environment.

> **Try one change:** the printed commands are meant to be **run
> yourself, separately, in a shell** -- they are documented, not executed
> by the lesson. Run the read-only ones directly from the repository
> root:
>
> ```bash
> ruff format --check lessons/14_environments_processes_and_packaging exercises/14_environments_processes_and_packaging
> ruff check lessons/14_environments_processes_and_packaging exercises/14_environments_processes_and_packaging
> ```
>
> Predict the result: `git status` reports no changes before or after --
> both commands only report status. A bare `ruff format` (no `--check`)
> is the one that would rewrite files, which is why the quality-gate
> command stays check-only.

## 5️⃣ Distributions, builds, and public APIs

A distribution name (what pip installs, e.g.
`learning-python-public-api-example-2026`) and its import package name
(what Python code imports, `packaging_public_api_example`) need not
match. `[build-system]` names the build backend a PEP 517 frontend must
use; `[project]` holds PEP 621 metadata (name, version, supported Python
versions). Importable code lives under `src/`, separate from
`pyproject.toml` -- this exposes missing packaging configuration instead
of accidentally importing an uninstalled package from the repository
root. A public API is documented at its package boundary: re-exporting
from `__init__.py` with `__all__` gives callers one stable import path,
and each public function's docstring is a contract (parameters, return
value, promised exceptions). `[project.scripts]` maps a console command
name to a `"import_package:function"` callable, declared in
`pyproject.toml`.

```python
# example_distribution/src/packaging_public_api_example/__init__.py
from ._greetings import greet

__all__ = ["greet"]
```

```toml
# example_distribution/pyproject.toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[project]
name = "learning-python-public-api-example-2026"
version = "0.1.0"
```

```text
1. Import package versus distribution package
  The distribution 'learning-python-public-api-example-2026' is installed
  by pip. It provides the import package 'packaging_public_api_example',
  used by Python code with `import`. The two names need not match.
```

Run the complete companion (prints a deterministic walkthrough; installs
nothing):

```bash
python lessons/14_environments_processes_and_packaging/05_distributions_builds_and_public_apis.py
```

See
[`05_distributions_builds_and_public_apis.py`](05_distributions_builds_and_public_apis.py)
for the full sequence, including all six numbered walkthrough sections and
the commands to install, inspect, and build the example distribution --
printed as text, **not executed** by this script.

> **Try one change (the one place this chapter leaves purely offline
> territory, and only if you choose to run it yourself):**
>
> ```bash
> python -m pip install -e lessons/14_environments_processes_and_packaging/example_distribution
> python -m pydoc packaging_public_api_example
> ```
>
> This installs only the small example package shown above, with no
> network access beyond the local editable install; `python -m pydoc`
> then reads `greet`'s docstring as its documented public contract. The
> Chapter 14 exercise's `starter_distribution/pyproject.toml` leaves a
> matching `[project.scripts]` table as a `# TODO` for you to add -- that
> file is part of the exercise, not this lesson.

## 🔁 Transition ahead

You now own the full local development loop: environments, processes,
streams, quality gates, and packaging. The remaining chapters apply these
skills to concrete domains — relational data with SQLite, HTTP servers and
clients — followed by the Task project and, finally, concurrency. Every one
of them is tested, debugged, and quality-checked with exactly the tools from
these three chapters.

## ⚠️ Common mistakes

- Installing with a bare `pip` that targets a different interpreter than the
  one running your code; use `python -m pip`.
- Printing or logging a secret's value while "validating" it.
- Writing diagnostics to stdout, so a caller parsing results sees noise.
- Building a shell command string from user input, or passing `shell=True`,
  instead of an argument list.
- Omitting a timeout or `check=True`, so a hung or failed child goes
  unnoticed.
- Catching every subprocess failure the same way instead of distinguishing
  timeout, nonzero exit, and could-not-start.
- Treating high coverage or passing formatting as proof of correctness.
- Importing code from the repository root instead of installing the
  distribution, hiding missing packaging configuration.

## 🧾 Summary

- A virtual environment isolates a project's dependencies; `python -m pip`
  installs into the intended interpreter.
- Environment variables configure a process; validate secrets without
  revealing them, and use stdout, stderr, and the exit status for their
  distinct purposes.
- Own a subprocess explicitly: interpreter, argument list, allowlisted
  environment, stdin, captured text, a finite timeout, `check=True`, and a
  specific error taxonomy.
- Formatting, linting, typing, testing, coverage, and CI each answer a
  different question and none implies the others.
- A distribution declares its build backend and metadata in `pyproject.toml`,
  uses a `src/` layout, documents its public API, and can expose a console
  command via `[project.scripts]`.

## ❓ Review questions (closed notes)

1. How can code tell whether it is running inside a virtual environment, and
   why prefer `python -m pip` over a bare `pip`?
2. How do you validate a secret from the environment without leaking it, and
   which stream should diagnostics use?
3. What does the process exit status communicate, and how do you set it?
4. List the ownership decisions you make when running a subprocess and why
   each matters.
5. What are the three distinct subprocess failure exceptions and what does
   each mean?
6. What can coverage prove, and what can it never prove on its own?
7. What is the difference between an import package and a distribution
   package, and how does `[project.scripts]` create a console command?

## 📚 Authoritative references

- [`venv` — Creation of virtual environments](https://docs.python.org/3/library/venv.html)
- [Installing packages with pip and virtual environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
- [`subprocess` — Subprocess management](https://docs.python.org/3/library/subprocess.html)
- [`os` — Miscellaneous operating system interfaces](https://docs.python.org/3/library/os.html)
- [`logging` — Logging facility for Python](https://docs.python.org/3/library/logging.html)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [Writing your `pyproject.toml` (PEP 621 metadata and `[project.scripts]`)](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

Once you can answer the review questions and have run all five lesson files,
continue to
[`exercises/14_environments_processes_and_packaging/`](../../exercises/14_environments_processes_and_packaging/README.md).
