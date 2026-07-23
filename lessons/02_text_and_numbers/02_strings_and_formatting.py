"""
Chapter 2, Lesson 2: Strings and Formatting

Purpose: cover string immutability, indexing/slicing, common methods,
f-strings, and formatting (alignment/precision).

Prerequisites: 01_operators_and_expressions.py (operators, precedence).

Read this file top to bottom, predict each output, then run it:

    python lessons/02_text_and_numbers/02_strings_and_formatting.py
"""

# Step 1: strings are immutable sequences of Unicode characters. Every
# string method returns a *new* string; none of them changes the original.
greeting = "Hello"
name = "World"
message = greeting + ", " + name + "!"
print(message)

# An f-string evaluates expressions inside `{}` and is usually clearer than
# concatenation once text and computed values must be combined.
print(f"{greeting}, {name}! ({len(greeting)} + {len(name)} letters)")

# Step 2: common methods, all non-mutating.
text = "  Learning Python is Fun  "
print("\noriginal: |" + text + "|")
print("stripped: |" + text.strip() + "|")
print("lower:", text.strip().lower())
print("upper:", text.strip().upper())
print("replaced:", text.strip().replace("Fun", "Awesome"))
print("text unchanged: |" + text + "|")

# Step 3: indexing and slicing. Indices start at 0; negative indices count
# from the end; a slice's stop index is excluded. An out-of-range single
# index raises IndexError, but an out-of-range slice bound is clamped
# instead of raising.
word = "Python"
print("\nword[0]:", word[0])
print("word[-1]:", word[-1])
print("word[0:3]:", word[0:3])
print("word[::-1]:", word[::-1])  # step -1 reverses the string
print("word[2:100]: |" + word[2:100] + "|")  # clamped, no error
print("len(word):", len(word))

# Step 4: f-string format specifiers control width, alignment, and
# precision. The part after `:` is the format spec; `.2f` means "fixed
# point, 2 digits after the decimal point," `>8` means "right-align in a
# field 8 characters wide."
price = 19.5
label = "cm"
print(f"\n{price:.2f} {label}")
print(f"[{label:>8}]")
print(f"[{label:<8}]")
print(f"[{label:^8}]")
print(f"{1234567:,}")  # thousands separator

# --- One-variable experiment -------------------------------------------
# Change `price` to 19.987 and predict what `{price:.2f}` will print before
# rerunning -- .2f rounds, it does not truncate.
