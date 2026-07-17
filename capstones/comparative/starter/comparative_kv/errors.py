"""Structured error boundaries shared by domain, CLI, and storage milestones."""

from collections.abc import Mapping
from typing import NoReturn


class IncompleteImplementationError(NotImplementedError):
    """Mark a milestone boundary that has not been implemented yet."""


class KvError(Exception):
    """Carry only the contract category, details object, and process exit code.

    Keep provider messages, paths, tracebacks, and platform error numbers out of
    normative responses.  Exact category/detail combinations are exhaustive in
    SPEC section 6 and are asserted semantically by the shared fixtures.
    """

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
        """Return exactly ``{"ok": false, "error": ...}`` for this error.

        The nested error has only ``category`` and ``details``; no prose or
        convenience fields are part of the public contract.
        """

        incomplete("comparative error envelope")


def incomplete(feature: str) -> NoReturn:
    """Raise the one intentional failure used by unfinished scaffold code."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
