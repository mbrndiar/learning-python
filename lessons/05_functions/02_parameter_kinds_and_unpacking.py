"""
Chapter 5, Lesson 2: Parameter Kinds and Unpacking

Purpose: cover default values, positional-only and keyword-only
parameters, `*args`/`**kwargs`, and call-site unpacking of collections
into arguments.

Prerequisites: 01_function_contracts.py; Chapter 3 (Collections) for
call-site unpacking of lists/dicts.

Read this file top to bottom, predict each output, then run it:

    python lessons/05_functions/02_parameter_kinds_and_unpacking.py
"""


# Step 1: a default value is used only when the caller omits that
# argument. Defaults are evaluated once, when `def` runs -- an immutable
# default (like the int 0 here) is safe to reuse across calls.
def add(a, b=0):
    return a + b


assert add(2, 3) == 5
assert add(5) == 5


# Step 2: the `/` marks every parameter before it as positional-only --
# the caller cannot pass it by keyword. The bare `*` marks every parameter
# after it as keyword-only -- the caller must pass it by keyword.
def format_measurement(value, /, unit="units", *, precision=1):
    return f"{value:.{precision}f} {unit}"


assert format_measurement(12.345, "cm", precision=2) == "12.35 cm"
# format_measurement(value=12.345, ...) would raise TypeError: `value` is
# positional-only.


# Step 3: `*args` collects any extra positional arguments into a tuple.
# The tuple exists (empty) even when no extra positional arguments are
# given, so the body can process every call through the same code path.
def sum_all(*numbers):
    return sum(numbers)


assert sum_all(1, 2, 3, 4) == 10
assert sum_all() == 0


# Step 4: `**kwargs` collects any extra keyword arguments into a dict,
# preserving the order they were supplied in (Python dicts remember
# insertion order).
def describe(**details):
    parts = []
    for key, value in details.items():
        parts.append(f"{key}={value}")
    return ", ".join(parts)


assert describe(name="Ada", age=36) == "name=Ada, age=36"


# Step 5: at a call site, `*` unpacks an iterable into positional
# arguments, and `**` unpacks a mapping into keyword arguments. This is
# the reverse direction of Steps 3-4: there, the function *collected*
# arguments; here, the caller *spreads* an existing collection out.
def describe_person(name, age, city="Unknown"):
    return f"{name} is {age} years old and lives in {city}."


person = ("Sam", 28)
location = {"city": "Bristol"}
assert (
    describe_person(*person, **location) == "Sam is 28 years old and lives in Bristol."
)

# --- One-variable experiment -------------------------------------------
# Change `location` to {"city": "Leeds", "age": 99} and predict what
# happens: age is already supplied positionally by `person`, so unpacking
# a second `age` by keyword should raise TypeError ("multiple values").

print("add(2, 3) =", add(2, 3))
print("format_measurement(...) =", format_measurement(12.345, "cm", precision=2))
print("sum_all(1, 2, 3, 4) =", sum_all(1, 2, 3, 4))
print("describe(...) =", describe(name="Ada", age=36))
print("describe_person(*person, **location) =", describe_person(*person, **location))
