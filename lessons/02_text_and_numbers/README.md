# 🔤 Chapter 2: Text and Numbers

**Semantic ID:** `module.text-and-numbers` · **Prerequisites:**
`module.python-fundamentals`

## 📍 Where this fits

Chapter 1 gave you names, core types, and a small preview of comparisons.
This chapter returns to expressions as its main subject: full operator
precedence, string manipulation and formatting, the text/binary boundary,
and the numeric types beyond plain `int`/`float`. Everything here still
avoids loops and user-defined collections as mechanisms -- those arrive in
Chapters 3 and 4.

## 🎯 Learning objectives

After this chapter, you should be able to:

- evaluate arithmetic, comparison, and boolean expressions and predict
  their result using Python's operator precedence;
- explain why `and`/`or` short-circuit and what they return with non-bool
  operands;
- index, slice, and format strings, and explain why string methods never
  modify their receiver;
- cross the boundary between `str` and `bytes` explicitly, with `encode`/
  `decode`, and use `bytearray` for basic mutable binary data;
- choose among `int`, `float`, `Decimal`, `Fraction`, and `complex` based on
  a problem's accuracy and interoperability requirements.

## 🧠 Motivation and mental model

An expression is anything Python can evaluate down to a value: `2 + 3`,
`"a" + "b"`, `x >= 18`. Operators compose small expressions into larger
ones, and precedence rules decide which operator "binds tighter" when
several appear together -- exactly like arithmetic order of operations in
math class, extended to comparisons and boolean logic.

Text and numbers look similar on screen but are fundamentally different
representations. A string is a sequence of Unicode *characters*; bytes are a
sequence of raw 0-255 integers with no memory of what encoding produced
them. Treating one as the other without an explicit `encode`/`decode` step
is a common source of bugs, which is why this chapter treats that boundary
as a first-class topic rather than a footnote.

## 📖 How to study this chapter

The four sections follow the same **read-predict-run-modify** loop as Chapter
1. Read one section, predict each fragment's result, and then run its linked
companion from the repository root. Make only the suggested one-value change
before rerunning; changing one assumption at a time makes cause and effect
visible.

## 1️⃣ Operators and expressions

An **expression** is code that Python evaluates to produce a value. A literal
such as `10` is an expression; so are `10 + 3`, `age >= 18`, and two smaller
expressions joined by `and`.

### Arithmetic operators

The basic numeric operators are:

| Operator | Meaning | Example result |
| --- | --- | --- |
| `+` | addition | `10 + 3` → `13` |
| `-` | subtraction | `10 - 3` → `7` |
| `*` | multiplication | `10 * 3` → `30` |
| `/` | true division | `10 / 3` → `3.3333333333333335` |
| `//` | floor division | `10 // 3` → `3` |
| `%` | remainder | `10 % 3` → `1` |
| `**` | exponentiation | `10 ** 3` → `1000` |

True division `/` returns a `float`, even when both operands are integers.
Floor division `//` rounds down toward negative infinity, not toward zero:

```python
print(10 / 3)
print(10 // 3)
print(-10 // 3)
print(-10 % 3)
```

This prints:

```text
3.3333333333333335
3
-4
2
```

The quotient and remainder still satisfy
`a == (a // b) * b + (a % b)`. For `-10` and `3`, that is
`-10 == (-4 * 3) + 2`.

### Precedence controls grouping

When several operators occur in one expression, precedence determines which
parts Python evaluates together. Exponentiation binds more tightly than
multiplication, which binds more tightly than addition. Parentheses override
the defaults:

```python
without_parentheses = 2 + 3 * 4
with_parentheses = (2 + 3) * 4
power = 2 ** 3 ** 2

print(without_parentheses)
print(with_parentheses)
print(power)
```

The results are `14`, `20`, and `512`. Exponentiation is right-associative, so
the final expression means `2 ** (3 ** 2)`, not `(2 ** 3) ** 2`. Parentheses
are worth adding whenever they make the intended grouping easier to read.

### Comparisons can be chained

