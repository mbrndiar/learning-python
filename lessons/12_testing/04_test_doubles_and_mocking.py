"""
Chapter 12, Lesson 4: Test Doubles and Mocking

Purpose: distinguish the kinds of test double (fake, stub, mock),
constrain a mock to a real interface with `Mock(spec=...)` so a
misspelled method fails loudly, and replace a dependency exactly where the
code under test looks it up using `unittest.mock.patch`.

Prerequisites: Lessons 1-3, and Chapter 11's dependency injection. A test
double stands in for a real collaborator so a test stays fast,
deterministic, and free of real I/O.

Run this file directly; it exercises each double and prints what it
verified:

    python lessons/12_testing/04_test_doubles_and_mocking.py
"""

from typing import Protocol
from unittest.mock import Mock, call, patch


# Step 1: the real collaborator. In production this would send email over
# the network. A test must never call the real one, so we substitute a
# double for it.
class EmailGateway:
    """Sends real email. Tests replace this with a double."""

    def send(self, to: str, subject: str, body: str) -> str:  # pragma: no cover
        raise RuntimeError("the real gateway must not run inside tests")


class EmailSender(Protocol):
    """The collaborator shape notify_signup actually needs."""

    def send(self, to: str, subject: str, body: str) -> str: ...


# Step 2: the code under test depends on *some* gateway with a send()
# method (dependency injection from Chapter 11). It does not care which.
def notify_signup(gateway: EmailSender, address: str) -> str:
    """Send one welcome message and return the gateway's receipt id."""
    return gateway.send(
        to=address,
        subject="Welcome",
        body="Thanks for signing up.",
    )


# Step 3: a FAKE is a working, lightweight implementation. It behaves like
# the real thing (you can send and later inspect what was sent) but keeps
# everything in memory. Fakes are ideal when the test needs realistic
# behavior, not just recorded calls.
class FakeEmailGateway:
    """A working in-memory substitute for EmailGateway."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> str:
        self.sent.append((to, subject, body))
        return f"fake-{len(self.sent)}"


# Step 4: a STUB returns canned answers to feed a specific path, without
# recording or verifying anything. Here it always reports the same receipt
# so the test can assert on the return value of notify_signup.
class StubEmailGateway:
    """Returns a fixed response; records nothing."""

    def send(self, to: str, subject: str, body: str) -> str:
        return "stub-receipt"


def demonstrate_fake_and_stub() -> None:
    fake = FakeEmailGateway()
    receipt = notify_signup(fake, "ada@example.com")
    # A fake lets you assert on realistic recorded state.
    assert fake.sent == [("ada@example.com", "Welcome", "Thanks for signing up.")]
    assert receipt == "fake-1"

    stub = StubEmailGateway()
    # A stub only feeds a canned answer down the path under test.
    assert notify_signup(stub, "grace@example.com") == "stub-receipt"
    print("fake recorded one message; stub returned its canned receipt")


# Step 5: a MOCK records interactions so the test can assert *how* the
# collaborator was called. Mock(spec=EmailGateway) constrains the mock to
# the real interface: accessing a method the real class does not have
# raises AttributeError, catching a typo that an unconstrained Mock would
# happily accept.
def demonstrate_mock_with_spec() -> None:
    gateway = Mock(spec=EmailGateway)
    gateway.send.return_value = "receipt-42"

    receipt = notify_signup(gateway, "lin@example.com")

    assert receipt == "receipt-42"
    # Verify the exact interaction at the boundary.
    gateway.send.assert_called_once_with(
        to="lin@example.com",
        subject="Welcome",
        body="Thanks for signing up.",
    )
    assert gateway.send.call_args_list == [
        call(to="lin@example.com", subject="Welcome", body="Thanks for signing up.")
    ]

    # The spec rejects methods the real EmailGateway does not define.
    try:
        gateway.deliver("oops")  # not a real EmailGateway method
    except AttributeError:
        print("Mock(spec=...) rejected a method the real class does not have")
    else:  # pragma: no cover - only runs if spec enforcement breaks
        raise AssertionError("spec should have rejected gateway.deliver")


# Step 6: patch where the name is *looked up*, not where it is defined.
# build_banner() calls read_setting() by its name in THIS module, so the
# patch target is this module's attribute. Patching the definition's
# original home would not affect this lookup. Using patch() as a context
# manager also guarantees the original is restored, avoiding fragile
# global replacement that leaks into later tests.
def read_setting(name: str) -> str:
    """Pretend to read configuration from disk or the environment."""
    raise RuntimeError("real configuration lookup must not run inside tests")


def build_banner() -> str:
    return f"== {read_setting('title')} =="


def demonstrate_patch_where_looked_up() -> None:
    with patch(
        f"{__name__}.read_setting", return_value="Release Notes"
    ) as fake_setting:
        assert build_banner() == "== Release Notes =="
        fake_setting.assert_called_once_with("title")
    # Outside the with-block the real read_setting is restored automatically.
    assert read_setting.__doc__ is not None
    print("patched read_setting only within the with-block, then restored it")


def main() -> None:
    demonstrate_fake_and_stub()
    demonstrate_mock_with_spec()
    demonstrate_patch_where_looked_up()
    print(
        "\nChoosing a double:\n"
        "  - fake: need realistic behavior and recorded state;\n"
        "  - stub: only need a canned answer to reach a code path;\n"
        "  - mock: need to verify how a collaborator was called;\n"
        "  - spec: constrain a mock to the real interface;\n"
        "  - patch: replace a name where the code under test looks it up."
    )


if __name__ == "__main__":
    main()
