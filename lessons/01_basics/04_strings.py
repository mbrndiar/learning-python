"""
Lesson 1.4: Strings

Strings are immutable sequences of Unicode characters. Python offers many
built-in tools to inspect and transform them; transformations return new
strings instead of modifying the original.
"""

greeting = "Hello"
name = "World"

# Concatenation joins strings. F-strings evaluate expressions inside braces
# and are generally clearer when text and non-text values must be combined.
message = greeting + ", " + name + "!"
print(message)
print(f"{greeting}, {name}! (using an f-string)")

# None of these methods changes `text`; each call returns a new string.
text = "  Learning Python is Fun  "
print("original:", repr(text))
print("stripped:", repr(text.strip()))
print("lower:", text.strip().lower())
print("upper:", text.strip().upper())
print("replaced:", text.strip().replace("Fun", "Awesome"))
print("split:", text.strip().split(" "))

# Indices begin at zero, negative indices count from the end, and a slice
# excludes its stop index. An invalid single index raises IndexError.
word = "Python"
print("first letter:", word[0])
print("last letter:", word[-1])
print("first three letters:", word[0:3])
print("reversed:", word[::-1])

# Length
print("length of word:", len(word))
