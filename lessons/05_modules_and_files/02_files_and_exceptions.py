"""
Lesson 5.2: Working with Files and Exceptions

This lesson writes and reads text using an explicit encoding, then handles an
expected error. A with statement closes the file even if its body raises an
exception.
"""

import os

file_path = os.path.join(os.path.dirname(__file__), "sample.txt")

# Mode "w" creates or truncates a file. Use "a" to append instead.
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

# Catch the narrowest error that can be handled here. A broad except would
# also hide unrelated programming defects.
try:
    result = 10 / 0
except ZeroDivisionError as error:
    print("Caught an error:", error)
finally:
    print("This always runs, error or not.")
