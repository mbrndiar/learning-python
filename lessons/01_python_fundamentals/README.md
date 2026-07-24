# 🌱 Chapter 1: Python Fundamentals

**Semantic ID:** `module.python-fundamentals` · **Prerequisites:** none —
this is the starting point for the whole course.

## 📍 Where this fits

This chapter is the entry point. It has no prerequisites, and every later
chapter assumes its vocabulary: running a script, naming a value, and
reading `bool`/`None` and simple comparisons. If you have never run a Python
program before, start here; if you already know these mechanics from another
language, skim the lessons and focus on the Python-specific wording (for
example, that assignment binds a name rather than declaring a typed
variable).

## 🎯 Learning objectives

After this chapter, you should be able to:

- run a Python script from the command line and read its printed output;
- explain the difference between a name, the object it is bound to, and that
  object's type;
- recognize the core scalar types (`int`, `float`, `str`, `bool`,
  `NoneType`) and inspect them with `type()` and `isinstance()`;
- convert explicitly between `int`, `float`, `str`, and `bool`, and explain
  why `bool("False")` is `True`;
- write a comparison expression and predict its `bool` result;
- use `assert` as a simple, local self-check.

## 🧠 Motivation and mental model

A computer only does what a program tells it to, one instruction at a time.
Python source files are that program: plain text files the `python`
interpreter reads from top to bottom and executes. Nothing happens by magic
or in parallel yet -- every example in this chapter runs in exactly the
order it is written.

The second idea worth building correctly from day one is that Python names
are labels, not boxes. In many languages a variable declaration reserves a
typed slot of memory. Python instead creates an object (say, the integer
`25`) and then *binds a name* to it (`age = 25`). The name can later be
rebound to a completely different kind of object; the type lives on the
object, not on the name. Getting this mental model right now prevents
confusion later, when several names can refer to the very same object (a
topic Chapter 3, Collections, depends on).

## 📖 How to study this chapter

Each section below is a small reading lesson followed by a runnable companion.
Read the explanation and predict the shown output first. Then run the linked
file from the repository root and compare the real output with your prediction.
Finally, make the suggested one-value change and rerun. This
**read-predict-run-modify** loop turns syntax you recognize into behavior you
can explain.

## 1️⃣ Running scripts, comments, and `print()`

A Python source file is a plain text file, conventionally ending in `.py`. The
command

```bash
python lessons/01_python_fundamentals/01_running_python.py
```

starts the Python interpreter and gives it the path to a source file. For the
simple scripts in this chapter, the interpreter reads the file from top to
bottom and executes each statement once in source order.

### Statements and comments

A **statement** is an instruction Python can execute. A call to `print()` is
one kind of statement:

```python
# Python ignores this comment.
print("Hello, World!")
print("Learning", "Python", "starts", "here.")
print("2026", "07", "23", sep="-")
```

The `#` character starts a comment. Python ignores everything from `#` to the
end of that line, so comments can explain intent without changing the
program's behavior.

`print(...)` calls Python's built-in `print` function:

1. Text between matching quotes creates a string value.
2. Commas separate the values passed to `print`.
3. By default, `print` puts one space between multiple values and a newline
   after them.
4. The optional `sep="-"` argument changes the separator for that call only.

The fragment therefore prints:

```text
Hello, World!
Learning Python starts here.
2026-07-23
```

Single and double quotes both delimit strings. Choose the form that keeps the
text readable; double quotes make an apostrophe straightforward:

```python
print("A string can contain an apostrophe, like Ada's notebook.")
```

The complete runnable companion is
[`01_running_python.py`](01_running_python.py). It prints five lines and needs
no hidden entry point or setup.

> **Try one change:** replace `sep="-"` with `sep="/"`. Predict which line
> changes and which lines stay identical, then rerun the file.

## 2️⃣ Values, names, assignment, and types

Printing literal text is useful, but programs also need to remember values.
Python separates three ideas:

- an **object** is a value that exists while the program runs;
- a **name** is a label bound to an object;
- a **type** describes what kind of object it is and what operations it
  supports.

Assignment uses one equals sign:

```python
age = 25
height = 1.75
name = "Ada"
is_learning = True
favorite_color = None
```

Python first evaluates the expression on the right of `=`, producing an
object, and then binds the name on the left to that object. It does not declare
`age` as a permanently integer-shaped storage box. The type belongs to the
object, not to the name.

These are the core scalar values used throughout the first chapters:

| Type | Example literal | Meaning |
| --- | --- | --- |
| `int` | `25` | a whole number |
| `float` | `1.75` | an approximate number with a fractional part |
| `str` | `"Ada"` | Unicode text |
| `bool` | `True`, `False` | a truth value |
| `NoneType` | `None` | the single value meaning "no value here" |

`True`, `False`, and `None` are spelled exactly as shown, including the capital
letter. They are Python values, not quoted text.

### Inspecting a value

Use `type(value)` when you need the exact type and
`isinstance(value, SomeType)` when you need to ask whether the value counts as
a given type:

```python
print(type(age))
print(isinstance(age, int))
print(isinstance(age, str))
print("favorite_color:", favorite_color)
print(favorite_color is None)
```

The output is:

```text
<class 'int'>
True
False
favorite_color: None
True
```

`favorite_color is None` is the dedicated idiom for checking the singleton
`None` value. The broader meaning of object identity is deferred until the
course has introduced collections.

### Rebinding changes one name

A name can later be rebound to another object:

```python
original_greeting = "Hello"
greeting = original_greeting
greeting = "Hi"

print(greeting)
print(original_greeting)
```

This prints:

```text
Hi
Hello
```

