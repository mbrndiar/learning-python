"""
Exercises: Chapter 11 - Typing, Protocols, and Dependency Injection

Implement each function/class below, then run this file directly to
check your work.

    python exercises/11_typing_protocols_and_di/exercises.py

Each starter raises NotImplementedError until you implement it.
"""

from dataclasses import dataclass, field
from typing import Annotated, Literal, Protocol, Self, TypeVar


def describe_optional_name(name: str | None) -> str:
    """Return "(none)" when `name` is None, otherwise `name` upper-cased.

    Narrow the union with an `is None` (or `is not None`) check before
    calling any str-only method.
    """
    # TODO: implement this function
    raise NotImplementedError


T = TypeVar("T")


def last(items: list[T]) -> T:
    """Return the last element of a non-empty list, generic over its type."""
    # TODO: implement this function
    raise NotImplementedError


AccessMode = Literal["read", "write"]
PositiveCount = Annotated[int, "must be positive"]


def access_label(mode: AccessMode) -> str:
    """Return "read-only" or "writable" for the corresponding finite mode."""
    raise NotImplementedError("TODO: handle both Literal values")


def repeat_label(label: str, count: PositiveCount) -> str:
    """Join `count` copies of label; validate the Annotated constraint."""
    raise NotImplementedError("TODO: reject non-positive count, then join labels")


@dataclass
class Query:
    clauses: list[str] = field(default_factory=list)

    def where(self, clause: str) -> Self:
        """Append one clause and return this same instance for chaining."""
        raise NotImplementedError("TODO: append clause and return self")


class Notifier(Protocol):
    """Anything with this method can be used by AlertService."""

    def notify(self, message: str) -> None: ...


@dataclass
class AlertService:
    """Depends on a Notifier instead of constructing one internally."""

    notifier: Notifier

    def alert(self, message: str) -> None:
        # TODO: delegate to self.notifier.notify(...) with the message
        # prefixed by "ALERT: "
        raise NotImplementedError


class RecordingNotifier:
    """A test-friendly Notifier that records messages instead of doing I/O."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str) -> None:
        # TODO: append message to self.messages
        raise NotImplementedError


class UppercaseNotifier:
    """A second, differently-behaved Notifier implementation."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str) -> None:
        # TODO: append message.upper() to self.messages
        raise NotImplementedError


assert describe_optional_name(None) == "(none)"
assert describe_optional_name("ada") == "ADA"
print("describe_optional_name: OK")

assert last([1, 2, 3]) == 3
assert last(["a", "b"]) == "b"
print("last: OK")

assert access_label("read") == "read-only"
assert access_label("write") == "writable"
assert repeat_label("go", 3) == "go go go"
try:
    repeat_label("go", 0)
except ValueError:
    pass
else:
    raise AssertionError("Annotated metadata needs an explicit runtime check")
print("Literal and Annotated contracts: OK")

query = Query()
assert query.where("active = true") is query
assert query.where("owner = 'Ada'") is query
assert query.clauses == ["active = true", "owner = 'Ada'"]
print("Self-returning Query: OK")

recording = RecordingNotifier()
AlertService(recording).alert("disk full")
assert recording.messages == ["ALERT: disk full"]

uppercase = UppercaseNotifier()
AlertService(uppercase).alert("disk full")
assert uppercase.messages == ["ALERT: DISK FULL"]
print("AlertService with two interchangeable Notifiers: OK")

print("\nAll checks passed!")
