"""
Chapter 2, Lesson 1: Operators and Expressions

Purpose: give arithmetic, comparison, and boolean operators full treatment,
including precedence and short-circuit evaluation. Chapter 1 used `==` and
`>=` only as a small preview; this lesson is where operators become the main
subject.

Prerequisites: Chapter 1 (names, core scalar types, bool, truthiness).

Read this file top to bottom, predict each output, then run it:

    python lessons/02_text_and_numbers/01_operators_and_expressions.py
"""

# Step 1: arithmetic operators. With integer operands, `/` performs true
# division and always returns a float; `//` is floor division and rounds
# toward negative infinity (not toward zero), which matters for negative
# numbers. `%` is the remainder and satisfies a == (a // b) * b + (a % b).
a = 10
b = 3
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)  # true division -> float
print("a // b =", a // b)  # floor division -> int
print("a % b =", a % b)
print("a ** b =", a**b)  # exponentiation

print("\n-10 // 3 =", -10 // 3)  # floors toward negative infinity: -4, not -3
print("-10 % 3 =", -10 % 3)  # remainder keeps the sign of the divisor

# Step 2: precedence. `**` binds tighter than unary minus on its left, `*`
# and `/` bind tighter than `+` and `-`, and parentheses always win. When in
# doubt, add parentheses -- it costs nothing and removes ambiguity for the
# reader.
without_parens = 2 + 3 * 4
with_parens = (2 + 3) * 4
print("\n2 + 3 * 4 =", without_parens)
print("(2 + 3) * 4 =", with_parens)
print("2 ** 3 ** 2 =", 2**3**2)  # ** is right-associative: 2 ** (3 ** 2)

# Step 3: comparisons produce bool and can be chained. `0 <= age < 130` is
# equivalent to `0 <= age and age < 130`, but `age` is evaluated only once.
age = 42
print("\n0 <= age < 130:", 0 <= age < 130)
print("age == 42 and age != 41:", age == 42 and age != 41)

# Step 4: `and`/`or` short-circuit and return one of their operands, not
# necessarily a bool. Python evaluates the right operand only when the
# result cannot yet be determined from the left one alone.
sunny = True
warm = False
print("\nsunny and warm:", sunny and warm)
print("sunny or warm:", sunny or warm)
print("not sunny:", not sunny)

# With non-bool operands, `and`/`or` return whichever operand decided the
# result, which is a common source of surprise the first time it is seen.
first_name = ""
fallback_name = "Guest"
chosen_name = (
    first_name or fallback_name
)  # "" is falsy, so `or` returns the second operand
print("\nfirst_name or fallback_name ->", repr(chosen_name))

# Step 5: floating-point numbers are approximations. 0.1 + 0.2 is not
# exactly 0.3 in binary floating point, so direct equality can fail even
# though the values print as if they were equal.
total = 0.1 + 0.2
print("\n0.1 + 0.2 ==", repr(total))
print("total == 0.3:", total == 0.3)

# --- One-variable experiment -------------------------------------------
# Change `age` in Step 3 to 130 and predict the result of the chained
# comparison before rerunning. Then change it to -1 and predict again.
