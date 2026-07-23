"""
Chapter 1, Lesson 2: Values, Names, and Types

Purpose: introduce objects, names/assignment, the core scalar types
(int, float, str, bool, NoneType), and the `type()` / `isinstance()`
inspection tools.

Prerequisites: 01_running_python.py (print, comments, running a script).

Read this file top to bottom, predict each `print()` output, then run it:

    python lessons/01_python_fundamentals/02_values_names_and_types.py
"""

# Step 1: a literal creates a value (an object). Assignment binds a name to
# that object; the name itself is not a labelled storage box with a fixed
# type. Python is "dynamically typed": the type lives on the object, not on
# the name.
age = 25  # int: a whole number
height = 1.75  # float: a number with a fractional part
name = "Ada"  # str: text
is_learning = True  # bool: True or False
favorite_color = None  # NoneType: the single value that means "no value"

print("name:", name)
print("age:", age)
print("height:", height)
print("is_learning:", is_learning)
print("favorite_color:", favorite_color)
print("favorite_color is None:", favorite_color is None)

# Step 2: type() reports the exact type currently bound to a name.
# isinstance() asks "does this object behave as this type?" -- prefer it when
# checking a value's type in later conditional logic, because it also
# accepts subclasses (a distinction that matters once the course reaches
# classes).
print("\ntype(name):", type(name))
print("type(age):", type(age))
print("isinstance(age, int):", isinstance(age, int))
print("isinstance(age, str):", isinstance(age, str))

# Step 3: rebinding a name only changes what that name points to. It does not
# modify the object that was previously bound, and it does not affect any
# other name.
original_greeting = "Hello"
greeting = original_greeting
greeting = "Hi"
print("\ngreeting:", greeting)
print("original_greeting is unchanged:", original_greeting)

# Step 4: bool is its own type, but True and False behave like 1 and 0 in
# arithmetic. Prefer writing True/False to express a yes/no condition instead
# of relying on that numeric behavior -- it is shown here only so the
# behavior is not a surprise later.
print("\nTrue + True =", True + True)
print("type(True):", type(True))  # noqa: UP003 -- intentionally calling type()

# Step 5: naming rules and style. Names are case-sensitive, must not start
# with a digit, and by convention use snake_case. Avoid reusing the name of a
# built-in function such as `print`, `str`, or `type` -- doing so hides that
# built-in for the rest of the file.
learner_name = "Grace"  # snake_case: the conventional style in this course
print("\nlearner_name:", learner_name)

# --- One-variable experiment -------------------------------------------
# Try changing `favorite_color` above to a string such as "blue" *before* the
# None-related prints, rerun the file, and compare the "favorite_color:"
# line and the type it would report. Change one value at a time so you can
# attribute each difference in output to the exact line you changed.
