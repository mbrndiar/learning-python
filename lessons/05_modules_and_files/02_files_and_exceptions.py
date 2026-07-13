"""
Lesson 5.2: Working with Files and Exceptions

This lesson shows how to write to and read from a file, and how to
handle errors gracefully using try/except.
"""

import os

file_path = os.path.join(os.path.dirname(__file__), "sample.txt")

# Writing to a file
with open(file_path, "w", encoding="utf-8") as file:
    file.write("Hello, file!\n")
    file.write("Learning Python is fun.\n")

# Reading from a file
with open(file_path, "r", encoding="utf-8") as file:
    contents = file.read()

print("File contents:")
print(contents)

# Clean up the file we created
os.remove(file_path)

# Handling exceptions
try:
    result = 10 / 0
except ZeroDivisionError as error:
    print("Caught an error:", error)
finally:
    print("This always runs, error or not.")
