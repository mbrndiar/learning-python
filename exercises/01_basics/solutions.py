"""
Solutions: 01 Basics

Reference implementations for exercises/01_basics/exercises.py.
Try to solve the exercises yourself before checking this file!
"""


def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


def is_palindrome(text):
    normalized = text.lower()
    return normalized == normalized[::-1]


def count_vowels(text):
    return sum(1 for char in text.lower() if char in "aeiou")


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
