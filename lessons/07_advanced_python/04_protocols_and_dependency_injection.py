"""
Lesson 7.4: Protocols, Dependency Injection and Adapters

A Protocol describes required behavior without requiring inheritance.
Dependency injection gives an object its collaborator instead of constructing
one internally. An adapter makes an existing interface satisfy a new protocol.
"""

from dataclasses import dataclass
from typing import Protocol


class MessageSender(Protocol):
    """Anything with this method can be used by ReminderService."""

    def send(self, recipient: str, message: str) -> None: ...


@dataclass
class ReminderService:
    sender: MessageSender

    def remind(self, recipient: str, task: str) -> None:
        self.sender.send(recipient, f"Reminder: {task}")


class ConsoleSender:
    """Satisfy MessageSender structurally, without inheriting from it."""

    def send(self, recipient: str, message: str) -> None:
        print(f"To {recipient}: {message}")


class LegacyNotifier:
    """Pretend this older class cannot be changed."""

    def notify(self, text: str) -> None:
        print(text)


class LegacyNotifierAdapter:
    """Translate MessageSender calls to LegacyNotifier.notify()."""

    def __init__(self, notifier: LegacyNotifier) -> None:
        self.notifier = notifier

    def send(self, recipient: str, message: str) -> None:
        self.notifier.notify(f"[{recipient}] {message}")


class RecordingSender:
    """A test-friendly sender that records calls instead of doing real I/O."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> None:
        self.messages.append((recipient, message))


if __name__ == "__main__":
    ReminderService(ConsoleSender()).remind("Ada", "finish the type-hint lesson")

    adapted_sender = LegacyNotifierAdapter(LegacyNotifier())
    ReminderService(adapted_sender).remind("Grace", "review the capstone")

    recording_sender = RecordingSender()
    ReminderService(recording_sender).remind("Lin", "test without real I/O")
    print("Recorded for a test:", recording_sender.messages)
