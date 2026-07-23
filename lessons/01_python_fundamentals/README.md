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

## 🧩 Progressive syntax and mechanism

1. **Comments and statements.** `#` starts a comment; Python ignores the
   rest of that line. A statement is one instruction; the interpreter runs
   statements top to bottom.
2. **`print()`.** Prints its arguments, separated by a space by default (or
   by whatever string you pass as `sep=`), followed by a newline.
3. **Assignment and names.** `name = value` binds `name` to the object
   `value` produced by evaluating the right-hand side. Rebinding a name does
   not modify the object it previously pointed to.
4. **Core scalar types.** `int` (whole numbers), `float` (numbers with a
   fractional part), `str` (text), `bool` (`True`/`False`), and the single
   value `None` of type `NoneType`, meaning "no value here."
5. **Inspection.** `type(value)` reports the exact type; `isinstance(value,
   SomeType)` asks whether a value counts as that type, including through
   inheritance (a distinction that matters once the course reaches classes).
   Check the singleton `None` with the dedicated idiom `value is None`;
   Chapter 3 later generalizes `is` to object identity.
6. **Explicit conversion.** `int(text)`, `float(text)`, `str(value)`, and
   `bool(value)` are constructors used as converters. `int()`/`float()`
   require text that matches their numeric grammar, or they raise
   `ValueError`. `bool(value)` tests truthiness, not word content: every
   non-empty string, including `"False"`, is truthy.
7. **Comparisons (bounded preview).** `==`, `<`, `>`, `<=`, `>=` all produce
   a `bool`. Chapter 2, Text and Numbers, covers the complete operator set
   and its precedence; here they exist only to make truthiness concrete.
8. **`assert` as a self-check.** `assert condition` does nothing when
   `condition` is truthy and raises `AssertionError` otherwise. It is the
   simplest way a script can verify its own expectations.

## 📖 Read-predict-run-modify workflow

Work through the three lesson files in order. For each file:

1. **Read** the module docstring and every `Step` comment before running
   anything.
2. **Predict** what each `print()` call will output. Write the prediction
   down, even briefly.
3. **Run** the file and compare the real output with your prediction:

   ```bash
   python lessons/01_python_fundamentals/01_running_python.py
   python lessons/01_python_fundamentals/02_values_names_and_types.py
   python lessons/01_python_fundamentals/03_conversion_and_truthiness.py
   ```

4. **Modify** one value (see the "One-variable experiment" comment near the
   bottom of lessons 2 and 3), rerun, and explain the new output before
   moving on.

### Expected output highlights

- `01_running_python.py` prints five lines, ending with an apostrophe inside
  a double-quoted string.
- `02_values_names_and_types.py` shows that `type(name)` reports `str` while
  `isinstance(age, str)` reports `False`, and that rebinding `greeting`
  leaves `original_greeting` at `"Hello"`.
- `03_conversion_and_truthiness.py` shows `bool('False') -> True`, followed
  by silent, passing `assert` statements (no output from a passing
  `assert`), and a comment describing -- without triggering -- a
  `ValueError`.

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
