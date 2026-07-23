"""timekeeper_cli: a tiny console application for the packaging exercise.

The public entry point is :func:`main`. A ``[project.scripts]`` table in
``pyproject.toml`` turns this callable into an installed ``timekeeper``
command.
"""


def main() -> int:
    """Print a deterministic banner and return a success exit status."""
    print("timekeeper: ready")
    return 0
