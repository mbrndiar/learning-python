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
        "  python -m venv .venv          # create a virtual environment\n"
        "  source .venv/bin/activate     # activate it (Linux/macOS)\n"
        "  .venv\\Scripts\\activate         # activate it (Windows)\n"
        "  pip install <package>         # install a package into the venv\n"
        "  pip freeze > requirements.txt # record installed packages\n"
        "  pip install -r requirements.txt  # install from that file\n"
        "  deactivate                    # leave the virtual environment"
    )

    print(
        "\nWhy bother? Without a virtual environment, installing package "
        "versions for one project can silently break another project that "
        "needs a different version of the same package."
    )
