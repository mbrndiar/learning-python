"""
Chapter 5, Lesson 1: Function Contracts

Purpose: introduce `def`, parameters, return values, the distinction
between a pure function and one with side effects, and basic
`name: type -> type` annotations as documentation (not enforcement).

Prerequisites: Chapters 1-4 (values, text/numbers, collections, flow and
iteration). This is the first lesson in the whole course to use `def`.

Read this file top to bottom, predict each output, then run it:

    python lessons/05_functions/01_function_contracts.py
"""


# Step 1: `def` creates a function object and binds it to a name. The
# indented block is the function *body*; it does not run until the
# function is *called*. Parameters are local names, bound to whatever
# arguments the caller supplies.
def greet(name):
    """Return a greeting string. A docstring documents the contract."""
    return f"Hello, {name}!"


# Step 2: `return` immediately ends the call and hands a value back to the
# caller. Calling greet("Ada") does not print anything by itself -- it
# produces a value that the caller decides what to do with.
message = greet("Ada")
print(message)


# Step 3: a function with no `return` statement (or a bare `return`)
# implicitly returns `None`. This is a *side-effecting* function: it does
# something observable (printing) rather than handing back a value.
def announce(message):
    print(f"Announcement: {message}")


announce_result = announce("Lesson started")
print("announce_result:", announce_result)
assert announce_result is None


# Step 4: a *pure* function's result depends only on its arguments, and it
# has no observable side effects (no printing, no mutating shared data). A
# pure function is easier to test and reason about, because calling it
# twice with the same arguments always gives the same result.
def square(number):
    return number**2


assert square(4) == 16
assert square(4) == 16  # calling again with the same input: same result


# Step 5: parameters and return values may carry a `name: type -> type`
# annotation. Python does not enforce these at runtime -- they are
# documentation for readers and tools, not a type checker built into the
# language.
def to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit. The annotation says: takes a float,
    returns a float -- but calling to_fahrenheit("100") would still run."""
    return celsius * 9 / 5 + 32


assert to_fahrenheit(0) == 32
assert to_fahrenheit(100) == 212

# --- One-variable experiment -------------------------------------------
# Call to_fahrenheit("100") (a string, not a float) and predict what
# happens: TypeError, a wrong-looking result, or success? Annotations are
# not enforced, so the actual outcome depends on what the operators inside
# the function do with a string argument.

print("square(4) =", square(4))
print("to_fahrenheit(100) =", to_fahrenheit(100))
