"""Public greeting functions for the exercise package."""

from ._formatting import _shout, _titlecase

__all__ = ["hello", "shout_hello"]


def hello(name: str) -> str:
    return f"Hello, {_titlecase(name)}!"


def shout_hello(name: str) -> str:
    return _shout(f"hello, {name}")
