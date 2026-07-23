"""
Chapter 7, Lesson 3: Text and Binary Files

Purpose: open files in text and binary modes, understand how encodings and
newline translation apply to text mode only, work with raw bytes, and take
explicit ownership of closing a file (before Lesson 4 automates it with
`with`).

Prerequisites: Lessons 1-2 (exception flow, paths). This lesson opens and
closes files by hand first, on purpose, so `with` in Lesson 4 is clearly a
convenience over an explicit pattern you already understand -- not unknown
magic.

Read this file top to bottom, predict each output, then run it:

    python lessons/07_exceptions_files_and_paths/03_text_and_binary_files.py
"""

import tempfile
from pathlib import Path

temporary = tempfile.TemporaryDirectory(prefix="files_lesson_")
root = Path(temporary.name)

try:
    # Step 1: explicit ownership. open() returns a file object that must be
    # closed to release the underlying OS resource and guarantee buffered
    # writes reach disk. Without `with` (introduced next lesson), that is
    # the caller's job -- shown here with a manual try/finally, echoing
    # Lesson 1's finally clause.
    manual_path = root / "manual.txt"
    file = open(manual_path, "w", encoding="utf-8")
    try:
        file.write("Opened and closed by hand.\n")
    finally:
        file.close()
    print("File closed manually:", file.closed)

    # Step 2: modes. "w" creates or truncates; "a" appends; "r" (the
    # default) reads. Every operation repeats the explicit ownership pattern
    # so no file handle leaks before `with` is introduced.
    text_path = root / "sample.txt"
    handle = open(text_path, "w", encoding="utf-8")
    try:
        handle.write("Hello, file!\n")
        handle.write("Learning Python is fun.\n")
    finally:
        handle.close()

    handle = open(text_path, encoding="utf-8")
    try:
        contents = handle.read()
    finally:
        handle.close()
    print("\nFile contents:")
    print(contents)

    handle = open(text_path, "a", encoding="utf-8")
    try:
        handle.write("Appended line.\n")
    finally:
        handle.close()
    print("After append:", text_path.read_text(encoding="utf-8").splitlines())

    # Step 3: newline behavior. Text mode translates "\n", "\r", and
    # "\r\n" to "\n" on read by default. newline="" preserves those
    # line-ending sequences in the returned str; it still decodes bytes.
    mixed_path = root / "mixed_endings.txt"
    mixed_path.write_bytes(b"first\r\nsecond\nthird\r")
    handle = open(mixed_path, encoding="utf-8")
    try:
        translated = handle.read()
    finally:
        handle.close()
    handle = open(mixed_path, encoding="utf-8", newline="")
    try:
        untranslated = handle.read()
    finally:
        handle.close()
    print("\nTranslated newlines:", translated.splitlines())
    print("Untranslated text (raw):", repr(untranslated))

    # Step 4: binary mode transfers bytes unchanged -- no encoding
    # parameter exists for "wb"/"rb" because there is no text to decode.
    binary_path = root / "sample.bin"
    binary_payload = b"\x00Python\xff"
    handle = open(binary_path, "wb")
    try:
        handle.write(binary_payload)
    finally:
        handle.close()
    handle = open(binary_path, "rb")
    try:
        binary_contents = handle.read()
    finally:
        handle.close()
    print("\nBinary contents:", binary_contents)
    print("Binary contents as hex:", binary_contents.hex())
    assert binary_contents == binary_payload
finally:
    temporary.cleanup()

# --- One-variable experiment -------------------------------------------
# Remove `newline=""` from the `untranslated` read above and predict how
# `repr(untranslated)` changes. Text mode's default newline translation
# collapses every "\r\n" and "\r" to "\n" -- the file on disk does not
# change, only what read() hands back changes.
