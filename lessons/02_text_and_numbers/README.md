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

## 🧩 Progressive syntax and mechanism

1. **Arithmetic and precedence.** `+ - * / // % **`; `/` is true division
   and returns a float even for integer operands; `//` floors toward
   negative infinity; `**` is right-associative. Parentheses always win.
2. **Comparisons and boolean logic, in full.** Chained comparisons
   (`0 <= age < 130`); `and`/`or` short-circuit and return whichever operand
   decided the result, not necessarily `True`/`False`.
3. **Floating-point approximation.** `0.1 + 0.2 != 0.3` because binary
   floating point cannot represent every decimal fraction exactly.
4. **String immutability, indexing, and slicing.** Zero-based indices,
   negative indices from the end, half-open slices (`stop` excluded).
   Methods such as `.strip()`, `.upper()`, and `.replace()`
   always return a new string.
5. **f-string formatting.** `{value:.2f}` (fixed precision), `{value:>8}` /
   `{value:<8}` / `{value:^8}` (alignment), `{value:,}` (thousands
   separator).
6. **The text/binary boundary.** `str.encode(encoding)` produces `bytes`;
   `bytes.decode(encoding)` reverses it. Indexing a `str` returns a
   one-character `str`; indexing `bytes` returns an `int`. `bytearray` is
   the basic mutable counterpart to immutable `bytes` (deeper buffer-level
   tools such as `memoryview` are out of scope here).
7. **Numeric representations.** `float` (fast, approximate), `Decimal`
   (configurable decimal arithmetic, still requires an explicit rounding
   rule), `Fraction` (exact rational values), `complex` (real + imaginary,
   no natural ordering). Lesson 4 previews `import` as a bounded,
   just-in-time tool to reach these standard-library types; full import
   mechanics are taught in the Modules and Files chapter.

## 📖 Read-predict-run-modify workflow

Work through the four lesson files in order, predicting each `print()`
before running:

```bash
python lessons/02_text_and_numbers/01_operators_and_expressions.py
python lessons/02_text_and_numbers/02_strings_and_formatting.py
python lessons/02_text_and_numbers/03_unicode_text_and_bytes.py
python lessons/02_text_and_numbers/04_numeric_representations.py
```

### Expected output highlights

- `01_operators_and_expressions.py`: `-10 // 3` prints `-4` (not `-3`), and
  `0.1 + 0.2 == 0.3` prints `False` even though both sides look equal.
- `02_strings_and_formatting.py`: `text unchanged:` reprints the original,
  untouched string even after several method calls were applied to it.
- `03_unicode_text_and_bytes.py`: `encoded[3]` prints an `int` (`195`), not
  a character. Invalid mutation and decoding expressions remain commented
  until exception handling is taught.
- `04_numeric_representations.py`: `Decimal from float equals Decimal from
  text: False` -- `Decimal(0.1)` and `Decimal("0.1")` are different values.

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
