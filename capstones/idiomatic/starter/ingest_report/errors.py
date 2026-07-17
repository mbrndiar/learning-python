"""Stable application errors and intentional starter placeholders.

Milestone guidance: callers classify failures by semantic code and exit
category, not message text.  Keep user input, source content, source I/O or
partial completion, database failures, and cancellation distinguishable at the
CLI boundary.  A partial-import error also needs to carry the committed result
for stdout while reporting failure on stderr; do not turn it into success.
"""

from collections.abc import Mapping
from typing import NoReturn


class ApplicationError(Exception):
    """An expected failure safe to render without a traceback.

    Preserve the structured details for ``--json-errors`` and let the boundary
    decide text versus JSON rendering.  Stable English messages support people;
    stable codes and exit categories support automation.
    """

    def __init__(
        self,
        code: str,
        message: str,
        exit_code: int,
        details: Mapping[str, object] | None = None,
    ):
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.details = dict(details or {})
        super().__init__(message)

    def envelope(self) -> dict[str, object]:
        """Return the documented machine-readable error envelope."""

        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class IncompleteImplementationError(NotImplementedError):
    """Mark a milestone boundary that has not been implemented yet.

    This is the intentional starter failure.  Replace calls milestone by
    milestone, but do not classify this placeholder as an expected user error.
    """


def incomplete(feature: str) -> NoReturn:
    """Raise the one intentional failure used by unfinished scaffold code."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