After the second assignment, both names refer to the same `"Hello"` string.
The third assignment rebinds only `greeting` to a new `"Hi"` object. It does
not edit `"Hello"` and does not move `original_greeting`.

Names are case-sensitive, cannot start with a digit, and conventionally use
`snake_case`. Avoid names such as `print`, `str`, or `type`, because assigning
to one would hide the built-in operation with that name.

The complete runnable companion is
[`02_values_names_and_types.py`](02_values_names_and_types.py). It also shows
the intentionally surprising fact that `True + True` evaluates to `2`; write
`True` and `False` for yes/no meaning rather than relying on that numeric
compatibility.

> **Try one change:** change `favorite_color = None` to
> `favorite_color = "blue"`. Predict the two lines that report
> `favorite_color` before rerunning.

## 3️⃣ Explicit conversion, comparisons, and truthiness

Python does not automatically treat numeric text as a number. If a program
receives `"42"`, that value is still a `str` until the program explicitly asks
for a conversion:

```python
whole_number = int("42")
measurement = float("3.5")
label = str(123)
truncated = int(-3.9)

print(whole_number)
print(measurement)
print(label)
print(truncated)
```

The type names here are being called as **constructors**. Each creates a value
of its type from the supplied argument:

```text
42
3.5
123
-3
```

Although `123` and `"123"` look alike when printed, the first is an `int` and
the converted result is a `str`. Also notice that `int(-3.9)` truncates toward
zero; it does not round to the nearest whole number.

Conversion has a contract. The text must match the constructor's grammar:
`int("42")` works, but `int("3.5")` and `int("not-a-number")` raise
`ValueError`. Unhandled errors stop a script. Catching errors with
`try`/`except` comes later, so the runnable lesson documents this boundary
without deliberately crashing.

### Truthiness is not word parsing

`bool(value)` asks whether a value is **truthy**. It does not read text and
interpret English words:

```python
print(bool("False"))
print(bool(""))
print(bool(0))
print(bool(1))
print(bool(None))
```

This prints:

```text
True
False
False
True
False
```

Every non-empty string is truthy, even `"False"` or `"0"`. An empty string,
zero, and `None` are falsy. Later chapters add collections to this model;
empty collections are falsy too.

### Comparisons produce `bool`

Comparison operators such as `==`, `<`, `>`, `<=`, and `>=` evaluate to a
`bool`:

```python
age = 20
is_adult = age >= 18

print(is_adult)
print(type(is_adult))
```

The result is the value `True` of type `bool`. Chapter 2 gives operators and
precedence their full treatment; this bounded preview is enough to make a
self-check meaningful.

### `assert` records an expectation

`assert condition` evaluates its condition:

- if the condition is truthy, execution continues with no output;
- if it is falsy, Python raises `AssertionError` and stops the script.

```python
assert whole_number == 42
assert measurement == 3.5
assert is_adult, "expected the sample age to represent an adult"
```

All three assertions pass silently. That silence is success, not evidence that
Python skipped them. Use `assert` here for small executable expectations, not
for validating untrusted user input.

The complete runnable companion is
[`03_conversion_and_truthiness.py`](03_conversion_and_truthiness.py).

> **Try one change:** change `age = 20` to `age = 15`. Before running, predict
> both the value and the type of `is_adult`. The value changes; the type does
> not.

## 🔁 Transition to Chapter 2

This chapter treated arithmetic and comparisons as a small preview needed
for truthiness. Chapter 2, Text and Numbers, returns to operators as its
main subject: full precedence rules, the difference between `/` and `//`,
string slicing and formatting, and the boundary between `str` and `bytes`.

## ⚠️ Common mistakes

- Using `=` (assignment) where `==` (comparison) was intended.
- Believing `bool("False")` is `False` because of the word inside the
  string -- truthiness only checks whether the string is empty.
- Expecting `int("3.5")` to work like `float("3.5")`; `int()`'s grammar does
  not accept a decimal point.
- Assuming rebinding a name changes every other name that previously pointed
  to the same object -- it does not; only mutation would, and nothing in
  this chapter mutates anything.
- Renaming a variable to shadow a built-in, such as `type = "int"`, which
  hides that built-in for the rest of the file.

## 🧾 Summary

- A Python program is a sequence of statements executed top to bottom.
- Names are bound to objects; the object carries the type, not the name.
- `int`, `float`, `str`, `bool`, and `None` are the starting vocabulary for
  values.
- `type()` and `isinstance()` inspect an object; conversions such as
  `int(text)` and `bool(value)` must be requested explicitly and can fail
  or surprise you if you assume they parse meaning rather than test types.
- `assert` gives a script a small, immediate way to state and check its own
  expectations.

## ❓ Review questions (closed notes)

Answer these without looking back at the lesson files or this README.

1. What is the difference between a name, an object, and a type?
2. If `x = 5` and then `y = x` and then `x = 10`, what is `y`?
3. Why is `bool("False")` equal to `True`?
4. What error does `int("3.5")` raise, and why?
5. What does `assert condition` do when `condition` is `False`? When it is
   `True`?
6. Name one difference between `type(value)` and `isinstance(value, T)`.

## 📚 Authoritative references

- [The Python Tutorial: An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)
- [Built-in Types](https://docs.python.org/3/library/stdtypes.html)
- [Built-in Functions: `print`, `type`, `isinstance`, `bool`, `int`, `float`, `str`](https://docs.python.org/3/library/functions.html)
- [The `assert` statement](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement)

Once you can answer the review questions and have run all three lesson
files, continue to
[`exercises/01_python_fundamentals/`](../../exercises/01_python_fundamentals/README.md).
