"""
Chapter 14, Lesson 1: Virtual Environments and pip

Purpose: explain why real projects isolate their dependencies, recognize
whether the current interpreter is inside a virtual environment, and know
the commands that create, activate, populate, and leave one. This lesson
inspects the running interpreter but installs nothing and touches no
network.

Prerequisites: Chapters 1-13. A virtual environment is just a directory
that holds an isolated set of installed packages for one project.

Run it from the repository root:

    python lessons/14_environments_processes_and_packaging/01_virtual_environments_and_pip.py
"""

import sys
import sysconfig


# Step 1: detect a virtual environment from the interpreter itself, not from
# an environment variable a shell happened to set. sys.prefix points at the
# active environment; sys.base_prefix points at the base installation. They
# differ exactly when a venv is active.
def in_virtual_env() -> bool:
    """Return True if the current interpreter is running inside a venv."""
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def main() -> None:
    # Step 2: sys.executable is the interpreter actually running this
    # process. Running pip as `python -m pip` guarantees you install into
    # *this* interpreter's environment rather than some other python on PATH.
    print("Python executable:", sys.executable)
    print("Python version:", sys.version.split()[0])
    print("Running inside a virtual environment?", in_virtual_env())
    # A venv isolates installed third-party packages but reuses the base
    # interpreter's standard library.
    print("Standard library location:", sysconfig.get_path("stdlib"))

    # Step 3: the commands you would type in a terminal. They are printed,
    # not executed, so this lesson stays offline and deterministic.
    print(
        "\nCommon commands you would run in a terminal (not executed here):\n"
        "  python -m venv .venv               # create an environment\n"
        "  source .venv/bin/activate          # activate it (Linux/macOS)\n"
        "  .venv\\Scripts\\Activate.ps1         # activate it (PowerShell)\n"
        "  python -m pip install -r requirements-dev.txt\n"
        "  python -m pip list                 # inspect installed packages\n"
        "  python -m pip freeze               # snapshot this environment\n"
        "  deactivate                         # leave the environment"
    )

    # Step 4: why it matters, and the difference between an intended
    # dependency list and a full resolved snapshot.
    print(
        "\nWithout isolation, installing one project's package versions can "
        "silently break another project that needs different versions.\n"
        "A maintained requirements file records what the project intends to "
        "install; `pip freeze` reports everything currently resolved in one "
        "environment, including transitive dependencies."
    )


if __name__ == "__main__":
    main()
