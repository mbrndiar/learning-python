"""
Lesson 9.1: Virtual Environments and pip

Real Python projects use packages that are not part of the standard
library. `pip` is Python's package installer, and virtual environments
keep each project's packages isolated from each other and from the
system Python installation. This lesson does not install anything -
it only explains and inspects the tools using code you can run safely.
"""

import sys
import sysconfig


def in_virtual_env():
    """Return True if the current interpreter is running inside a venv.

    `sys.prefix` differs from `sys.base_prefix` when a virtual environment
    is active, because the venv points back at the base installation.
    """
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


if __name__ == "__main__":
    print("Python executable:", sys.executable)
    print("Python version:", sys.version.split()[0])
    print("Running inside a virtual environment?", in_virtual_env())
    print("Standard library location:", sysconfig.get_path("stdlib"))

    print(
        "\nCommon commands you would run in a terminal (not executed here):\n"
        "  python3 -m venv .venv             # create an environment\n"
        "  source .venv/bin/activate         # activate it (Linux/macOS)\n"
        "  .venv\\Scripts\\Activate.ps1        # activate it (PowerShell)\n"
        "  python -m pip install -r requirements-dev.txt\n"
        "  python -m pip list               # inspect installed packages\n"
        "  python -m pip freeze             # snapshot this environment\n"
        "  deactivate                       # leave the environment"
    )

    print(
        "\nWhy bother? Without a virtual environment, installing package "
        "versions for one project can silently break another project that "
        "needs a different version of the same package."
    )
    print(
        "\nA maintained dependency file records what the project intends to "
        "install. `pip freeze` instead reports everything currently resolved "
        "in one environment, including transitive dependencies."
    )
