# 🔁 Chapter 4: Flow and Iteration

**Semantic ID:** `module.flow-and-iteration` · **Prerequisites:**
`module.collections`

## 📍 Where this fits

Chapter 3 built and inspected collections by index, slice, and membership,
but never visited every element automatically. This chapter closes that
gap: full `if`/`elif`/`else` statements, `for`/`while` loops, iteration
helpers (`range`, `enumerate`, `zip`), loop control (`break`/`continue`/loop
`else`), accumulator patterns, and comprehensions derived directly from
equivalent loops. This chapter still does not introduce learner-defined
functions -- that is Chapter 5.

## 🎯 Learning objectives

After this chapter, you should be able to:

- write and trace a multi-branch `if`/`elif`/`else` statement, including
  nested conditionals;
- write a `for` loop over a `range`, a list, or another iterable, and a
  `while` loop that terminates;
- use `enumerate()` to pair elements with indices and `zip()` to walk
  several iterables together;
- use `break`, `continue`, and a loop's `else` clause correctly, and explain
  what the `else` clause actually means;
- build a running total, a running search result, a frequency count, and a
  grouping dictionary with a loop;
- explain why `Counter` and `defaultdict` exist by comparing them to the
  hand-built loop versions of the same task;
- translate a loop into an equivalent list, set, or dict comprehension, and
  vice versa.

## 🧠 Motivation and mental model

Programs become useful once they can repeat work without repeating source
code. A loop expresses "do this once per element" or "do this until a
condition changes," instead of writing out each repetition by hand. Every
comprehension in this chapter is deliberately introduced only *after* its
equivalent loop, side by side -- a comprehension is not new behavior, it is
a more concise way to write a pattern you can already read as a loop.

The accumulator pattern -- start with an initial value before the loop,
then update it once per pass -- is the single idea underneath running
totals, running maximums, frequency counts, and grouping dictionaries. Once
you can recognize "what is the initial value, and what happens each pass?"
for one of these, you can recognize it for all of them.

## 📖 How to study this chapter

Control flow is easiest to learn by tracing. For every fragment below, write
down:

1. the value of the condition or next iterable element;
2. the indented block Python enters;
3. the names changed during that pass;
4. the output produced before execution continues.

Then run the linked companion and compare its trace with yours. This chapter
keeps all logic at script level; Chapter 5 is where repeated logic first moves
into learner-defined functions.

## 1️⃣ Conditions and truthiness

An `if` statement chooses which block of statements to execute. A colon starts
the block, and consistent indentation marks which statements belong to it:

```python
temperature = 22

if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("It's a pleasant day.")
elif temperature > 10:
    print("It's a bit chilly.")
else:
    print("It's cold outside!")
```

Python tests branches from top to bottom:

1. `temperature > 30` is `False`;
2. `temperature > 20` is `True`, so that block prints;
3. the remaining branches are skipped.

Exactly one branch runs, producing:

```text
It's a pleasant day.
```

Order matters. A broad condition placed before a more specific one can make
the specific branch unreachable.

### Any value can act as a condition

An `if` does not require an expression already typed as `bool`. Python applies
the truthiness rules learned in Chapter 1:

```python
pending_tasks = []

if pending_tasks:
    print("There is work to do.")
else:
    print("Nothing pending.")

pending_tasks.append("write report")

if pending_tasks:
    print("There is work to do.")
```

```text
Nothing pending.
There is work to do.
```

Empty strings, empty collections, numeric zero, and `None` are falsy.
Non-empty collections are truthy. This makes an emptiness check readable
without writing `len(pending_tasks) > 0`.

### Membership and boolean operators compose conditions

`in` tests membership and can be combined with `and`, `or`, `not`, and chained
comparisons:

```python
allowed_roles = {"admin", "editor"}
current_role = "editor"
age = 25
has_ticket = True

if current_role in allowed_roles and 18 <= age < 65 and has_ticket:
    print(f"{current_role!r} has standard admission.")
```

