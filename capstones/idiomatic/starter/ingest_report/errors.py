"""Stable application errors and intentional starter placeholders."""

from collections.abc import Mapping
from typing import NoReturn


class ApplicationError(Exception):
    """An expected failure safe to render without a traceback."""

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
    """Mark a milestone boundary that has not been implemented yet."""


def incomplete(feature: str) -> NoReturn:
    """Raise the one intentional failure used by unfinished scaffold code."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
