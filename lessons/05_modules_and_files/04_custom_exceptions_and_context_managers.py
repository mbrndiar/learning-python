"""
Lesson 5.4: Custom Exceptions and Context Managers

This lesson goes beyond basic try/except to cover defining your own
exception types and writing your own context managers (the objects
that power the `with` statement).
"""

from contextlib import contextmanager
from pathlib import Path


# --- Custom exceptions -----------------------------------------------------
class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""

    def __init__(self, balance, amount):
        # Structured attributes let a handler inspect the failure without
        # parsing the human-readable message.
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw {amount}: balance is only {balance}")


def withdraw(balance, amount):
    """Raise a custom exception instead of a generic one when funds are low."""
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount


# --- Custom context manager (class-based) -----------------------------------
class ManagedFile:
    """A minimal re-implementation of `open()` as a context manager.

    Implementing `__enter__` and `__exit__` lets an object work with the
    `with` statement, guaranteeing cleanup even if an error occurs.
    """

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.path, self.mode, encoding="utf-8")
        # The value returned here is what `as file` receives in the with block.
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        # Python calls __exit__ on normal completion and when the body raises,
        # so cleanup belongs here rather than after the with statement.
        if self.file:
            self.file.close()
        # A truthy return would suppress the active exception. False (or None)
        # preserves it after cleanup, which is the safer default.
        return False


# --- Custom context manager (function-based, using @contextmanager) --------
@contextmanager
def timer_message(label):
    """Print a start/end message around a block of code."""
    print(f"Starting: {label}")
    try:
        # Code before yield acts like __enter__; the single yielded value would
        # be bound by `as`. Code after yield acts like __exit__.
        yield
    finally:
        # finally preserves cleanup even when the managed block raises.
        print(f"Finished: {label}")


if __name__ == "__main__":
    try:
        withdraw(100, 500)
    except InsufficientFundsError as error:
        print("Caught custom error:", error)
        print("  balance was:", error.balance, "| requested:", error.amount)

    file_path = Path(__file__).with_name("managed_sample.txt")

    with ManagedFile(file_path, "w") as file:
        file.write("Written using a custom context manager.\n")

    with ManagedFile(file_path, "r") as file:
        print("\nFile contents:", file.read().strip())

    file_path.unlink()

    print()
    with timer_message("processing data"):
        total = sum(range(1000))
        print("  total:", total)
