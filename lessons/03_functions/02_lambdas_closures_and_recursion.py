"""
Lesson 3.2: Lambdas, Closures and Recursion

This lesson goes beyond basic function definitions to cover three more
advanced (but common) function-related concepts in Python.
"""

# --- Lambda expressions -----------------------------------------------
# A lambda is a small, anonymous, single-expression function. Assigning a
# nontrivial lambda to a name usually loses readability; use `def` when the
# operation deserves documentation, statements, or reuse in several places.
square = lambda x: x**2
add = lambda a, b: a + b

# The key function is called for each item to compute a comparison value.
# sorted() returns a new list and leaves `words` unchanged.
words = ["banana", "kiwi", "apple", "fig"]
by_length = sorted(words, key=lambda word: len(word))


# --- Closures -----------------------------------------------------------
def make_multiplier(factor):
    """Return a function that remembers `factor` even after this call ends.

    `multiplier` is a closure: it "closes over" the `factor` variable from
    its enclosing scope.
    """

    # Each call to make_multiplier creates a distinct enclosing `factor`.
    # `double` and `triple` below therefore share code but retain different
    # captured environments.
    def multiplier(number):
        return number * factor

    return multiplier


def make_counter():
    """Demonstrate `nonlocal`: mutating an enclosing variable from a closure."""
    count = 0

    def increment():
        # Assignment would normally create a new local `count`. `nonlocal`
        # redirects that assignment to the nearest enclosing function scope.
        nonlocal count
        count += 1
        return count

    return increment


# --- Recursion -----------------------------------------------------------
def factorial(n):
    """Compute n! recursively. The base case stops the recursion."""
    # A recursive function needs both a stopping case and progress toward it.
    # Each unfinished call remains on the call stack until the base value
    # returns and the pending multiplications can resolve.
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    """Return the n-th Fibonacci number with deliberately naive recursion.

    This mirrors the mathematical definition but recalculates the same values.
    It is a teaching example, not an efficient implementation for large n.
    """
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    print("square(5) =", square(5))
    print("add(2, 3) =", add(2, 3))
    print("words sorted by length:", by_length)
    print("filtered (len > 4):", list(filter(lambda w: len(w) > 4, words)))
    print("mapped (upper):", list(map(lambda w: w.upper(), words)))

    double = make_multiplier(2)
    triple = make_multiplier(3)
    print("\ndouble(5) =", double(5))
    print("triple(5) =", triple(5))

    counter = make_counter()
    print("\ncounter():", counter())
    print("counter():", counter())
    print("counter():", counter())

    print("\nfactorial(5) =", factorial(5))
    print("fibonacci(0..7):", [fibonacci(i) for i in range(8)])
    print("Naive Fibonacci is readable, but repeated work makes it slow for large n.")
