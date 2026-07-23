"""
Chapter 9, Lesson 4: The Python Data Model

Purpose: implement special ("dunder") methods so custom objects
participate in Python's built-in syntax -- printing, equality, ordering,
arithmetic operators, `len()`, and iteration -- rather than needing
bespoke method names for each.

Prerequisites: Lessons 1-3 (classes, composition/inheritance, properties).

Read this file top to bottom, predict each output, then run it:

    python lessons/09_object_oriented_programming/04_python_data_model.py
"""


class Money:
    """Demonstrate dunder methods that integrate an object with operators."""

    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        """Unambiguous representation, useful for debugging and in the REPL."""
        return f"Money({self.amount!r})"

    def __str__(self):
        """Human-friendly representation, used by print() and str()."""
        return f"${self.amount:.2f}"

    def __eq__(self, other):
        """Define what it means for two Money values to be equal."""
        if not isinstance(other, Money):
            # NotImplemented (not the exception NotImplementedError) tells
            # Python to try the other operand's reflected method, and
            # ultimately to fall back to its normal default if neither
            # side supports the comparison.
            return NotImplemented
        return self.amount == other.amount

    def __lt__(self, other):
        """Define ordering so Money values can be compared and sorted."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __add__(self, other):
        """Overload + to add two Money values together."""
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount + other.amount)

    def __float__(self):
        """Support an explicit conversion via float(money_value)."""
        return float(self.amount)


# Step 1: __repr__ vs __str__. repr() favors an unambiguous, often
# code-like form; str() (used by print()) favors a human-friendly form.
price1 = Money(19.99)
price2 = Money(5.01)
total = price1 + price2
print("repr(total):", repr(total))
print("str(total):", total)

# Step 2: __eq__/__lt__ let Money participate in ==, <, and sorted().
print("\nEqual to an equivalent Money?", price1 == Money(19.99))
print("Less than?", price2 < price1)
print("Sorted:", sorted([price1, price2, total]))
print("float(total):", float(total))


class Vector:
    """A minimal 2D vector supporting equality and addition."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x!r}, {self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)


# Step 3: an unsupported operand returns NotImplemented rather than
# raising directly -- Python then raises a clear TypeError itself once no
# operand on either side can handle the operation.
print("\nVector(1, 2) + Vector(3, 4):", Vector(1, 2) + Vector(3, 4))
print("Vector.__add__(Vector(1, 2), 3):", Vector.__add__(Vector(1, 2), 3))


class Playlist:
    """Expose container behavior through the len()/iteration protocols."""

    def __init__(self, titles):
        self._titles = list(titles)

    def __len__(self):
        return len(self._titles)

    def __iter__(self):
        return iter(self._titles)


# Step 4: __len__ and __iter__ let a custom object work with len() and
# for-loops/list() exactly like a built-in sequence, without exposing its
# internal list directly.
playlist = Playlist(["First", "Second", "Third"])
print("\nlen(playlist):", len(playlist))
print("list(playlist):", list(playlist))
for title in playlist:
    print(" -", title)

# --- One-variable experiment -------------------------------------------
# Remove Vector's __eq__ (or comment it out) and predict what
# Vector(1, 2) == Vector(1, 2) returns then. Without a custom __eq__, the
# inherited default from `object` compares identity (is), not value --
# so two distinct, equal-looking Vectors would no longer compare equal.
