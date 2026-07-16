"""
Lesson 9.5: Logging and Automated Quality Tools

Logging records runtime diagnostics with severity and context. External tools
then provide different kinds of repeatable feedback:

    ruff format .
    ruff check .
    ruff format --check .
    mypy
    python -m pytest ...
    coverage run -m unittest ...
    coverage report

This repository configures Ruff across the repository, strict mypy for both
typed capstone solutions, and branch coverage for both capstones.
"""

import logging

# Library modules create named loggers but do not choose handlers or global
# levels. The application configures those policy decisions at its boundary.
logger = logging.getLogger(__name__)

QUALITY_STEPS = (
    ("format", "ruff format ."),
    ("lint", "ruff check ."),
    ("type-check configured application files", "mypy"),
    (
        "run a targeted pytest lesson",
        "python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py -v",
    ),
    ("measure configured capstone coverage", "coverage run -m unittest ..."),
    ("report measured coverage", "coverage report"),
)


def calculate_total(prices: list[float]) -> float:
    """Return a total while recording useful diagnostic context."""
    # Logging's placeholder style defers string formatting until the message is
    # enabled, unlike building an f-string before calling logger.debug().
    logger.debug("Calculating total for %d prices", len(prices))
    total = sum(prices)
    logger.info("Calculated total %.2f", total)
    return total


def describe_quality_steps() -> None:
    """Print the narrow-to-wide feedback loop documented by this module."""
    print("\nA practical local feedback loop:")
    for purpose, command in QUALITY_STEPS:
        print(f"  {purpose}: {command}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
    print("Total:", calculate_total([10.0, 2.5, 7.5]))
    describe_quality_steps()
    print("\nTool configuration and scope live in pyproject.toml.")
