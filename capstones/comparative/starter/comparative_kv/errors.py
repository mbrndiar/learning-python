"""Typed error boundaries for the guided comparative starter."""

from collections.abc import Mapping
from typing import NoReturn


class IncompleteImplementationError(NotImplementedError):
    """Mark a milestone boundary that has not been implemented yet."""


class KvError(Exception):
    """TODO(m1): carry one category, details object, and exit code."""

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
        """TODO(m2): return the exact failure envelope."""

        incomplete("comparative error envelope")


def incomplete(feature: str) -> NoReturn:
    """Raise the one intentional failure used by unfinished scaffold code."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
