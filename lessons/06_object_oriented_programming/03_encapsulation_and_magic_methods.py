"""
Lesson 6.3: Encapsulation and Magic Methods

Encapsulation means controlling access to an object's internal state.
Magic methods (also called "dunder" methods, for double underscore) let
your objects integrate with Python's built-in operators and functions.
"""


class BankAccount:
    """Demonstrate encapsulation with a "private" balance attribute."""

    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance  # leading underscore: "protected", by convention
        self.__pin = "0000"  # double underscore: name-mangled, harder to access

    @property
    def balance(self):
        """Expose a read-only view of the balance."""
        return self._balance

    def deposit(self, amount):
        """Add money to the account, validating the input first."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount):
        """Remove money from the account if funds allow it."""
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount

    def _check_pin(self, pin):
        """Internal helper (protected): not part of the public API."""
        return pin == self.__pin


class Money:
    """Demonstrate magic methods that let objects work with operators."""

    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        """Unambiguous representation, useful for debugging in the REPL."""
        return f"Money({self.amount!r})"

    def __str__(self):
        """Human-friendly representation, used by print() and str()."""
        return f"${self.amount:.2f}"

    def __eq__(self, other):
        """Define what it means for two Money objects to be equal."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount

    def __lt__(self, other):
        """Define ordering so Money objects can be compared and sorted."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __add__(self, other):
        """Overload the + operator to add two Money objects together."""
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount + other.amount)

    def __len__(self):
        """Let len() report something meaningful, e.g. whole dollars."""
        return int(self.amount)


if __name__ == "__main__":
    account = BankAccount("Ada", 100)
    account.deposit(50)
    account.withdraw(30)
    print(f"{account.owner}'s balance: {account.balance}")

    try:
        account.withdraw(1000)
    except ValueError as error:
        print("Caught an error:", error)

    # __pin is name-mangled to _BankAccount__pin, so this would raise
    # AttributeError: account.__pin
    print("Direct pin check:", account._check_pin("0000"))

    price1 = Money(19.99)
    price2 = Money(5.01)
    total = price1 + price2

    print("repr:", repr(total))
    print("str:", total)
    print("Equal?", price1 == Money(19.99))
    print("Less than?", price2 < price1)
    print("len(total):", len(total))
    print("Sorted:", sorted([price1, price2, total]))
