"""
Solutions: 03 Functions
"""


def make_multiplier(factor):
    def multiplier(value):
        return value * factor

    return multiplier


def sum_all(*args):
    return sum(args)


def describe(**kwargs):
    return ", ".join(f"{key}={value}" for key, value in kwargs.items())


def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    double = make_multiplier(2)
    triple = make_multiplier(3)
    assert double(5) == 10
    assert triple(5) == 15
    print("make_multiplier: OK")

    assert sum_all(1, 2, 3) == 6
    assert sum_all() == 0
    print("sum_all: OK")

    assert describe(name="Ada", age=36) == "name=Ada, age=36"
    print("describe: OK")

    assert factorial(0) == 1
    assert factorial(5) == 120
    print("factorial: OK")

    print("\nAll checks passed!")
