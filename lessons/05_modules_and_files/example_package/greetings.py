"""
Greeting functions for example_package.

This module contains the public API of the package.  It uses a relative
import (``from ._formatting import ...``) to reach a sibling module inside
the same package.  The leading dot means "this package"; without it Python
would search sys.path for a top-level module named ``_formatting``.
"""

from ._formatting import _shout, _titlecase

__all__ = ["hello", "shout_hello"]


def hello(name: str) -> str:
    """Return a polite greeting."""
    return f"Hello, {_titlecase(name)}!"


def shout_hello(name: str) -> str:
    """Return an enthusiastic greeting."""
    return _shout(f"hello, {name}")
