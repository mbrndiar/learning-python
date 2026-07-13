"""
Exercises: 01 Basics

Implement each function below, then run this file directly to check
your work:

    python exercises/01_basics/exercises.py
"""


def celsius_to_fahrenheit(celsius):
    """Convert a Celsius temperature to Fahrenheit.

    Formula: F = C * 9/5 + 32
    """
    # TODO: implement this function
    raise NotImplementedError


def is_palindrome(text):
    """Return True if `text` reads the same forwards and backwards.

    Comparison should be case-insensitive, e.g. "Racecar" -> True.
    """
    # TODO: implement this function
    raise NotImplementedError


def count_vowels(text):
    """Return the number of vowels (a, e, i, o, u) in `text`,
    case-insensitive."""
    # TODO: implement this function
    raise NotImplementedError


if __name__ == "__main__":
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    print("celsius_to_fahrenheit: OK")

    assert is_palindrome("Racecar") is True
    assert is_palindrome("hello") is False
    print("is_palindrome: OK")

    assert count_vowels("Hello World") == 3
    assert count_vowels("PYTHON") == 1
    print("count_vowels: OK")

    print("\nAll checks passed!")
