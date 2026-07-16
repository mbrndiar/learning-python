"""Errors used by the idiomatic capstone scaffold."""

from typing import NoReturn


class IncompleteImplementationError(NotImplementedError):
    """Mark a milestone boundary that has not been implemented yet."""


def incomplete(feature: str) -> NoReturn:
    """Raise the one intentional failure used by unfinished scaffold code."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the next milestone"
    )
