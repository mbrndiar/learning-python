"""
Lesson 1.3: Operators

Arithmetic, comparison and logical operators are the building blocks
of any expression in Python.
"""

a = 10
b = 3

# Arithmetic operators
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)  # true division -> float
print("a // b =", a // b)  # floor division -> int
print("a % b =", a % b)  # modulo (remainder)
print("a ** b =", a**b)  # exponentiation

# Comparison operators (return a bool)
print("a == b:", a == b)
print("a != b:", a != b)
print("a > b:", a > b)
print("a <= b:", a <= b)

# Logical operators
sunny = True
warm = False
print("sunny and warm:", sunny and warm)
print("sunny or warm:", sunny or warm)
print("not sunny:", not sunny)
