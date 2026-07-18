"""
Lesson 9.7: Packaging and Public API Documentation

Python uses "package" for two related ideas: an import package is code loaded
with ``import``, while a distribution package is the installable project built
and installed by packaging tools. Run this lesson from the repository root:

    python lessons/09_tooling_and_debugging/07_packaging_and_public_apis.py
"""

EXAMPLE_ROOT = "lessons/09_tooling_and_debugging/example_distribution"

WALKTHROUGH = (
    (
        "1. Import package versus distribution package",
        "The distribution 'learning-python-public-api-example-2026' is installed "
        "by pip. It provides the import package 'packaging_public_api_example', "
        "used by Python code. These names need not match.",
    ),
    (
        "2. Build metadata",
        "[build-system] tells a PEP 517 frontend which backend and build "
        "requirements to use in an isolated build environment. [project] holds "
        "standard metadata such as the distribution name, version, and supported "
        "Python versions.",
    ),
    (
        "3. src layout",
        "Importable code lives under src/, separate from pyproject.toml. This "
        "helps expose missing packaging configuration instead of accidentally "
        "importing an uninstalled package from the repository root.",
    ),
    (
        "4. Development and release artifacts",
        "An editable install links an environment to the working source. A wheel "
        "is a built archive intended for installation; an sdist is a source "
        "archive from which a wheel can be built.",
    ),
    (
        "5. Public documentation",
        "Public docstrings are contracts: document behavior, parameters, return "
        "values, and promised exceptions. Inspect them interactively with help() "
        "or in a terminal with python -m pydoc.",
    ),
)


def main() -> None:
    """Print a deterministic packaging walkthrough and commands to explore."""
    print("Packaging and public APIs")
    print(f"Example distribution: {EXAMPLE_ROOT}")

    for heading, explanation in WALKTHROUGH:
        print(f"\n{heading}\n  {explanation}")

    print(
        "\nTry in an isolated virtual environment:\n"
        f"  python -m pip install -e {EXAMPLE_ROOT}\n"
        '  python -c "import packaging_public_api_example as api; '
        'help(api.greet)"\n'
        "  python -m pydoc packaging_public_api_example\n"
        f"  python -m build {EXAMPLE_ROOT}"
    )


if __name__ == "__main__":
    main()
