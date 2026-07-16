"""Stable application errors and process exit categories."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from .models import ImportResult


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


class PartialImportError(ApplicationError):
    """Report a committed partial import while preserving a non-zero exit."""

    def __init__(self, result: "ImportResult"):
        self.result = result
        super().__init__(
            "partial_import",
            "one or more HTTP pages could not be imported",
            4,
            {"failed_pages": list(result.failed_pages)},
        )


class IncompleteImplementationError(NotImplementedError):
    """Retained so starter and solution expose the same public imports."""


def incomplete(feature: str) -> NoReturn:
    """Raise the intentional failure used only by unfinished starter code."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
