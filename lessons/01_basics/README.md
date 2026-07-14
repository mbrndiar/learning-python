# 🌱 Module 1: Basics

An introduction to the fundamental building blocks of Python. This module
has no prerequisites - it's the starting point for the whole course.

## 🎯 Learning objectives

After this module, you should be able to run a script, bind values to names,
recognize Python's core scalar types, perform calculations, compare values, and
transform text.

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

## ▶️ Running

```bash
python lessons/01_basics/01_hello_world.py
python lessons/01_basics/02_variables_and_types.py
python lessons/01_basics/03_operators.py
python lessons/01_basics/04_strings.py
```

Once you've read through all four files, practice what you learned in
[`exercises/01_basics/`](../../exercises/01_basics/README.md).

## ⚠️ Common mistakes

- Using `=` (assignment) when `==` (equality comparison) is intended.
- Combining text and numbers with `+` without conversion; prefer an f-string.
- Accessing an index outside `0` through `len(value) - 1`.
- Assuming a string method changes the original string.
- Naming a variable `type`, `str`, or `print`, hiding the built-in function.

## ❓ Review questions

1. What is the difference between a name, a value, and a type?
2. How do `/`, `//`, and `%` differ?
3. Why does `text.upper()` not modify `text`?
4. What characters does the slice `value[1:4]` select?
5. When is `None` more appropriate than an empty string or zero?