Comparisons still produce `bool`, but Python can express a bounded range as
one chained comparison:

```python
age = 42
print(0 <= age < 130)
print(age == 42 and age != 41)
```

`0 <= age < 130` means the same condition as
`0 <= age and age < 130`, while evaluating the middle expression only once.
Both lines above print `True`.

### Boolean operators short-circuit

`not` inverts truthiness. `and` and `or` evaluate from left to right and stop
as soon as the result has been decided:

- `left and right` skips `right` when `left` is falsy;
- `left or right` skips `right` when `left` is truthy.

They return the operand that decided the result, not necessarily a `bool`:

```python
first_name = ""
fallback_name = "Guest"
chosen_name = first_name or fallback_name

print(chosen_name)
```

The empty string is falsy, so `or` must evaluate and return the second operand.
The output is `Guest`, a `str`, rather than `True`.

### A `float` is an approximation

Python's `float` uses binary floating-point representation. Many decimal
fractions have no finite binary representation, just as `1 / 3` has no finite
decimal representation:

```python
total = 0.1 + 0.2
print(total)
print(total == 0.3)
```

```text
0.30000000000000004
False
```

This is representation behavior, not a broken addition operator. The final
section introduces alternatives when exact decimal or rational arithmetic is
part of the problem's contract.

Run the complete companion:

```bash
python lessons/02_text_and_numbers/01_operators_and_expressions.py
```

See [`01_operators_and_expressions.py`](01_operators_and_expressions.py) for
the full sequence.

> **Try one change:** set `age = 130`, predict `0 <= age < 130`, and rerun.
> Then try `age = -1`. The strict upper bound excludes `130`; the lower bound
> excludes `-1`.

## 2️⃣ Strings, slicing, and formatting

A `str` is an immutable sequence of Unicode characters. **Immutable** means an
existing string cannot be edited in place. Concatenation and every string
method produce another string instead.

### Building text without changing its inputs

```python
greeting = "Hello"
name = "World"
message = greeting + ", " + name + "!"

print(message)
print(greeting)
```

The first line prints `Hello, World!`; the second still prints `Hello`.
Concatenation with `+` created `message` without changing either input.

Methods follow the same rule:

```python
text = "  Learning Python is Fun  "
print("|" + text.strip() + "|")
print(text.strip().upper())
print(text.strip().replace("Fun", "Awesome"))
print("|" + text + "|")
```

```text
|Learning Python is Fun|
LEARNING PYTHON IS FUN
Learning Python is Awesome
|  Learning Python is Fun  |
```

`text.strip()` creates a value without the surrounding whitespace. Calling
`.upper()` or `.replace()` creates further values. Because none is assigned
back to `text`, its final output still includes the original spaces.

### Indexing selects one character; slicing selects a range

Indices start at zero. Negative indices count backward from the end. A slice
uses `start:stop:step`, and the `stop` position is excluded:

```python
word = "Python"
print(word[0])
print(word[-1])
print(word[0:3])
print(word[::-1])
print(word[2:100])
```

```text
P
n
Pyt
nohtyP
thon
```

`word[0]` returns a one-character `str`. An invalid single index raises
`IndexError`, but a slice safely clamps an out-of-range boundary; that is why
`word[2:100]` returns the available suffix.

### f-strings combine values and formatting

Prefixing a string literal with `f` lets expressions appear inside `{}`:

```python
price = 19.5
label = "cm"

print(f"{price:.2f} {label}")
print(f"[{label:>8}]")
print(f"{1234567:,}")
```

```text
19.50 cm
[      cm]
1,234,567
```

The optional format specifier follows `:`:

- `.2f` uses fixed-point notation with two digits after the decimal point;
- `>8`, `<8`, and `^8` align a value right, left, or center in width 8;
- `,` adds a thousands separator.

Formatting changes presentation, not the stored value. In particular, `.2f`
rounds the displayed number; it does not truncate or rebind `price`.

Run the complete companion:

```bash
python lessons/02_text_and_numbers/02_strings_and_formatting.py
```

