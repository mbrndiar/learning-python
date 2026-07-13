"""
Lesson 7.3: Type Hints

Type hints are optional annotations that document the expected types of
variables, function arguments and return values. Python does not enforce
them at runtime, but tools like `mypy` and IDEs use them to catch bugs
before the code even runs.
"""

from typing import Dict, List, Optional, Union


def add(a: int, b: int) -> int:
    """A function with hinted parameter types and return type."""
    return a + b


def greet(name: str, greeting: str = "Hello") -> str:
    """Type hints work the same way alongside default argument values."""
    return f"{greeting}, {name}!"


def find_user(user_id: int, users: Dict[int, str]) -> Optional[str]:
    """`Optional[str]` means the return value is either `str` or `None`."""
    return users.get(user_id)


def normalize(value: Union[int, float, str]) -> float:
    """`Union` means the parameter can be any one of several types."""
    return float(value)


def average(numbers: List[float]) -> float:
    """`List[float]` documents a list whose elements are expected to be floats."""
    return sum(numbers) / len(numbers)


class Point:
    """Type hints can also annotate instance attributes."""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y

    def distance_to(self, other: "Point") -> float:
        """Use a string annotation ("Point") to refer to the class being
        defined, since `Point` isn't fully defined yet at this point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


if __name__ == "__main__":
    print("add(2, 3) =", add(2, 3))
    print(greet("Ada"))

    users = {1: "Ada", 2: "Grace"}
    print("find_user(1, users):", find_user(1, users))
    print("find_user(99, users):", find_user(99, users))

    print("normalize(5):", normalize(5))
    print("normalize('3.14'):", normalize("3.14"))
    print("average([1.0, 2.0, 3.0]):", average([1.0, 2.0, 3.0]))

    p1 = Point(0, 0)
    p2 = Point(3, 4)
    print("distance:", p1.distance_to(p2))

    # Type hints are NOT enforced at runtime -- Python will happily run this
    # even though it violates the `int` hint on `add`. Tools like mypy
    # would flag this as an error without running the code.
    print("add('2', '3') (not actually enforced):", add("2", "3"))
