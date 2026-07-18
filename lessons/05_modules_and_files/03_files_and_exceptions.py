"""
Lesson 5.3: Working with Files and Exceptions

This lesson writes and reads text using an explicit encoding, preserves raw
bytes with binary modes, then handles an expected error. A with statement closes
the file even if its body raises an exception.
"""

import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="files_lesson_") as directory:
    root = Path(directory)
    file_path = root / "sample.txt"

    # Mode "w" creates or truncates a file. Use "a" to append instead.
    with file_path.open("w", encoding="utf-8") as file:
        file.write("Hello, file!\n")
        file.write("Learning Python is fun.\n")

    # Text mode decodes bytes through the stated encoding and returns str.
    with file_path.open("r", encoding="utf-8") as file:
        contents = file.read()

    print("File contents:")
    print(contents)

    binary_path = root / "sample.bin"
    binary_payload = b"\x00Python\xff"

    # Binary mode transfers bytes unchanged and has no text encoding parameter.
    # Use it when the exact byte representation is the file format's contract.
    with binary_path.open("wb") as file:
        file.write(binary_payload)
    with binary_path.open("rb") as file:
        binary_contents = file.read()

    print("Binary contents:", binary_contents)
    print("Binary contents as hex:", binary_contents.hex())

# Catch the narrowest error that can be handled here. A broad except would
# also hide unrelated programming defects.
try:
    result = 10 / 0
except ZeroDivisionError as error:
    print("Caught an error:", error)
finally:
    print("This always runs, error or not.")
