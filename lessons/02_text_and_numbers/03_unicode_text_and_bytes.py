"""
Chapter 2, Lesson 3: Unicode Text and Bytes

Purpose: introduce the text/binary boundary -- encoding, decoding, and basic,
controlled mutation of binary data with `bytearray`. This lesson stays at a
basic level: the buffer protocol and `memoryview` are out of scope here.

Prerequisites: 02_strings_and_formatting.py (str immutability, indexing).

Read this file top to bottom, predict each output, then run it:

    python lessons/02_text_and_numbers/03_unicode_text_and_bytes.py
"""

# Step 1: str is Unicode text. bytes is a sequence of integers from 0
# through 255 with no memory of which character encoding produced them.
# Encoding and decoding are therefore an explicit, two-sided agreement.
message = "café"
encoded = message.encode("utf-8")
decoded = encoded.decode("utf-8")

print("text:", message)
print("UTF-8 bytes:", encoded)
print("decoded:", decoded)
assert decoded == message

# Step 2: indexing a str returns a one-character str; indexing bytes
# instead returns an int (the byte's numeric value). Slicing bytes returns
# bytes.
print("\nstr index message[3]:", message[3], type(message[3]).__name__)
print("bytes index encoded[3]:", encoded[3], type(encoded[3]).__name__)
print("bytes slice encoded[3:5]:", encoded[3:5])
assert encoded[3] == 195  # first byte of the two-byte UTF-8 encoding of 'é'

# Step 3: bytes is immutable, just like str -- this is what makes bytes
# usable as a dict/set key. bytearray is the mutable counterpart: it
# supports item assignment and in-place methods such as extend().
mutable = bytearray(b"cat")
mutable[0] = ord("h")  # ord() maps a one-character string to its code point
mutable.extend(b"!")
print("\nmutated bytearray:", mutable)
assert mutable == bytearray(b"hat!")

# bytes itself refuses item assignment. The commented expression below would
# raise TypeError, so the runnable lesson leaves it disabled until exception
# handling is taught later:
#
# encoded[0] = ord("C")

# Step 4: decoding is not a generic bytes-to-text cast. A byte sequence that
# does not match the chosen encoding's rules raises UnicodeDecodeError. This
# expression is also documentation rather than executable code for now:
#
# b"\xff".decode("utf-8")

# Step 5: bytearray can also be built from a str given an explicit encoding,
# and converted back to immutable bytes when mutation is no longer needed.
buffer = bytearray("hello".encode("ascii"))
buffer[0] = ord("H")
frozen = bytes(buffer)
print("\nfrozen bytes:", frozen)
assert frozen == b"Hello"

# --- One-variable experiment -------------------------------------------
# Change `message` in Step 1 to "naïve résumé" and predict how many bytes
# `encoded` will contain before rerunning -- count is not the same as the
# number of characters once accented letters are UTF-8 encoded.
