"""
Chapter 9, Lesson 3: Properties and Encapsulation

Purpose: control access to an object's internal state using naming
conventions (`_name`, `__name`) and `@property`; explain what a property
setter validates that a plain attribute cannot; and explain what name
mangling does and does not protect against.

Prerequisites: Lessons 1-2 (classes/methods, composition/inheritance).

Read this file top to bottom, predict each output, then run it:

    python lessons/09_object_oriented_programming/03_properties_and_encapsulation.py
"""


class BankAccount:
    """Demonstrate encapsulation with a validated, read-only-looking balance."""

    def __init__(self, owner, balance=0):
        self.owner = owner
        # A single leading underscore is a convention meaning "not part of
        # the public API" -- Python does not enforce it; it signals intent
        # to other developers (and to yourself, later).
        self._balance = balance
        # A double leading underscore triggers name mangling: Python
        # rewrites __pin to _BankAccount__pin, making accidental
        # collisions with subclass attributes unlikely. It is not a
        # security boundary -- Step 3 shows the mangled name directly.
        self.__pin = "0000"

    @property
    def balance(self):
        """Expose a read-only view of the balance through attribute syntax."""
        return self._balance

    def deposit(self, amount):
        """Add money to the account, validating the input first."""
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount):
        """Remove money from the account if funds allow it."""
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount

    def _check_pin(self, pin):
        """Internal helper (protected): not part of the public API."""
        return pin == self.__pin


# Step 1: balance reads like a plain attribute but is computed through a
# property -- there is no way to assign account.balance directly, because
# no setter was defined for it.
account = BankAccount("Ada", 100)
account.deposit(50)
account.withdraw(30)
print(f"{account.owner}'s balance: {account.balance}")

try:
    account.balance = 1_000_000
except AttributeError as error:
    print("Cannot assign to a read-only property:", error)

# Step 2: deposit/withdraw validate their input before mutating state --
# the property alone only controls *reading*; these methods control
# *writing*, which is why _balance itself stays non-public.
try:
    account.withdraw(1000)
except ValueError as error:
    print("\nCaught an error:", error)

# Step 3: name mangling. `account.__pin` would raise AttributeError,
# because Python renamed the attribute to _BankAccount__pin at class
# definition time -- but the mangled name is still directly reachable, so
# this is obscurity, not a security boundary.
print("\nDirect pin check via method:", account._check_pin("0000"))
print("Mangled attribute is reachable:", account._BankAccount__pin)

# --- One-variable experiment -------------------------------------------
# Add a `set_pin(self, old_pin, new_pin)` method that only updates
# self.__pin when `old_pin` matches. Predict: does that method also need
# name mangling awareness, or does __pin work normally from *inside* the
# class? (Name mangling only affects the *lookup*, not code written
# inside the class body itself -- __pin means the same mangled name
# everywhere inside BankAccount.)