See [`02_strings_and_formatting.py`](02_strings_and_formatting.py) for all
method, slice, and alignment examples.

> **Try one change:** set `price = 19.987` and predict `{price:.2f}` before
> rerunning. The displayed result is `19.99`.

## 3️⃣ Unicode text and bytes

Text and binary data are different kinds of value:

- `str` represents Unicode characters such as `"café"`;
- `bytes` represents immutable integers from 0 through 255;
- an **encoding** defines how characters map to bytes.

Bytes do not remember which encoding created them. The producer and consumer
must therefore agree explicitly.

### Encoding and decoding form a round trip

```python
message = "café"
encoded = message.encode("utf-8")
decoded = encoded.decode("utf-8")

print(message)
print(encoded)
print(decoded)
assert decoded == message
```

```text
café
b'caf\xc3\xa9'
café
```

UTF-8 represents the first three characters with one byte each and `é` with
two bytes, `\xc3\xa9`. Encoding crosses from text to bytes; decoding with the
same agreed encoding crosses back. The passing assertion confirms the round
trip.

Using the wrong decoding rule is not a generic cast. It can produce corrupted
text or raise `UnicodeDecodeError`; exception handling is intentionally left
for a later chapter.

### Indexing exposes the representation difference

```python
print(message[3])
print(encoded[3])
print(encoded[3:5])
```

```text
é
195
b'\xc3\xa9'
```

Indexing `str` returns a one-character `str`. Indexing `bytes` returns the
selected byte as an `int`; slicing `bytes` returns another `bytes` value.
Therefore `encoded[3]` is `195`, the numeric value of the first byte in `é`'s
two-byte UTF-8 representation.

### Use `bytearray` when binary data must change

Like `str`, `bytes` is immutable. `bytearray` provides a mutable binary
sequence:

```python
mutable = bytearray(b"cat")
mutable[0] = ord("h")
mutable.extend(b"!")

print(mutable)
print(bytes(mutable))
```

```text
bytearray(b'hat!')
b'hat!'
```

The `b` prefix creates a bytes literal. `ord("h")` produces the integer code
point for the one-character string, which is valid for this ASCII byte.
`bytes(mutable)` freezes the current contents into an immutable value.

Run the complete companion:

```bash
python lessons/02_text_and_numbers/03_unicode_text_and_bytes.py
```

See [`03_unicode_text_and_bytes.py`](03_unicode_text_and_bytes.py) for the
round-trip assertions and a second mutation example.

> **Try one change:** replace `"café"` with `"naïve résumé"`. Predict how the
> printed UTF-8 bytes will differ from the visible text before rerunning;
> accented characters appear as multiple byte values.

## 4️⃣ Numeric representations and conversions

There is no universally best numeric type. Choose a representation whose
behavior matches the problem:

| Type | Representation | Good fit |
| --- | --- | --- |
| `int` | exact whole number | counts and integer identifiers |
| `float` | approximate binary floating point | measurements and scientific interoperability |
| `Decimal` | configurable decimal arithmetic | decimal rules such as monetary calculations |
| `Fraction` | exact numerator/denominator | ratios and exact rational arithmetic |
| `complex` | real and imaginary components | domains that naturally use complex numbers |

`Decimal` and `Fraction` live in Python's standard library rather than among
the automatically available built-ins. This lesson uses a bounded preview:

```python
import math
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
```

For now, read `import math` as "make the standard-library module available as
`math`" and `from decimal import Decimal` as "make this named tool available
directly." Chapter 6 teaches modules, packages, and import mechanics in full.

### Compare approximate and decimal arithmetic

Use `math.isclose` when two floating-point results should be compared within a
small tolerance:

```python
float_total = 0.1 + 0.2
print(float_total == 0.3)
print(math.isclose(float_total, 0.3))
```

The lines print `False` and `True`. This preserves `float`'s useful speed and
interoperability without pretending every stored value is exact.

When the input contract is decimal text, construct `Decimal` from that text:

