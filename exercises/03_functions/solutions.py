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


def format_label(name, /, *, category):
    return f"{category}: {name}"


def record_topic(topics, topic):
    topics.append(topic)


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

    assert format_label("Functions", category="Lesson") == "Lesson: Functions"
    print("format_label: OK")

    topics = ["parameters"]
    result = record_topic(topics, "return values")
    assert topics == ["parameters", "return values"]
    assert result is None
    print("record_topic: OK")

    assert factorial(0) == 1
    assert factorial(5) == 120
    print("factorial: OK")

    print("\nAll checks passed!")
