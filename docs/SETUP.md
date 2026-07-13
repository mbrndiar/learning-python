# Setting Up Your Environment

Before starting the lessons, get Python installed and a project workspace
ready. This only needs to be done once.

## 1. Install Python

1. Download Python 3.9 or newer from https://www.python.org/downloads/
   (on Linux, use your package manager, e.g. `sudo apt install python3`).
2. Verify the installation:

   ```bash
   python3 --version
   ```

   On Windows the command is usually `python --version`.

## 2. Get the code

Clone this repository (or download it as a ZIP) and open a terminal in the
project's root directory:

```bash
git clone https://github.com/mbrndiar/learning-python.git
cd learning-python
```

## 3. Create a virtual environment

A virtual environment keeps this project's Python packages isolated from
the rest of your system. The lessons themselves have no external
dependencies, but a virtual environment is still good practice and is
required for the optional `pytest` lesson.

```bash
# Create the environment (creates a .venv/ folder)
python3 -m venv .venv

# Activate it
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows (Command Prompt / PowerShell)
```

Once activated, your shell prompt is usually prefixed with `(.venv)`. To
leave the virtual environment, run `deactivate`.

## 4. Install optional tools

Everything in `lessons/` runs with the standard library alone. A few
lessons (`lessons/09_tooling_and_debugging/04_pytest_basics.py`) and the
exercises/tests use `pytest`, which is an optional but recommended
addition:

```bash
pip install -r requirements-dev.txt
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
