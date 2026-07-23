"""
Greeting functions for example_package.

This module is the package's public API. It reaches a sibling module inside
the same package with a relative import (a leading dot means "this
package"). Without the dot, Python would search sys.path for a top-level
module literally named ``_formatting``, which may not exist or may resolve
to the wrong thing.
"""

from ._formatting import _shout, _titlecase

__all__ = ["hello", "shout_hello"]


def hello(name: str) -> str:
    """Return a polite greeting."""
    return f"Hello, {_titlecase(name)}!"


def shout_hello(name: str) -> str:
    """Return an enthusiastic greeting."""
    return _shout(f"hello, {name}")