Every part is truthy, so the output is:

```text
'editor' has standard admission.
```

The `!r` conversion in the f-string asks for the representation of the value,
which includes the quotes around this string. Boolean short-circuiting still
applies: as soon as one part of the `and` chain is falsy, later parts need not
be evaluated.

### Nested decisions refine an already chosen path

```python
account_balance = 120
requested_amount = 50
is_frozen = False

if is_frozen:
    print("Account is frozen.")
else:
    if requested_amount <= account_balance:
        print("Withdrawal approved.")
    else:
        print("Insufficient funds.")
```

Trace the outer branch first, then the inner branch. Here `is_frozen` is
`False`, so Python enters the outer `else`; `50 <= 120` is `True`, so it prints
`Withdrawal approved.`.

Run the complete companion:

```bash
python lessons/04_control_flow/01_conditions_and_truthiness.py
```

See
[`01_conditions_and_truthiness.py`](01_conditions_and_truthiness.py)
for the full five-step branch trace.

> **Try one change:** set `requested_amount = 200`. Predict the outer branch
> and then the inner branch before rerunning.

## 2️⃣ Loops and iteration control

A loop repeats an indented block. A `for` loop takes values from an
**iterable**; a `while` loop repeats while a condition stays truthy.

### `for` consumes one element per pass

```python
for number in range(1, 6):
    print(number)

fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

`range(1, 6)` produces `1`, `2`, `3`, `4`, and `5`; as with slicing, the stop
value is excluded. On each pass Python binds the loop name to the next value,
runs the body, and then requests another value.

The second loop does not need numeric indices. It receives each list element
directly:

```text
apple
banana
cherry
```

### `while` must make progress

```python
countdown = 3

while countdown > 0:
    print(countdown)
    countdown -= 1

print("Liftoff!")
```

```text
3
2
1
Liftoff!
```

After each pass, `countdown -= 1` moves the condition toward `False`. Without
that progress, the loop would continue indefinitely unless a `break` ended it.

### `enumerate` and `zip` align related values

`enumerate(iterable)` pairs each element with an index:

```python
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

```text
0: apple
1: banana
2: cherry
```

`zip(a, b)` pairs elements at matching positions:

```python
prices = [1.20, 0.55, 2.10]

for fruit, price in zip(fruits, prices):
    print(f"{fruit}: {price:.2f}")
```

```text
apple: 1.20
banana: 0.55
cherry: 2.10
```

`zip` stops when the shortest input is exhausted. It does not require equal
lengths and does not warn about discarded extra values.

### `break`, `continue`, and loop `else`

`break` exits the nearest loop immediately. `continue` skips the rest of the
current pass and requests the next value:

```python
for number in range(1, 10):
    if number == 7:
        break
    if number % 2 == 0:
        continue
    print(number)
```

The loop prints `1`, `3`, and `5`. It skips even values and exits before
printing `7`.

A loop can have an `else` block. It runs only when iteration completes without
`break`:

```python
target = "pear"

for fruit in fruits:
    if fruit == target:
        print("Found:", target)
        break
else:
    print("Not found:", target)
```

`"pear"` never matches, so no `break` occurs and the output is
`Not found: pear`. Loop `else` does **not** mean the iterable was empty; it
means the loop did not exit through `break`.

### A basic accumulator remembers work across passes

An accumulator starts with an explicit value before the loop and updates once
per pass:

```python
readings = [12, 45, 7, 68, 23]
total = 0
highest = readings[0]

for reading in readings:
    total += reading
    if reading > highest:
        highest = reading

print(total)
print(highest)
```

The results are `155` and `68`. The next section applies this same shape to
dictionaries.

Run the complete companion:

```bash
python lessons/04_control_flow/02_loops_and_iteration_control.py
```

See
[`02_loops_and_iteration_control.py`](02_loops_and_iteration_control.py)
for every helper and control statement in one trace.

