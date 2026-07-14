# 🗂️ Module 4: Data Structures

Python's built-in collection types, and concise ways to build and
transform them.

## 🎯 Learning objectives

After this module, you should be able to select a collection by its semantics,
copy and mutate collections intentionally, iterate through mappings, and write
readable comprehensions.

## 🧭 Choosing a collection

| Type | Ordered | Mutable | Duplicates | Typical purpose |
| --- | --- | --- | --- | --- |
| `list` | yes | yes | yes | changing sequence |
| `tuple` | yes | no | yes | fixed record or sequence |
| `dict` | insertion order | yes | keys unique | key-to-value lookup |
| `set` | no promised order | yes | no | membership and set algebra |
| `frozenset` | no promised order | no | no | immutable set |

Membership in a set or dictionary is usually faster than scanning a list.
Choose by meaning first, then measure performance if it matters.

## 🔗 References, mutation, and copying

Assignment does not copy an object:

```python
first = [1, 2]
second = first
second.append(3)
print(first)  # [1, 2, 3]
```

Use `first.copy()`, `first[:]`, or `list(first)` for a shallow copy. Nested
objects remain shared; use `copy.deepcopy()` only when independent recursive
copies are truly required. Equality (`==`) compares values, while identity
(`is`) asks whether two names refer to the same object.

Tuple unpacking assigns several names (`x, y = point`), and starred unpacking
captures the remainder (`first, *middle, last = values`). Dictionary views
from `.keys()`, `.values()`, and `.items()` reflect later dictionary changes.
Keys must be hashable, which normally means their equality-relevant state
cannot change.

## ✨ Comprehensions

A comprehension describes a transformation and optional filter:

```python
squares = {number: number ** 2 for number in range(6) if number % 2 == 0}
```

Use a normal loop when the expression has side effects, multiple steps, or
becomes difficult to read. A generator expression uses parentheses and
produces values lazily instead of storing all of them.

## 📚 Concepts covered

- **`01_lists_and_tuples.py`** - lists (mutable, ordered) and tuples
  (immutable, ordered): creating, indexing, slicing and common methods.
- **`02_dictionaries_and_sets.py`** - dictionaries (key-value pairs) and
  sets (unique, unordered values), including common operations on each.
- **`03_comprehensions_and_collections.py`** - list/dict/set/generator
  comprehensions, and useful classes from the `collections` module:
  `Counter`, `defaultdict`, `namedtuple` and `OrderedDict`.

## ▶️ Running

```bash
python lessons/04_data_structures/01_lists_and_tuples.py
python lessons/04_data_structures/02_dictionaries_and_sets.py
python lessons/04_data_structures/03_comprehensions_and_collections.py
```

Once you've read through all three files, practice what you learned in
[`exercises/04_data_structures/`](../../exercises/04_data_structures/README.md).

## ⚠️ Common mistakes

- Expecting assignment or a shallow copy to duplicate nested objects.
- Relying on set iteration order.
- Accessing a missing dictionary key with `mapping[key]` when `.get()` is
  appropriate.
- Modifying collection size while iterating over it.
- Using a comprehension so complex that a loop would be clearer.

## ❓ Review questions

1. Which collection best represents unique tags, and why?
2. What is shared after making a shallow copy of a nested list?
3. How do `mapping[key]` and `mapping.get(key)` differ for a missing key?
4. Why can a tuple usually be a dictionary key but a list cannot?
5. When is a generator expression preferable to a list comprehension?
