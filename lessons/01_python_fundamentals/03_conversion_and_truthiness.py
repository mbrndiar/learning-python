"""
Chapter 1, Lesson 3: Conversion and Truthiness

Purpose: convert between int, float, str, and bool explicitly; describe (but
not yet catch) a conversion failure; and use `assert` as a first, local
self-check.

Prerequisites: 02_values_names_and_types.py (objects, names, core types,
type()/isinstance()).

Read this file top to bottom, predict each output, then run it:

    python lessons/01_python_fundamentals/03_conversion_and_truthiness.py
"""

# Step 1: explicit conversion. Each of these built-in names is a type used
# as a constructor: calling it converts its argument to that type.
whole_number = int("42")
measurement = float("3.5")
label = str(123)
truncated = int(-3.9)  # int() truncates toward zero; it does not round.

print("int('42') ->", whole_number)
print("float('3.5') ->", measurement)
print("str(123) ->", label)
print("int(-3.9) ->", truncated)

# Step 2: bool() tests truthiness, it does not parse words. Every non-empty
# string is truthy, including the string "False" -- the word is not
# inspected, only whether the string has any characters at all.
print("\nbool('False') ->", bool("False"))
print("bool('') ->", bool(""))
print("bool(0) ->", bool(0))
print("bool(1) ->", bool(1))
print("bool(None) ->", bool(None))

# Step 3 (bounded preview): comparisons produce bool values. `==` tests
# equality; `<`, `>`, `<=`, `>=` order values. Chapter 2 covers the full set
# of operators and their precedence -- this is only enough to make
# truthiness concrete.
age = 20
is_adult = age >= 18
print("\nage >= 18 ->", is_adult)
print("type(is_adult):", type(is_adult))

# Step 4: assert as a local self-check. `assert condition` does nothing when
# `condition` is truthy, and raises AssertionError when it is falsy. This
# lets a script verify its own expectations instead of only printing values
# for a human to eyeball.
assert whole_number == 42
assert measurement == 3.5
# `not` inverts truthiness. Chapter 2 introduces the complete boolean operator
# set; this one unary check is enough to state the expected false case here.
assert bool("False")
assert not bool("")
print("\nAll assertions in Step 4 passed silently -- that is expected.")

# `assert` can also carry a message, shown only if the condition is false.
assert is_adult, "expected the sample age to represent an adult"

# Step 5: a conversion failure. int() and float() require their argument to
# match the constructor's grammar; text that does not match raises
# ValueError. This course has not introduced `try`/`except` yet, so this
# lesson only *describes* the failure instead of triggering it -- running
# the line below (uncommented) would stop the script immediately, because an
# unhandled exception ends the program.
#
#   int("not-a-number")  # would raise: ValueError: invalid literal for int()
#
# Exception *handling* (catching and recovering from this) is covered later,
# in the Modules and Files chapter -- for now, the important habit is
# validating or trusting input before converting it.
print("\nA conversion failure would raise ValueError; see the comment above.")

# --- One-variable experiment -------------------------------------------
# Change `age` in Step 3 to 15 and predict what `is_adult` and its printed
# type will be before rerunning. The type does not change -- only the value
# does, because comparisons always produce a bool.
