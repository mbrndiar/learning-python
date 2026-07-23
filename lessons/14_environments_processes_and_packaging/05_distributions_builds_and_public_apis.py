"""
Chapter 14, Lesson 5: Distributions, Builds, and Public APIs

Purpose: distinguish an import package from a distribution package,
understand the `[build-system]` and `[project]` tables in `pyproject.toml`,
explain the `src/` layout, editable installs, wheels, and sdists, and
document a public API with docstrings that act as a contract.

Prerequisites: Chapter 6 (modules and packages) and Lessons 1-4. The
accompanying example distribution lives in `example_distribution/` beside
this file. This lesson prints a deterministic walkthrough and the commands
to explore it; it installs nothing and reaches no network.

Run it from the repository root:

    python lessons/14_environments_processes_and_packaging/05_distributions_builds_and_public_apis.py
"""

EXAMPLE_ROOT = "lessons/14_environments_processes_and_packaging/example_distribution"

# Step 1: a fixed, ordered walkthrough so the output is deterministic.
WALKTHROUGH = (
    (
        "1. Import package versus distribution package",
        "The distribution 'learning-python-public-api-example-2026' is installed "
        "by pip. It provides the import package 'packaging_public_api_example', "
        "used by Python code with `import`. The two names need not match.",
    ),
    (
        "2. Build metadata in pyproject.toml",
        "[build-system] tells a PEP 517 frontend which backend and build "
        "requirements to use in an isolated build environment. [project] holds "
        "standard PEP 621 metadata such as the distribution name, version, and "
        "supported Python versions.",
    ),
    (
        "3. The src/ layout",
        "Importable code lives under src/, separate from pyproject.toml. This "
        "exposes missing packaging configuration instead of accidentally "
        "importing an uninstalled package from the repository root.",
    ),
    (
        "4. Development and release artifacts",
        "An editable install (`pip install -e`) links an environment to the "
        "working source. A wheel is a built archive intended for installation; "
        "an sdist is a source archive from which a wheel can be built.",
    ),
    (
        "5. Public API documentation",
        "Public docstrings are contracts: document behavior, parameters, return "
        "values, and promised exceptions. Inspect them with help() or, in a "
        "terminal, with python -m pydoc.",
    ),
    (
        "6. Console entry points",
        '[project.scripts] maps a command name to "import_package:function". '
        "After installation, the packaging tool creates that command and calls "
        "the declared function; the Chapter 14 exercise adds one for real.",
    ),
)


def main() -> None:
    """Print a deterministic packaging walkthrough and commands to explore."""
    print("Distributions, builds, and public APIs")
    print(f"Example distribution: {EXAMPLE_ROOT}")

    for heading, explanation in WALKTHROUGH:
        print(f"\n{heading}\n  {explanation}")

    # Step 7: the commands to try in an isolated virtual environment. They
    # are printed, not executed, so this lesson performs no installs.
    print(
        "\nTry in an isolated virtual environment (not executed here):\n"
        f"  python -m pip install -e {EXAMPLE_ROOT}\n"
        '  python -c "import packaging_public_api_example as api; help(api.greet)"\n'
        "  python -m pydoc packaging_public_api_example\n"
        f"  python -m build {EXAMPLE_ROOT}\n"
        "The wheel and sdist appear under dist/ and are generated artifacts, "
        "ignored by Git; pyproject.toml plus src/ are the source of truth."
    )


if __name__ == "__main__":
    main()
