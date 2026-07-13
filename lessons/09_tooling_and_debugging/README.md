# Module 9: Tooling and Debugging

The everyday tools that make writing, running and fixing Python code
easier - beyond the language itself.

## Concepts covered

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

## Running

```bash
python lessons/09_tooling_and_debugging/01_virtual_environments_and_pip.py
python lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py
python lessons/09_tooling_and_debugging/03_command_line_arguments.py
pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
```

Once you've read through all four files, practice what you learned in
[`exercises/09_tooling_and_debugging/`](../../exercises/09_tooling_and_debugging/README.md).
