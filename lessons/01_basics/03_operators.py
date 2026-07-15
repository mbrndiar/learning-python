"""
Lesson 1.3: Operators

Arithmetic, comparison and logical operators are the building blocks
of any expression in Python.
"""

a = 10
b = 3

# For the integer operands demonstrated here, `/` performs true division and
# returns a float. Integer `//` floors toward negative infinity, so
# `-10 // 3` is -4 rather than -3. Other numeric types can define their own
# result types and division behavior.
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)  # true division -> float
print("a // b =", a // b)  # floor division -> int
print("a % b =", a % b)  # satisfies: a == (a // b) * b + (a % b)
print("a ** b =", a**b)  # exponentiation

# Comparisons between these built-in numbers produce bool values and do not
# modify either operand. User-defined types can customize comparison behavior.
print("a == b:", a == b)
print("a != b:", a != b)
print("a > b:", a > b)
print("a <= b:", a <= b)

# `and` and `or` short-circuit: Python evaluates the right operand only when it
# is needed. With non-boolean operands they return one operand, not necessarily
# True or False; these boolean examples keep that first encounter simple.
sunny = True
warm = False
print("sunny and warm:", sunny and warm)
print("sunny or warm:", sunny or warm)
print("not sunny:", not sunny)
