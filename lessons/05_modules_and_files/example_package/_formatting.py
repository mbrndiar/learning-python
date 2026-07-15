"""
Internal formatting helpers for example_package.

Names that begin with a single underscore are a convention that signals
"internal implementation detail—not part of the public API".  They can still
be imported explicitly, but callers are not expected to rely on them.
"""


def _shout(text: str) -> str:
    """Return text in upper-case followed by an exclamation mark."""
    return text.upper() + "!"


def _titlecase(text: str) -> str:
    """Return text with every word capitalised."""
    return text.title()
