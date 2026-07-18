"""
Lesson 1.5: Text and Binary Data

``str`` represents Unicode text, while ``bytes`` represents encoded data as
integer byte values. Encoding and decoding are explicit boundaries because a
byte sequence has no inherent character encoding. ``bytearray`` and
``memoryview`` are useful when binary data must be changed or accessed without
first making another copy.
"""

# Text must be encoded before it can be written to a binary protocol or file.
# UTF-8 is a common choice, but both sides must agree on the encoding.
message = "café ☕"
encoded = message.encode("utf-8")
decoded = encoded.decode("utf-8")

print("text:", message)
print("UTF-8 bytes:", encoded)
print("decoded:", decoded)
assert decoded == message

# A str index returns a one-character str. A bytes index instead returns an
# int from 0 through 255; slice when a bytes result is needed.
print("text index:", message[3], type(message[3]).__name__)
print("byte index:", encoded[3], type(encoded[3]).__name__)
print("byte slice:", encoded[3:5])
assert encoded[3] == 195
assert encoded[3:5] == b"\xc3\xa9"

# bytes is immutable. This makes bytes safe to share and usable as a mapping
# key, but changing an item requires a mutable bytearray or a new bytes object.
try:
    encoded[0] = ord("C")
except TypeError as error:
    print("bytes mutation:", type(error).__name__)

mutable = bytearray(b"cat")
mutable[0] = ord("h")
mutable.extend(b"!")
print("mutated bytearray:", mutable)
assert mutable == bytearray(b"hat!")

# Decoding is not a generic bytes-to-text cast. Invalid UTF-8 raises an error
# unless the program deliberately selects another error-handling policy.
try:
    b"\xff".decode("utf-8")
except UnicodeDecodeError as error:
    print("invalid UTF-8:", type(error).__name__)

# memoryview exposes an object that supports the buffer protocol without first
# copying its data. A slice is still a view, so this write reaches the original
# bytearray. Writability follows the underlying object: a view of bytes is
# read-only, and memoryview does not encode or decode text.
buffer = bytearray(b"ABCDE")
view = memoryview(buffer)
window = view[1:4]
window[0] = ord("x")
read_only_view = memoryview(b"ABC")

print("buffer through view:", buffer)
print("views are read-only:", view.readonly, read_only_view.readonly)
assert buffer == bytearray(b"AxCDE")
assert view.readonly is False
assert read_only_view.readonly is True

# A bytearray cannot be resized while a view exports its buffer. Release all
# related views when finished; this is a scope/lifetime boundary, not just a
# faster spelling of ordinary slicing.
try:
    buffer.append(ord("F"))
except BufferError as error:
    print("resize while viewed:", type(error).__name__)

window.release()
view.release()
read_only_view.release()
buffer.append(ord("F"))
assert buffer == bytearray(b"AxCDEF")
