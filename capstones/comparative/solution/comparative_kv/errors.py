"""Typed failures and normative process metadata."""

from collections.abc import Mapping
from typing import NoReturn


class IncompleteImplementationError(NotImplementedError):
    """Compatibility marker shared with the guided starter."""


class KvError(Exception):
    """One failure from the frozen comparative contract."""

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
        """Return the exact failure envelope."""

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
    """Raise one typed contract failure."""

    raise KvError(category, details, exit_code)


def incomplete(feature: str) -> NoReturn:
    """Retain the starter-compatible incomplete boundary."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
