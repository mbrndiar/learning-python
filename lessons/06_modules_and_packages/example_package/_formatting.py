"""
Internal formatting helpers for example_package.

A leading underscore is a naming convention meaning "internal implementation
detail -- not part of the public API". Python does not enforce this; the name
can still be imported explicitly. It signals intent to readers and tools.
"""


def _shout(text: str) -> str:
    """Return text in upper-case followed by an exclamation mark."""
    return text.upper() + "!"


def _titlecase(text: str) -> str:
    """Return text with every word capitalized."""
    return text.title()
