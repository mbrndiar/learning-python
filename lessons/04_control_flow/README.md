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

## 🧩 Progressive syntax and mechanism

1. **Full conditionals.** `if`/`elif`/`else` as a statement (not just the
   Chapter 1 conditional-expression preview); branches are tested top to
   bottom, and only the first true one runs. Falsy values include `0`,
   `""`, and empty collections.
2. **`for` and `while`.** `for name in iterable:` visits each element once;
   `while condition:` repeats until `condition` becomes falsy -- the body
   must make progress toward that, or an intentional `break` must exit it.
3. **`range`, `enumerate`, `zip`.** `range(start, stop)` generates integers
   with `stop` excluded; `enumerate(iterable)` pairs each element with its
   index; `zip(a, b)` pairs elements from two iterables, stopping at the
   shorter one.
4. **Loop control.** `break` exits the nearest loop immediately; `continue`
   skips only the rest of the current pass. A loop's `else` block runs only
   if the loop completed without `break` -- the classic "search, and report
   not-found only if nothing matched" pattern.
5. **Accumulator patterns.** Running total/maximum with `+=`/comparison
   inside a loop; frequency counting with `dict.get(key, 0) + 1`; grouping
   with `dict.setdefault(key, []).append(value)`.
6. **Specialized collections.** `collections.Counter` replaces manual
   frequency counting; `collections.defaultdict(factory)` replaces
   `setdefault` by calling `factory` automatically for a missing key.
7. **Comprehensions.** `[expr for name in iterable]`,
   `{expr for name in iterable}`, `{key: value for name in iterable}`, each
   introduced as a direct rewrite of an equivalent loop; `if condition`
   after `for` filters; a nested comprehension mirrors a nested loop, outer
   `for` first.

## 📖 Read-predict-run-modify workflow

Work through the four lesson files in order, predicting each `print()`
before running:

```bash
python lessons/04_control_flow/01_conditions_and_truthiness.py
python lessons/04_control_flow/02_loops_and_iteration_control.py
python lessons/04_control_flow/03_accumulators_and_specialized_collections.py
python lessons/04_control_flow/04_comprehensions.py
```

### Expected output highlights

- `01_conditions_and_truthiness.py`: an empty list prints `"Nothing
  pending."`; after one append, the same condition prints `"There is work
  to do."`.
- `02_loops_and_iteration_control.py`: the fruit search for `"pear"` prints
  `"Not found: pear"` from the loop's `else` clause, because the loop never
  hit `break`.
- `03_accumulators_and_specialized_collections.py`: `manual_counts` and
  `dict(counter_counts)` are asserted equal -- `Counter` is a shortcut, not
  different behavior.
- `04_comprehensions.py`: every `*_loop` result is asserted equal to its
  `*_comprehension` counterpart.

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