> **Try one change:** set `target = "banana"`. Predict where `break` occurs
> and whether the loop's `else` block still runs.

## 3️⃣ Accumulators and specialized collections

Many programs reduce a stream of values to a result. The accumulator may be a
number, but it can also be a dictionary that remembers counts or groups.

### Counting frequencies by hand

```python
words = ["fox", "dog", "fox", "cat", "dog", "fox"]
manual_counts = {}

for word in words:
    manual_counts[word] = manual_counts.get(word, 0) + 1

print(manual_counts)
```

```text
{'fox': 3, 'dog': 2, 'cat': 1}
```

Trace one pass at a time:

1. `.get(word, 0)` returns zero for a new word or its current count;
2. `+ 1` computes the next count;
3. bracket assignment stores that count under the word.

The initial accumulator is `{}`; each pass updates one key.

### Grouping values by a derived key

```python
animals = ["fox", "dog", "cat", "ferret", "camel", "capybara"]
groups = {}

for animal in animals:
    first_letter = animal[0]
    groups.setdefault(first_letter, []).append(animal)

print(groups)
```

```text
{'f': ['fox', 'ferret'], 'd': ['dog'], 'c': ['cat', 'camel', 'capybara']}
```

`setdefault(key, [])` returns the existing list when the key is present. For a
new key, it inserts and returns a new empty list. `.append(animal)` then
mutates whichever list was returned.

### `Counter` and `defaultdict` encode the same patterns

The standard library provides specialized dictionary types. This is the same
bounded import preview used in Chapter 2; Chapter 6 explains imports:

```python
from collections import Counter, defaultdict
```

`Counter` expresses frequency counting directly:

```python
counter_counts = Counter(words)
print(counter_counts)
print(counter_counts.most_common(2))
```

```text
Counter({'fox': 3, 'dog': 2, 'cat': 1})
[('fox', 3), ('dog', 2)]
```

It does not introduce different counting behavior; it packages the manual
accumulator and adds operations such as `.most_common()`.

`defaultdict(list)` calls `list()` to create an empty list when a missing key
is accessed:

```python
default_groups = defaultdict(list)

for animal in animals:
    default_groups[animal[0]].append(animal)

print(dict(default_groups))
```

The result equals the manual `groups` dict. Converting to plain `dict` makes
that equivalence visible in the output.

Run the complete companion:

```bash
python lessons/04_control_flow/03_accumulators_and_specialized_collections.py
```

See
[`03_accumulators_and_specialized_collections.py`](03_accumulators_and_specialized_collections.py)
for executable equality assertions between both manual and specialized forms.

> **Try one change:** add one more `"cat"` to `words`. Predict
> `counter_counts.most_common(2)` before rerunning; equal counts preserve
> first-seen order.

## 4️⃣ Comprehensions

A comprehension is a compact expression for a collection-building loop. It
should not hide a mechanism you cannot already write explicitly.

### Derive a list comprehension from its loop

Start with a loop that appends one transformed value per pass:

```python
numbers = range(1, 6)
squares_loop = []

for number in numbers:
    squares_loop.append(number**2)
```

Move the appended expression to the front and the loop clause after it:

```python
squares_comprehension = [number**2 for number in numbers]
```

Both forms produce `[1, 4, 9, 16, 25]`. The general shape is:

```python
[expression for name in iterable]
```

### A trailing `if` filters inputs

```python
even_squares_loop = []
for number in numbers:
    if number % 2 == 0:
        even_squares_loop.append(number**2)

even_squares = [number**2 for number in numbers if number % 2 == 0]
```

Both results are `[4, 16]`. The trailing condition decides whether an input is
included; the leading expression decides what value is collected.

### Dict and set comprehensions change the brackets and result shape

```python
square_lookup = {number: number**2 for number in numbers}
remainders = {number % 3 for number in numbers}

print(square_lookup)
print(sorted(remainders))
```

