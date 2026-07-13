"""
Lesson 1.4: Strings

Strings are sequences of characters. Python offers many built-in
tools to create, inspect and transform them.
"""

greeting = "Hello"
name = "World"

# Concatenation and f-strings
message = greeting + ", " + name + "!"
print(message)
print(f"{greeting}, {name}! (using an f-string)")

# Useful string methods
text = "  Learning Python is Fun  "
print("original:", repr(text))
print("stripped:", repr(text.strip()))
print("lower:", text.strip().lower())
print("upper:", text.strip().upper())
print("replaced:", text.strip().replace("Fun", "Awesome"))
print("split:", text.strip().split(" "))

# Indexing and slicing
word = "Python"
print("first letter:", word[0])
print("last letter:", word[-1])
print("first three letters:", word[0:3])
print("reversed:", word[::-1])

# Length
print("length of word:", len(word))
