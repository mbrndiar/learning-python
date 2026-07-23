# 📦 Chapter 3: Collections

**Semantic ID:** `module.collections` · **Prerequisites:**
`module.text-and-numbers`

## 📍 Where this fits

Chapters 1 and 2 worked with single values and text. This chapter
introduces Python's four core built-in collections -- `list`, `tuple`,
`dict`, and `set` -- along with the idea that some names can share the same
underlying object. Deliberately, this chapter does **not** iterate a
collection with `for`/`while`, and does not use comprehensions: those are
Chapter 4's subject. Everything here is solved with construction, indexing,
slicing, membership tests, and methods.

## 🎯 Learning objectives

After this chapter, you should be able to:

- construct, index, slice, and mutate a `list`, and construct and unpack a
  `tuple`;
- explain why a mutating method such as `.append()` returns `None` and how
  that differs from a function such as `sorted()` that returns a new
  collection;
- construct a `dict` and a `set`, look up and update values, and test
  membership with `in`;
- explain why dictionary/set keys must be hashable and what happens when a
  mutable object such as a list is used as one;
- distinguish `is` (identity) from `==` (equality), and explain aliasing:
  two names bound to the very same object;
- distinguish in-place mutation from rebinding, and a shallow copy from an
  independent (deep) one.

## 🧠 Motivation and mental model

So far, every value in this course has been immutable (numbers, strings) or
used only through a single name. Collections introduce a new possibility:
**two names can refer to the exact same mutable object.** When that
happens, a mutation performed through one name is visible through the
other, because there is really only one object -- not two copies of it.
This is not a bug or a special case; it follows directly from Chapter 1's
mental model that assignment binds a name to an object rather than copying
it.

Understanding this is essential before Chapter 4 introduces loops: a loop
that appears to "not work" is very often actually mutating a shared list
that another part of the program still expects to be untouched.

## 🧩 Progressive syntax and mechanism

1. **List construction and access.** `[a, b, c]`; `lst[i]`, `lst[i:j]`,
   `lst[::step]`; mutating methods `.append()`, `.insert()`, `.remove()`,
   `.pop()`, `.sort()`, `.extend()`, all returning `None` and mutating in
   place. `sorted(lst)` instead returns a new list.
2. **Tuple construction and unpacking.** `(a, b)`; a single-element tuple
   needs a trailing comma, `(a,)`. Tuples reject item assignment. Unpacking:
   `x, y = point`; starred unpacking, `first, *rest = values`.
3. **Dict construction and access.** `{"key": value, ...}`; `d[key]` raises
   `KeyError` for a missing key, `d.get(key, default)` does not; `d[key] =
   value` updates or adds; `d.pop(key)` removes and returns a value.
   `.keys()`/`.values()`/`.items()` return view objects, shown here through
   `list(...)` for deterministic printing rather than a loop.
4. **Hashability.** Dict keys and set members must be hashable, which
   requires effective immutability. A `list` is unhashable and raises
   `TypeError` if used as a key; a `tuple` of hashable values works.
5. **Set construction and algebra.** `{a, b, c}`; `.add()`, `.discard()`;
   `&` (intersection), `|` (union), `-` (difference), `^` (symmetric
   difference). Set order is not guaranteed, so this lesson sorts a set
   before printing it for deterministic output.
6. **Identity versus equality.** `is` compares object identity; `==`
   compares value. Two distinct, equal lists are `==` but not `is`.
7. **Aliasing, mutation, and copying.** Assigning one name to another
   (`team = roster`) creates an alias, not a copy. `.copy()` (or
   `list(original)`) makes a *shallow* copy: mutating the new outer
   collection does not affect the original, but a *shared inner mutable
   object* still does, until it is replaced rather than mutated.
   `bytearray` follows the same aliasing and copying rules as `list`.

## 📖 Read-predict-run-modify workflow

Work through the three lesson files in order, predicting each `print()`
before running:

```bash
python lessons/03_collections/01_lists_and_tuples.py
python lessons/03_collections/02_dictionaries_and_sets.py
python lessons/03_collections/03_references_mutation_and_copying.py
```

### Expected output highlights

- `01_lists_and_tuples.py`: `sorted(unsorted_copy)` prints a new, sorted
  list while `unsorted_copy unchanged:` reprints the original order.
- `02_dictionaries_and_sets.py`: `person` keeps insertion order through
  every update; an invalid list-key expression is shown only as a comment.
- `03_references_mutation_and_copying.py`: `roster` and `team` both show
  `"Alan"` appended, and `roster is team` prints `True` -- until `team` is
  rebound to a brand-new list, after which `roster` is unaffected.

## 🔁 Transition to Chapter 4

This chapter inspected collections only by index, slice, and membership.
Chapter 4, Flow and Iteration, introduces `for` and `while` to visit every
element of a collection, and shows how comprehensions are a direct
translation of an equivalent loop.

## ⚠️ Common mistakes

- Printing the return value of a mutating method (for example,
  `print(numbers.sort())`), which prints `None`.
- Assuming `list.copy()` produces a fully independent object when its
  elements are themselves mutable.
- Using a `list` as a dict key or set member and being surprised by
  `TypeError` -- only hashable (typically immutable) values are allowed.
- Confusing `is` with `==`: two equal-but-distinct objects are not
  identical.
- Assuming a `dict` or `set` prints in a specific, guaranteed order for
  sets -- only dicts guarantee insertion order.

## 🧾 Summary

- `list`, `tuple`, `dict`, and `set` are the four core built-in collections,
  each with different mutability and ordering guarantees.
- Assignment can create an alias to an existing object; mutating through
  one alias is visible through every other alias to the same object.
- A shallow copy protects the outer collection but not shared, mutable
  inner objects.
- Hashability -- effectively, immutability -- is required for dict keys and
  set members.

## ❓ Review questions (closed notes)

1. What does `numbers.sort()` return, and why does printing it directly
   surprise many learners?
2. What is the difference between `a is b` and `a == b`?
3. If `b = a` and then `b.append(1)`, what happens to `a`? What if instead
   `b = a[:]` (or `a.copy()`) before `b.append(1)`?
4. Why can a `tuple` be used as a dict key but a `list` cannot?
5. What is the difference between `dict.get(key, default)` and
   `dict[key]`?
6. Given `nested = [[1], [2]]` and `shallow = nested.copy()`, does
   `shallow[0].append(9)` change `nested`? Does `shallow[0] = [9]`?

## 📚 Authoritative references

- [Common sequence operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations)
- [More on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
- [Mapping types — `dict`](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [Set types — `set`, `frozenset`](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [`copy` — shallow and deep copy operations](https://docs.python.org/3/library/copy.html)
- [Data model: object identity](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)

Once you can answer the review questions and have run all three lesson
files, continue to
[`exercises/03_collections/`](../../exercises/03_collections/README.md).
