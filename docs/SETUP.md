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
the rest of your system. The lessons themselves have no runtime dependencies, but a virtual environment
is still good practice and keeps the optional development tools isolated.

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

## 4. Install optional tools

Everything in `lessons/` runs with the standard library alone. The development
requirements add `pytest`, Ruff, mypy and coverage so you can practice testing,
formatting, linting, static type checking and coverage measurement:

```bash
pip install -r requirements-dev.txt
```

The more reliable interpreter-specific form is:

```bash
python -m pip install -r requirements-dev.txt
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
[course outline in the README](../README.md#course-outline).

## Optional modern setup with uv

The `venv` and `pip` workflow above is built into Python, widely available, and
worth understanding. [uv](https://docs.astral.sh/uv/) is a popular
third-party alternative that can install Python versions, create environments,
and install packages through one fast command-line tool.

After installing uv by following its official instructions, run from the
repository root:

```bash
uv python install 3.14
uv venv --python 3.14
uv pip install -r requirements-dev.txt
uv run python lessons/01_basics/01_hello_world.py
uv run python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
uv run ruff check .
uv run mypy
```

The explicit `uv venv` and `uv pip` commands mirror the course's existing
workflow; they do not require converting this repository into a packaged
project. uv also supports project metadata and lock files, which become useful
when an application has runtime dependencies and needs reproducible installs.

## Optional Python version managers

[mise](https://mise.jdx.dev/) and [asdf](https://asdf-vm.com/) can select
versions of Python and other development tools per project. They complement
`venv`/`pip` or uv rather than replacing dependency isolation:

- use mise or asdf when one tool should manage versions for several languages;
- use uv when you want a Python-focused installer and environment workflow;
- use the built-in approach when minimizing prerequisites matters most.

Beginners only need one approach. Start with the standard-library instructions
above; adopt an alternative after you understand which responsibility each
tool handles.

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

### Leaving or recreating an environment

Run `deactivate` to leave it. A virtual environment contains generated files,
so it is safe to delete `.venv` and recreate it from
`requirements-dev.txt`; do not commit `.venv` to version control.
