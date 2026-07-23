"""
Solutions: Chapter 11 - Typing, Protocols, and Dependency Injection

Reference solutions for exercises/11_typing_protocols_and_di/exercises.py.

Run this file directly:

    python exercises/11_typing_protocols_and_di/solutions.py
"""

from dataclasses import dataclass, field
from typing import Annotated, Literal, Protocol, Self, TypeVar


def describe_optional_name(name: str | None) -> str:
    if name is None:
        return "(none)"
    return name.upper()


T = TypeVar("T")


def last(items: list[T]) -> T:
    return items[-1]


AccessMode = Literal["read", "write"]
PositiveCount = Annotated[int, "must be positive"]


def access_label(mode: AccessMode) -> str:
    if mode == "read":
        return "read-only"
    return "writable"


def repeat_label(label: str, count: PositiveCount) -> str:
    if count <= 0:
        raise ValueError("count must be positive")
    return " ".join([label] * count)


@dataclass
class Query:
    clauses: list[str] = field(default_factory=list)

    def where(self, clause: str) -> Self:
        self.clauses.append(clause)
        return self


class Notifier(Protocol):
    def notify(self, message: str) -> None: ...


@dataclass
class AlertService:
    notifier: Notifier

    def alert(self, message: str) -> None:
        self.notifier.notify(f"ALERT: {message}")


class RecordingNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str) -> None:
        self.messages.append(message)


class UppercaseNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str) -> None:
        self.messages.append(message.upper())


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
