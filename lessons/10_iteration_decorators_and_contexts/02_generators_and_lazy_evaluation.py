"""
Chapter 10, Lesson 2: Generators and Lazy Evaluation

Purpose: use `yield` to write a generator function -- the easiest way to
build an iterator without hand-writing `__iter__`/`__next__` -- and see
generators' defining property: values are computed lazily, one at a
time, only as requested, and a generator can be run through exactly once.

Prerequisites: Lesson 1 (iterables, iterators, StopIteration). Everything
here is a different way to reach the same protocol Lesson 1 implemented
by hand with `CountUp`.

Read this file top to bottom, predict each output, then run it:

    python lessons/10_iteration_decorators_and_contexts/02_generators_and_lazy_evaluation.py
"""


def countdown(start):
    """A generator function: calling it does not run the body -- it
    returns a generator object immediately, paused before the first line.
    """
    # Execution pauses at each yield and resumes right after it the next
    # time a value is requested; the suspended frame keeps `start`
    # between yields, exactly like CountUp kept `self.current` in
    # Lesson 1 -- but here Python manages that state automatically.
    while start > 0:
        yield start
        start -= 1
    yield "Liftoff!"


# Step 1: calling countdown(3) does not execute anything yet.
countdown_gen = countdown(3)
print("Calling countdown(3) returns a generator, not a list:", type(countdown_gen))

print("\nConsuming it with a for loop:")
for value in countdown_gen:
    print(" ", value)


def fibonacci_up_to(limit):
    """Lazily generate Fibonacci numbers less than `limit`."""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


# Step 2: laziness. Calling fibonacci_up_to(30) does no computation --
# only iterating it (here, via list()) pulls values out one at a time.
fib_gen = fibonacci_up_to(30)
print("\nfibonacci_up_to(30):", list(fib_gen))

# Step 3: exhaustion. A generator can be iterated through exactly once;
# asking for its values again yields nothing further, unlike a list.
print("Reusing the same (now exhausted) generator:", list(fib_gen))
print("A fresh call still works:", list(fibonacci_up_to(30)))

# Step 4: a generator expression is the lazy counterpart of a list
# comprehension -- same syntax, but wrapped in () instead of [].
squares = (n**2 for n in range(5))
print("\nGenerator expression, consumed once:", list(squares))

# --- One-variable experiment -------------------------------------------
# Change `while a < limit` to `while a <= limit` in fibonacci_up_to and
# predict whether fibonacci_up_to(21) then includes 21 in its output.
# Nothing else about how the generator is consumed needs to change --
# laziness is a property of *how* values are produced, independent of
# what condition decides when to stop.
