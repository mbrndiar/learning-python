"""
Chapter 13, Lesson 4: Logging and Diagnostics

Purpose: emit runtime diagnostics with the `logging` module instead of
scattered `print()` calls, understand severity levels and the
library-versus-application split, use lazy `%`-style message formatting,
and choose deliberately among `print()`, `pdb`, and `logging`.

Prerequisites: Lessons 1-3. Quality tools (Ruff, mypy, coverage) and CI
are covered in Chapter 14; this lesson is only about diagnostics.

Run it from the repository root:

    python lessons/13_debugging_and_cli/04_logging_and_diagnostics.py
"""

import logging

# Step 1: a library module creates a named logger and does NOT configure
# handlers or the global level. Naming it after the module (__name__) lets
# the application control level, format, and destination from one place.
logger = logging.getLogger(__name__)


def calculate_total(prices: list[float]) -> float:
    """Return a total while recording useful diagnostic context."""
    # Step 2: pass the format arguments to the logging call rather than
    # building an f-string. logging only formats the message if the level
    # is enabled, so disabled debug logs cost almost nothing.
    logger.debug("calculating total for %d prices", len(prices))
    total = sum(prices)
    logger.info("calculated total %.2f", total)
    return total


def authenticate(user: str, token: str) -> bool:
    """Demonstrate logging identifiers but never secrets."""
    # Step 3: log identifiers and context, never passwords or tokens. The
    # token value is deliberately absent from the log message.
    logger.info("authenticating user %s", user)
    authorized = bool(token)
    if not authorized:
        logger.warning("missing token for user %s", user)
    return authorized


def main() -> None:
    # Step 4: the APPLICATION configures logging once, at its boundary.
    # basicConfig sets the level, format, and (by default) sends records
    # to stderr. Libraries never call this for you.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )

    print("Total:", calculate_total([10.0, 2.5, 7.5]))
    print("Authorized:", authenticate("ada", token="s3cret"))
    print("Authorized:", authenticate("grace", token=""))

    print(
        "\nChoosing a diagnostic tool:\n"
        "  - print(): a quick, temporary peek at one local value;\n"
        "  - pdb: pause and inspect control flow interactively (Lesson 1);\n"
        "  - logging: diagnostics that should stay in reusable or deployed\n"
        "    code, with a severity level the application can filter."
    )


if __name__ == "__main__":
    main()
