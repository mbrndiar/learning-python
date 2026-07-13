"""
Solutions: 02 Control Flow
"""


def fizzbuzz(n):
    result = []
    for number in range(1, n + 1):
        if number % 15 == 0:
            result.append("FizzBuzz")
        elif number % 3 == 0:
            result.append("Fizz")
        elif number % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(number))
    return result


def count_evens(numbers):
    count = 0
    for number in numbers:
        if number % 2 == 0:
            count += 1
    return count


def first_negative(numbers):
    for number in numbers:
        if number < 0:
            return number
    return None


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
