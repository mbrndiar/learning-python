"""
Lesson 7.2: Generators and Iterators

Iterators are objects that produce a sequence of values, one at a time.
Generators are the easiest way to create an iterator, using `yield`
instead of `return`.
"""


def countdown(start):
    """A generator function: calling it returns a generator object.

    Execution pauses at each `yield` and resumes right after it the next
    time a value is requested.
    """
    while start > 0:
        yield start
        start -= 1
    yield "Liftoff!"


def fibonacci_sequence(limit):
    """Lazily generate Fibonacci numbers up to (but not including) `limit`."""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


class Countdown:
    """A custom iterator implemented with the iterator protocol.

    Implementing `__iter__` and `__next__` lets an object work with
    `for` loops, `next()`, and other iteration tools, just like a
    generator does.
    """

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


if __name__ == "__main__":
    print("Generator-based countdown:")
    for value in countdown(3):
        print(" ", value)

    print("\nGenerators are lazy: values are computed on demand.")
    gen = fibonacci_sequence(30)
    print("  fibonacci_sequence(30):", list(gen))

    # Once exhausted, a generator cannot be reused.
    print("  reusing the same generator:", list(gen))

    print("\nGenerator expression (like a list comprehension, but lazy):")
    squares = (n**2 for n in range(5))
    print("  ", list(squares))

    print("\nClass-based iterator:")
    for value in Countdown(3):
        print(" ", value)

    # next() manually advances an iterator, raising StopIteration when done.
    iterator = iter(Countdown(2))
    print("\nManual iteration with next():")
    print(" ", next(iterator))
    print(" ", next(iterator))
    try:
        next(iterator)
    except StopIteration:
        print("  StopIteration raised: no more values")
