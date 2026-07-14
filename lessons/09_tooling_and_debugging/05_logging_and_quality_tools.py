"""
Lesson 9.5: Logging and Automated Quality Tools

Logging records diagnostics with severity and context. External tools then
provide fast, repeatable feedback:

    ruff check .
    ruff format --check .
    mypy
    coverage run -m unittest ...
    coverage report

This repository configures those commands in pyproject.toml.
"""

import logging

logger = logging.getLogger(__name__)


def calculate_total(prices: list[float]) -> float:
    """Return a total while recording useful diagnostic context."""
    logger.debug("Calculating total for %d prices", len(prices))
    total = sum(prices)
    logger.info("Calculated total %.2f", total)
    return total


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
    print("Total:", calculate_total([10.0, 2.5, 7.5]))
    print("\nQuality-tool configuration lives in pyproject.toml.")
