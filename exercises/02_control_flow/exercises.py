"""
Exercises: 02 Control Flow

Implement each function below, then run this file directly to check
your work.
"""


def fizzbuzz(n):
    """Return a list of strings for numbers 1..n (inclusive) where:
    - multiples of 3 become "Fizz"
    - multiples of 5 become "Buzz"
    - multiples of both become "FizzBuzz"
    - everything else becomes the number as a string
    """
    # TODO: implement this function
    raise NotImplementedError


def count_evens(numbers):
    """Return how many numbers in the list are even."""
    # TODO: implement this function
    raise NotImplementedError


def first_negative(numbers):
    """Return the first negative number in the list, or None if there
    isn't one. Stop looking as soon as one is found."""
    # TODO: implement this function
    raise NotImplementedError


if __name__ == "__main__":
    assert fizzbuzz(15)[:5] == ["1", "2", "Fizz", "4", "Buzz"]
    assert fizzbuzz(15)[-1] == "FizzBuzz"
    print("fizzbuzz: OK")

    assert count_evens([1, 2, 3, 4, 5, 6]) == 3
    assert count_evens([1, 3, 5]) == 0
    print("count_evens: OK")

    assert first_negative([3, 5, -2, 8, -9]) == -2
    assert first_negative([1, 2, 3]) is None
    print("first_negative: OK")

    print("\nAll checks passed!")
