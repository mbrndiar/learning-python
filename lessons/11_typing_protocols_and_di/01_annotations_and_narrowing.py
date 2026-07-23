"""
Chapter 11, Lesson 1: Annotations and Narrowing

Purpose: introduce type annotations as an optional, non-enforced runtime
feature that static tools (mypy, IDEs) use; union types (`X | None`) for
values that may be absent; narrowing a union with an `if` check so a type
checker (and a human reader) can treat each branch as a single, definite
type; and type aliases for a recurring shape.

Prerequisites: Chapter 9 (classes) and Chapter 10 (decorators/generators)
-- annotations here describe ordinary functions and classes already
familiar from those chapters.

Read this file top to bottom, predict each output, then run it:

    python lessons/11_typing_protocols_and_di/01_annotations_and_narrowing.py
"""


# Step 1: annotations document expected types but are NOT enforced by
# Python itself at runtime -- only external tools like mypy check them.
def add(a: int, b: int) -> int:
    """A function with hinted parameter types and a return type."""
    return a + b


print("add(2, 3):", add(2, 3))
# This next call violates add's `int` hints, and Python runs it anyway --
# annotations are documentation for tools, not a runtime contract like a
# function's actual behavior.
print("add('2', '3') (hint violated, still runs):", add("2", "3"))


# Step 2: `X | None` documents that a value may be absent -- the union of
# type X and the singleton type of None.
def find_user(user_id: int, users: dict[int, str]) -> str | None:
    """Return a user's name, or None if `user_id` is not present."""
    return users.get(user_id)


users = {1: "Ada", 2: "Grace"}
print("\nfind_user(1, users):", find_user(1, users))
print("find_user(99, users):", find_user(99, users))


# Step 3: narrowing. Inside `if maybe_name is not None:`, a type checker
# treats `maybe_name` as `str` (the None case has been ruled out by the
# check), even though its declared type is `str | None`. This is not
# special syntax -- it is the type checker reading the same `if` a human
# reader already relies on to reason about the code.
def shout_if_present(maybe_name: str | None) -> str:
    """Return an upper-cased greeting, or a placeholder when absent."""
    if maybe_name is None:
        return "(no name)"
    # Here, maybe_name is narrowed to `str` -- .upper() is always valid
    # on this branch, which is exactly what the `is None` check ruled out.
    return maybe_name.upper()


print("\nshout_if_present('ada'):", shout_if_present("ada"))
print("shout_if_present(None):", shout_if_present(None))


# Step 4: a type alias names a recurring shape so signatures stay
# readable instead of repeating a long annotation everywhere.
UserMap = dict[int, str]


def describe_users(users: UserMap) -> list[str]:
    """Describe each user as 'id: name', sorted by id."""
    return [f"{user_id}: {name}" for user_id, name in sorted(users.items())]


print("\ndescribe_users(users):", describe_users(users))


class Point:
    """Type hints can annotate instance attributes too."""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y

    def distance_to(self, other: "Point") -> float:
        # A string annotation ("Point") refers to the class being
        # defined, since Point is not fully defined yet at this line.
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


p1 = Point(0, 0)
p2 = Point(3, 4)
print("\ndistance:", p1.distance_to(p2))

# --- One-variable experiment -------------------------------------------
# Change shout_if_present's body so it calls maybe_name.upper() BEFORE
# the `if maybe_name is None:` check, instead of after. Predict what
# happens when this runs with None -- and separately, predict what mypy
# (not Python itself) would say about that reordered code, given
# maybe_name's declared type is str | None at that point.
