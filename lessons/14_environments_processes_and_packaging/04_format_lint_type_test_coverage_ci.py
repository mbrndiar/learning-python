"""
Chapter 14, Lesson 4: Format, Lint, Type-Check, Test, Coverage, and CI

Purpose: understand the automated quality gates a Python project runs and
what each one can and cannot prove, use lazy logging for runtime
diagnostics, and see how the same bounded commands run locally and in
continuous integration (`.github/workflows/course.yml`).

Prerequisites: Chapter 12 (testing) and Lessons 1-3. This lesson only
describes and prints the commands; it does not run Ruff, mypy, pytest, or
coverage for you, so it stays deterministic and offline.

Run it from the repository root:

    python lessons/14_environments_processes_and_packaging/04_format_lint_type_test_coverage_ci.py
"""

import logging

# Step 1: a library module creates a named logger and does not configure
# handlers or the global level; the application decides that once.
logger = logging.getLogger(__name__)

# Step 2: each gate answers a different question and none implies the
# others. Formatting cannot prove correctness, types cannot prove
# requirements, and high coverage cannot prove the assertions are
# meaningful.
QUALITY_GATES = (
    (
        "format check",
        "does this chapter match one consistent style?",
        "ruff format --check lessons/14_environments_processes_and_packaging "
        "exercises/14_environments_processes_and_packaging",
    ),
    (
        "lint",
        "are there likely bugs or smells in this chapter?",
        "ruff check lessons/14_environments_processes_and_packaging "
        "exercises/14_environments_processes_and_packaging",
    ),
    ("type-check", "do the type annotations hold?", "mypy"),
    (
        "test (bounded)",
        "does observed behavior match expectations?",
        "python -m pytest lessons/12_testing/"
        "03_pytest_assertions_parameterization_and_fixtures.py -v",
    ),
    (
        "coverage",
        "which configured lines did the tests execute?",
        "PROJECT_IMPLEMENTATION=solution coverage run -m pytest "
        "projects/tasks/tests -q && coverage report "
        '--include="projects/tasks/solution/**/*.py"',
    ),
)


def calculate_total(prices: list[float]) -> float:
    """Return a total while recording useful diagnostic context."""
    # Step 3: pass format arguments to the logging call rather than building
    # an f-string. logging only formats the message if the level is enabled,
    # so a disabled debug log costs almost nothing.
    logger.debug("calculating total for %d prices", len(prices))
    total = sum(prices)
    logger.info("calculated total %.2f", total)
    return total


def describe_quality_gates() -> None:
    """Print each gate, the question it answers, and its bounded command."""
    print("\nAutomated quality gates (each answers a different question):")
    for name, question, command in QUALITY_GATES:
        print(f"  {name}: {question}")
        print(f"    $ {command}")


def main() -> None:
    # Step 4: the application configures logging once, at its boundary.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
    print("Total:", calculate_total([10.0, 2.5, 7.5]))
    describe_quality_gates()
    print(
        "\nContinuous integration runs these same kinds of gates in a clean\n"
        "environment. See .github/workflows/course.yml: it validates the\n"
        "manifest, runs every lesson and solution, checks formatting/lint/types,\n"
        "and runs the pytest lesson and packaging example. Passing locally first\n"
        "means CI should find nothing new."
    )


if __name__ == "__main__":
    main()