```text
{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
[0, 1, 2]
```

A dict comprehension uses `key: value`; a set comprehension uses one
expression and collapses duplicates.

### Nested comprehensions follow nested-loop order

```python
matrix = [[1, 2, 3], [4, 5, 6]]

flattened_loop = []
for row in matrix:
    for value in row:
        flattened_loop.append(value)

flattened = [value for row in matrix for value in row]
```

Read the comprehension's `for` clauses in the same order as the loops: the
leftmost clause is outermost. Both forms produce `[1, 2, 3, 4, 5, 6]`.

### Generator expressions compute lazily

Removing the list brackets gives a generator expression:

```python
sum_of_squares = sum(number**2 for number in numbers)
print(sum_of_squares)
```

The result is `55`. Values are supplied to `sum` on demand rather than first
being stored in a complete list. This chapter uses generator expressions only
in this simple consume-once form.

Run the complete companion:

```bash
python lessons/04_control_flow/04_comprehensions.py
```

See [`04_comprehensions.py`](04_comprehensions.py) for loop and comprehension
pairs whose results are checked with `assert`.

> **Try one change:** change the filter from `number % 2 == 0` to
> `number % 2 != 0`. Predict the new comprehension result before rerunning.

## 🔁 Transition to Chapter 5

This chapter repeated logic with loops, but every accumulator lived at the
top level of a script -- reusing it in a different script meant copying it.
Chapter 5, Function Contracts and Scope, packages logic like this behind a
name and a call contract, so it can be reused, tested, and composed.

## ⚠️ Common mistakes

- Writing a `while` loop whose condition never becomes false, producing an
  infinite loop.
- Assuming a loop's `else` clause means "the iterable was empty" -- it
  means "no `break` occurred."
- Reading `zip(a, b)` as requiring equal-length inputs; it silently stops
  at the shorter one.
- Writing `dict[key] += 1` for a brand-new key, which raises `KeyError`
  instead of the intended `dict.get(key, 0) + 1` or `defaultdict` pattern.
- Writing a comprehension before being able to say its equivalent loop out
  loud; if the comprehension does not obviously match a loop, it is
  probably too complex to be a comprehension.

## 🧾 Summary

- `if`/`elif`/`else` chooses one branch by testing conditions in order.
- `for`, `while`, `range`, `enumerate`, and `zip` cover the loop mechanisms
  used throughout the rest of this course.
- `break`, `continue`, and loop `else` give fine control over a loop's
  early exit and post-loop logic.
- Accumulator patterns generalize to frequency counts and grouping, which
  `Counter` and `defaultdict` express more concisely.
- Every comprehension in this chapter is a direct, verifiable rewrite of an
  equivalent loop.

## ❓ Review questions (closed notes)

1. In what order does Python test the branches of an `if`/`elif`/`else`
   chain, and how many branches can run?
2. What does a loop's `else` clause actually mean?
3. What happens if `zip(a, b)` is given a 3-element list and a 5-element
   list?
4. What is the accumulator pattern, and what two things do you need to
   identify before writing one?
5. What does `defaultdict(list)` do differently from a plain `dict` when a
   missing key is looked up?
6. Given a comprehension you cannot immediately explain, what should you
   write first to understand it?

## 📚 Authoritative references

- [The `if` statement](https://docs.python.org/3/reference/compound_stmts.html#the-if-statement)
- [The `for` statement](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement) ·
  [The `while` statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement)
- [Built-in Functions: `range`, `enumerate`, `zip`](https://docs.python.org/3/library/functions.html)
- [`break` and `continue` statements, and `else` clauses on loops](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops)
- [`collections.Counter`](https://docs.python.org/3/library/collections.html#collections.Counter) ·
  [`collections.defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
- [List/set/dict comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/04_control_flow/`](../../exercises/04_control_flow/README.md).