```python
decimal_tenth = Decimal("0.1")
decimal_total = decimal_tenth + decimal_tenth + decimal_tenth
decimal_from_float = Decimal(0.1)

print(decimal_total)
print(decimal_from_float == decimal_tenth)
```

The output is `0.3` and `False`. `Decimal(0.1)` faithfully imports the already
approximate float value; it cannot recover the human-written decimal that
existed before the float was created.

`Decimal` does not choose a universal business rounding policy. The program
must state one:

```python
taxed_price = Decimal("19.99") * Decimal("1.20")
display_price = taxed_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print(display_price)
```

This prints `23.99` using the explicitly requested half-up rule.

### Exact ratios and complex values

`Fraction` stores an exact rational number:

```python
one_third = Fraction(1, 3)
total = one_third + one_third + one_third

print(total)
print(Fraction("0.1"))
print(Fraction(0.1) == Fraction(1, 10))
```

The results are `1`, `1/10`, and `False`. As with `Decimal`, constructing from
a float captures the float's approximation; integer parts or text preserve the
intended exact ratio.

Python writes the imaginary part of a complex literal with `j`:

```python
impedance = 3 + 4j
print(impedance)
print(abs(impedance))
```

This prints `(3+4j)` and `5.0`. Complex numbers support equality but have no
natural less-than ordering.

Run the complete companion:

```bash
python lessons/02_text_and_numbers/04_numeric_representations.py
```

See [`04_numeric_representations.py`](04_numeric_representations.py) for all
five representations and their executable assertions.

> **Try one change:** replace `Fraction(1, 3)` with `Fraction(1, 4)` and
> predict the sum of three copies before rerunning. It becomes exactly `3/4`.

## 🔁 Transition to Chapter 3

This chapter treated `str` and `bytes` as text/binary sequences accessed by
index and slice. Chapter 3, Collections, generalizes that idea to `list`,
`tuple`, `dict`, and `set`, and introduces the concept of *mutation shared
through aliasing* -- something plain numbers and immutable strings never
exposed.

## ⚠️ Common mistakes

- Forgetting that `/` always returns a float, even for two integers whose
  division is exact.
- Assuming `//` truncates toward zero like some other languages' integer
  division; Python's `//` floors.
- Comparing floats with `==` instead of `math.isclose()`.
- Assuming a string method mutates its receiver -- none of them do.
- Treating `str` and `bytes` as interchangeable, or decoding with the wrong
  encoding and getting mojibake or a `UnicodeDecodeError`.
- Constructing `Decimal(0.1)` when `Decimal("0.1")` was intended -- the
  first imports a float's binary approximation.

## 🧾 Summary

- Operator precedence and parentheses determine how a compound expression
  is evaluated; when uncertain, add parentheses.
- `and`/`or` short-circuit and can return either operand, not just `bool`.
- Strings are immutable; every transforming method returns a new string.
- `bytes`/`bytearray` model raw binary data; encoding and decoding are the
  only bridge to/from Unicode text.
- `int`, `float`, `Decimal`, `Fraction`, and `complex` make different
  accuracy and performance trade-offs -- pick the one that matches the
  problem's contract.

## ❓ Review questions (closed notes)

1. Why does `-7 // 2` equal `-4` and not `-3`?
2. What do `and` and `or` return when their operands are not already
   `bool`?
3. Why does `text.upper()` not change `text`?
4. What is the type of `some_bytes[0]`? Of `some_string[0]`?
5. Why must bytes be decoded before they can be treated as text?
6. When would `Decimal` or `Fraction` be a better contract than `float`?

## 📚 Authoritative references

- [Expressions: operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence)
- [`str` — text sequence type](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)
- [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)
- [Binary sequence types: `bytes`, `bytearray`](https://docs.python.org/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview)
- [Floating-point arithmetic: issues and limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- [`decimal`](https://docs.python.org/3/library/decimal.html) ·
  [`fractions`](https://docs.python.org/3/library/fractions.html)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/02_text_and_numbers/`](../../exercises/02_text_and_numbers/README.md).
