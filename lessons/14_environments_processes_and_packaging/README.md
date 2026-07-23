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

## 🧩 Progressive syntax and mechanism

1. **Virtual environments.** `sys.prefix != sys.base_prefix` when a venv is
   active. Create with `python -m venv .venv`, activate, then
   `python -m pip install -r requirements-dev.txt`. Running pip as
   `python -m pip` targets *this* interpreter.
2. **Environment configuration.** Read with `os.environ.get(name)`. Validate
   a secret without returning or printing its value; error messages name the
   variable and rule, never the value. The runnable demo uses a fixed mapping
   so ambient configuration cannot change its output; `run_from_process()`
   shows where a real application supplies `os.environ`.
3. **Standard streams and exit status.** `print(...)` writes to stdout;
   `print(..., file=sys.stderr)` writes diagnostics; `return`ing an int from
   a `main()` that you pass to `raise SystemExit(main())` sets the process
   exit status, where `0` means success.
4. **Subprocess ownership.** `subprocess.run([sys.executable, "-c", code,
   message], env=..., stdin=subprocess.DEVNULL, capture_output=True,
   text=True, timeout=5, check=True)`. The argument list keeps `message` a
   single value; there is no shell to reinterpret it.
5. **Error taxonomy.** `subprocess.TimeoutExpired` (took too long),
   `subprocess.CalledProcessError` (ran but exited nonzero), and `OSError`
   (could not start) are distinct; handle each specifically.
6. **Quality gates.** `ruff format`/`ruff check`, `mypy`, `python -m pytest
   <bounded target>`, and `coverage run ... && coverage report`. None
   implies the others; CI runs the same kinds of gates, often over the full
   repository, in a clean environment.
7. **Packaging.** `[build-system]` names the build backend; `[project]`
   holds PEP 621 metadata; a `src/` layout keeps importable code separate.
   `[project.scripts]` maps a console command to a `"module:function"`
   callable. An editable install is for development; a wheel and sdist are
   built artifacts.

## 📖 Read-predict-run-modify workflow

Read each file top to bottom, predict its output, then run it:

```bash
python lessons/14_environments_processes_and_packaging/01_virtual_environments_and_pip.py
python lessons/14_environments_processes_and_packaging/02_environment_streams_and_exit_status.py
python lessons/14_environments_processes_and_packaging/03_subprocess_ownership.py
python lessons/14_environments_processes_and_packaging/04_format_lint_type_test_coverage_ci.py
python lessons/14_environments_processes_and_packaging/05_distributions_builds_and_public_apis.py
```

### Expected output highlights

- `01_...pip.py`: prints this interpreter's path and version, whether a venv
  is active, and the commands to create and use one (printed, not run).
- `02_...exit_status.py`: reports whether a token variable is configured
  (never its value), sends a line to stderr, and returns exit status 0.
- `03_subprocess_ownership.py`: runs one short child that echoes
  `result from child`, then lists the ownership decisions it made.
- `04_...ci.py`: prints DEBUG/INFO log records for a total, then the quality
  gates with the question each answers and its bounded command.
- `05_...public_apis.py`: prints an ordered packaging walkthrough and the
  commands to install, document, and build the example distribution.

Then modify something and predict the new result: change the child message
in Lesson 3 and confirm the echoed stdout changes; lower a `logger.debug`
call below the configured level in Lesson 4 and confirm it disappears.

### Try the packaging boundary yourself

The example distribution beside these lessons is safe to install into a
throwaway virtual environment:

```bash
python -m pip install -e lessons/14_environments_processes_and_packaging/example_distribution
python -m pydoc packaging_public_api_example
```

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
