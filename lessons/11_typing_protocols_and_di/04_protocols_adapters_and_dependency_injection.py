"""
Chapter 11, Lesson 4: Protocols, Adapters, and Dependency Injection

Purpose: use `typing.Protocol` to describe required behavior
structurally (by shape, not inheritance); inject a collaborator into an
object instead of letting it construct one internally; and write an
adapter that lets an existing, unrelated class satisfy a Protocol it was
never written against.

Prerequisites: Lessons 1-3 (annotations, generics, Literal/Self). Chapter
9's composition lesson (Car holding an Engine) is the same "give an
object its collaborator" idea, made explicit and type-checked here.

Read this file top to bottom, predict each output, then run it:

    python lessons/11_typing_protocols_and_di/04_protocols_adapters_and_dependency_injection.py
"""

from dataclasses import dataclass
from typing import Protocol


# Step 1: a Protocol describes a required shape -- any object with a
# matching `send` method satisfies MessageSender, whether or not it
# inherits from anything related to it. This is structural typing:
# compatibility is checked by shape, not by declared ancestry.
class MessageSender(Protocol):
    """Anything with this method can be used by ReminderService."""

    def send(self, recipient: str, message: str) -> None: ...


@dataclass
class ReminderService:
    """Receives its collaborator instead of constructing one internally.

    This is dependency injection: ReminderService's business logic
    (formatting a reminder) is fully decoupled from HOW the message
    actually gets delivered.
    """

    sender: MessageSender

    def remind(self, recipient: str, task: str) -> None:
        self.sender.send(recipient, f"Reminder: {task}")


# Step 2: two interchangeable implementations. Neither inherits from
# MessageSender -- each is accepted purely because it defines a matching
# send(recipient, message) method.
class ConsoleSender:
    """Satisfy MessageSender structurally, without inheriting from it."""

    def send(self, recipient: str, message: str) -> None:
        print(f"To {recipient}: {message}")


class RecordingSender:
    """A test-friendly sender that records calls instead of doing real I/O."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> None:
        self.messages.append((recipient, message))


# The same ReminderService works unchanged with either implementation --
# swapping ConsoleSender for RecordingSender changes nothing about
# ReminderService itself, exactly like Chapter 9's Car working unchanged
# with a different Engine instance.
ReminderService(ConsoleSender()).remind("Ada", "finish the typing lesson")

recording_sender = RecordingSender()
ReminderService(recording_sender).remind("Lin", "test without real I/O")
print("Recorded for a test:", recording_sender.messages)


# Step 3: an adapter. LegacyNotifier already exists, is used elsewhere,
# and cannot be changed -- but its method is called notify(), not send(),
# so it does not satisfy MessageSender as written. An adapter wraps it,
# translating one interface into the other at a single boundary.
class LegacyNotifier:
    """Pretend this older class is depended on elsewhere and cannot change."""

    def notify(self, text: str) -> None:
        print(text)


class LegacyNotifierAdapter:
    """Translate MessageSender calls into LegacyNotifier.notify() calls."""

    def __init__(self, notifier: LegacyNotifier) -> None:
        self.notifier = notifier

    def send(self, recipient: str, message: str) -> None:
        # Translation stays at this one boundary instead of leaking
        # legacy method names and formatting rules into ReminderService.
        self.notifier.notify(f"[{recipient}] {message}")


adapted_sender = LegacyNotifierAdapter(LegacyNotifier())
ReminderService(adapted_sender).remind("Grace", "review the capstone")

# Step 4: hasattr() is only a small runtime observation that a named
# attribute exists; it does not verify the method's signature or behavior.
# Protocol compatibility is primarily checked statically by a type checker.
print("\nConsoleSender has a send method:", hasattr(ConsoleSender(), "send"))
print("LegacyNotifier has a send method:", hasattr(LegacyNotifier(), "send"))

# --- One-variable experiment -------------------------------------------
# Write a third sender, e.g. a RaisingSender whose send() always raises
# RuntimeError, and pass it to ReminderService(...).remind(...). Predict:
# does anything about ReminderService itself need to change to reject or
# accept this new sender? (No -- ReminderService only ever calls
# self.sender.send(...); any object providing that method is accepted,
# which is the entire point of depending on a Protocol instead of one
# concrete class.)
