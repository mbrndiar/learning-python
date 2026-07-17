"""Carry stable error categories separately from Python exception mechanics.

Categories and detail objects are the machine-readable contract; exit codes
classify the process outcome.  Keeping both on one exception lets deep domain
and storage code fail without printing or depending on the CLI.
"""

from collections.abc import Mapping
from typing import NoReturn


class IncompleteImplementationError(NotImplementedError):
    """Compatibility marker shared with the guided starter."""


class KvError(Exception):
    """One categorized failure with its public details and process exit code."""

    def __init__(
        self,
        category: str,
        details: Mapping[str, object],
        exit_code: int,
    ):
        super().__init__(category)
        self.category = category
        self.details = dict(details)
        self.exit_code = exit_code

    def envelope(self) -> dict[str, object]:
        """Return the exact JSON-ready failure envelope, without exception text."""

        return {
            "ok": False,
            "error": {
                "category": self.category,
                "details": self.details,
            },
        }


def fail(
    category: str,
    details: Mapping[str, object],
    exit_code: int,
) -> NoReturn:
    """Raise a categorized contract failure from validation or persistence code."""

    raise KvError(category, details, exit_code)


def incomplete(feature: str) -> NoReturn:
    """Retain the starter-compatible incomplete boundary."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
