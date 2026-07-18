# 🌱 Module 1: Basics

An introduction to the fundamental building blocks of Python. This module
has no prerequisites - it's the starting point for the whole course.

## 🎯 Learning objectives

After this module, you should be able to run a script, bind values to names,
recognize Python's core scalar types, convert input explicitly, choose a suitable
numeric representation, perform calculations, compare values, and cross the
boundary between Unicode text and encoded bytes.

## 🏷️ Values, objects, and names

Every Python value is an object with a type. Assignment binds a name to an
object; it does not declare a storage box with a permanent type:

```python
score = 10
score = "ten"  # Legal, although changing a name's meaning can confuse readers.
```

The common starting types are `int` (whole numbers), `float` (floating-point
numbers), `str` (text), `bool` (`True` or `False`), and `NoneType`, whose sole
value `None` represents the absence of a value. Use `type(value)` to inspect an
exact type and `isinstance(value, int)` to ask whether a value behaves as an
instance of a type.

Names are case-sensitive. Choose descriptive `snake_case` names, do not start
them with a digit, and avoid replacing built-ins such as `str`, `list`, or
`sum`.

Constructors such as `int("42")`, `float("3.5")`, and `str(42)` make conversions
explicit. Invalid numeric text raises `ValueError`. `bool(value)` tests
truthiness; it does not parse words, so `bool("False")` is `True` because the
string is non-empty.

## ➗ Operators and expressions

An expression produces a value. Arithmetic includes `+`, `-`, `*`, `/`,
floor division `//`, remainder `%`, and exponentiation `**`. `/` always
produces a float; `//` rounds down, which matters for negative numbers:

```python
7 / 2    # 3.5
7 // 2   # 3
-7 // 2  # -4
```

Comparisons produce booleans and can be chained (`0 <= age < 130`). Logical
operators combine conditions. `not` is evaluated before `and`, and `and`
before `or`; parentheses make mixed conditions clearer.

Floating-point numbers are approximations. For example, `0.1 + 0.2` may not
compare exactly equal to `0.3`; later programs can use `math.isclose()` for
approximate comparison.

Use the numeric type that matches the contract:

- `int` stores exact whole numbers;
- `float` is efficient binary floating point for measurements and approximate
  computation;
- `Decimal` provides configurable decimal arithmetic, but the application must
  still choose precision and rounding rules;
- `Fraction` stores exact rational values and can grow expensive as numerators
  and denominators grow;
- `complex` represents real and imaginary components and has no natural ordering.

Construct `Decimal` or `Fraction` from decimal text when that text is the source.
Passing a float instead preserves the float's existing binary approximation.

## 🔤 Strings

Strings are immutable sequences of Unicode characters. Indexing selects one
character; slicing selects a range and excludes the stop index:

```python
language = "Python"
language[0]     # "P"
language[1:4]   # "yth"
language[-1]    # "n"
```

Because strings are immutable, methods such as `.upper()` return new strings.
F-strings embed expressions in readable text: `f"{name} scored {score}"`.
Escape sequences such as `\n` represent special characters; raw strings
(`r"C:\new"`) suppress most escape processing.

## 🔡 Text and binary data

`str` stores Unicode text. `bytes` stores immutable integers from 0 through 255
and does not remember which character encoding produced them. Encoding and
decoding therefore require an explicit agreement:

```python
payload = "café".encode("utf-8")
text = payload.decode("utf-8")
```

Indexing a string returns a one-character string; indexing bytes returns an
integer. Use `bytearray` for mutable binary data. `memoryview` can expose a
buffer without copying it, but it also introduces a lifetime boundary: resizing
a mutable buffer while views export it is not allowed.

## 📚 Concepts covered

- **`01_hello_world.py`** - running a script and printing your first
  message with `print()`.
- **`02_variables_and_types.py`** - Python is dynamically typed: a
  variable's type is inferred from the value assigned to it (`int`,
  `float`, `str`, `bool`), and can be checked with `type()`.
- **`03_operators.py`** - arithmetic (`+ - * / // % **`), comparison
  (`== != < > <= >=`) and logical (`and or not`) operators.
- **`04_strings.py`** - strings as sequences of characters: concatenation,
  f-strings, indexing/slicing and common string methods.
- **`05_text_and_binary_data.py`** - Unicode text versus encoded bytes,
  UTF-8 boundaries, immutable `bytes`, mutable `bytearray`, and zero-copy
  `memoryview` access.
- **`06_numeric_types_and_conversions.py`** - explicit conversions, float
  approximation, `Decimal`, `Fraction`, and `complex`, including the accuracy
  and performance boundaries of each representation.

## ▶️ Running

```bash
python lessons/01_basics/01_hello_world.py
python lessons/01_basics/02_variables_and_types.py
python lessons/01_basics/03_operators.py
python lessons/01_basics/04_strings.py
python lessons/01_basics/05_text_and_binary_data.py
python lessons/01_basics/06_numeric_types_and_conversions.py
```

Once you've read through all six files, practice what you learned in
[`exercises/01_basics/`](../../exercises/01_basics/README.md).

Authoritative references:

- [Python built-in types](https://docs.python.org/3/library/stdtypes.html)
- [floating-point limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- [`decimal`](https://docs.python.org/3/library/decimal.html)
- [`fractions`](https://docs.python.org/3/library/fractions.html)

## ⚠️ Common mistakes

- Using `=` (assignment) when `==` (equality comparison) is intended.
- Combining text and numbers with `+` without conversion; prefer an f-string.
- Expecting `bool("False")` to parse the word as a false value.
- Treating text and bytes as interchangeable or relying on an implicit encoding.
- Constructing `Decimal("0.1")` indirectly through `Decimal(0.1)`.
- Accessing an index outside `0` through `len(value) - 1`.
- Assuming a string method changes the original string.
- Naming a variable `type`, `str`, or `print`, hiding the built-in function.

## ❓ Review questions

1. What is the difference between a name, a value, and a type?
2. How do `/`, `//`, and `%` differ?
3. Why does `text.upper()` not modify `text`?
4. What characters does the slice `value[1:4]` select?
5. When is `None` more appropriate than an empty string or zero?
6. Why does `bool("False")` evaluate to `True`?
7. Why must bytes be decoded before they become text?
8. When would `Decimal` or `Fraction` be a better contract than `float`?
9. What prevents a `bytearray` from being resized while a `memoryview` exposes
   its buffer?
