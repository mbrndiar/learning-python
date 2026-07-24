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

## 📖 How to study this chapter

Work through the three sections in order. Each introduces one collection
boundary, shows a small fragment, and then points to the complete runnable
companion. Predict the fragment's result before reading the explanation; run
the companion from the repository root; then make the suggested one-change
experiment.

This chapter deliberately uses no `for`, `while`, comprehension, or
learner-defined function. You can learn what collections *are* and how mutation
works before Chapter 4 teaches how to visit every element automatically.

## 1️⃣ Lists and tuples

Both `list` and `tuple` are ordered sequences: each element has a zero-based
position, so the indexing and slicing rules from strings still apply. Their
main difference is mutability:

- a `list` can change after creation;
- a `tuple` fixes its sequence of element references.

### Constructing and reading a list

Square brackets create a list:

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

print(numbers[0])
print(numbers[-1])
print(numbers[1:4])
print(numbers[::2])
```

```text
3
6
[1, 4, 1]
[3, 4, 5, 2]
```

As with `str`, a single index selects one element and a slice creates a new
sequence. The stop index is excluded, and a step of `2` selects every other
element. Unlike `str`, the list itself can also be changed.

### Mutating methods act on the same list

Common list methods have distinct contracts:

| Operation | Effect |
| --- | --- |
| `items.append(value)` | add one value at the end |
| `items.insert(index, value)` | add one value at a position |
| `items.remove(value)` | remove the first equal value |
| `items.pop()` | remove and return the last value |
| `items.extend(values)` | append each supplied value |
| `items.sort()` | reorder the same list |

Most mutating methods return `None` so that the caller does not confuse the
side effect with a newly created list. `pop()` is different because the
removed element is useful to the caller:

```python
numbers = [3, 1, 4]
numbers.append(10)
popped = numbers.pop()
sort_result = numbers.sort()

print(numbers)
print(popped)
print(sort_result)
```

```text
[1, 3, 4]
10
None
```

`numbers.sort()` changed `numbers` in place. Assigning its return value back to
the same name -- `numbers = numbers.sort()` -- would lose the list and bind
`numbers` to `None`.

When the desired contract is "produce an ordered copy," use `sorted(...)`:

```python
original = [5, 3, 4]
ordered = sorted(original)

print(ordered)
print(original)
```

```text
[3, 4, 5]
[5, 3, 4]
```

The two operations answer different questions: `.sort()` mutates one existing
list; `sorted()` creates and returns another list.

### Tuples express a fixed sequence

Commas create a tuple; parentheses usually make the grouping obvious. A
one-element tuple needs its trailing comma:

```python
point = (3, 4)
single_item = (5,)

print(point)
print(single_item)
```

```text
(3, 4)
(5,)
```

Without the comma, `(5)` is just the integer `5` in parentheses. Tuple item
assignment such as `point[0] = 10` raises `TypeError`, because the tuple's
element references cannot be replaced.

### Unpacking binds several names at once

Sequence unpacking matches values on the right with targets on the left:

```python
x, y = point
first, *middle, last = [10, 20, 30, 40, 50]

print(x, y)
print(first, middle, last)
```

```text
3 4
10 [20, 30, 40] 50
```

Ordinary unpacking requires exactly the expected number of elements. A starred
target collects all remaining middle elements into a list.

Run the complete companion:

```bash
python lessons/03_collections/01_lists_and_tuples.py
```

See [`01_lists_and_tuples.py`](01_lists_and_tuples.py) for the full method
sequence and its before/after output.

> **Try one change:** replace the starred assignment with
> `first, second, *rest = [10, 20, 30, 40, 50]`. Predict all three bindings
> before rerunning.

## 2️⃣ Dictionaries and sets

A list associates values with numeric positions. A `dict` instead associates
each value with a unique **key**. A `set` keeps only unique values and provides
membership and set-algebra operations.

### A dictionary maps keys to values

A dict literal uses `key: value` pairs:

```python
person = {
    "name": "Ada Lovelace",
    "occupation": "Mathematician",
    "year_born": 1815,
}

print(person["name"])
```

Bracket lookup means "this key must exist." If it does not, Python raises
`KeyError`. Use `.get(key, default)` when absence is an expected case:

```python
print(person.get("hobby", "Not specified"))
print("name" in person)
print("hobby" in person)
```

```text
Not specified
True
False
```

For a dict, `in` tests keys, not values. It answers the membership question
without retrieving anything.

Assignment through brackets updates an existing key or adds a new one.
`.pop(key)` removes a key and returns its value:

```python
person["occupation"] = "Computer Scientist"
person["nationality"] = "British"
removed_year = person.pop("year_born")

print(person)
print(removed_year)
```

```text
{'name': 'Ada Lovelace', 'occupation': 'Computer Scientist', 'nationality': 'British'}
1815
```

Python dicts preserve insertion order. Updating `"occupation"` leaves it in
its original position; adding `"nationality"` places that key last.

`.keys()`, `.values()`, and `.items()` expose dynamic **view objects** over a
dict. This chapter converts a view to a list for inspection, because iteration
belongs to Chapter 4:

```python
print(list(person.keys()))
print(list(person.items()))
```

### Keys and set members must be hashable

Dict lookup needs a key whose hash remains stable while the key is stored.
Immutable values such as strings, integers, and tuples of hashable values fit
that contract:

```python
coordinates = {(0, 0): "origin", (1, 1): "diagonal"}
print(coordinates[(0, 0)])
```

A list is mutable and therefore unhashable. Writing
`{[1, 2]: "invalid"}` would raise `TypeError`. The same hashability rule
applies to set members.

### Sets keep unique members

Curly braces with comma-separated values create a set:

```python
languages = {"Python", "JavaScript", "Python", "Go"}
print(sorted(languages))

languages.add("Rust")
languages.discard("Go")
print(sorted(languages))
```

```text
['Go', 'JavaScript', 'Python']
['JavaScript', 'Python', 'Rust']
```

The repeated `"Python"` collapses into one member. Sets do not promise an
iteration order, so `sorted(...)` creates a deterministic list for display.
Use `set()`, not `{}`, for an empty set -- `{}` creates an empty dict.

Set operators compare membership:

```python
other = {"Go", "Rust", "Java"}

print(sorted(languages & other))
print(sorted(languages | other))
print(sorted(languages - other))
print(sorted(languages ^ other))
```

| Operator | Meaning | Result |
| --- | --- | --- |
| `&` | members in both sets | `['Rust']` |
| `\|` | members in either set | `['Go', 'Java', 'JavaScript', 'Python', 'Rust']` |
| `-` | members only in the left set | `['JavaScript', 'Python']` |
| `^` | members in exactly one set | `['Go', 'Java', 'JavaScript', 'Python']` |

Run the complete companion:

```bash
python lessons/03_collections/02_dictionaries_and_sets.py
```

See [`02_dictionaries_and_sets.py`](02_dictionaries_and_sets.py) for lookup,
updates, views, hashability, and all four set operations.

> **Try one change:** replace `other_languages` in the companion with the
> empty set `set()`. Predict the intersection, union, and difference before
> rerunning.

## 3️⃣ References, mutation, and copying

Chapter 1 established that assignment binds a name to an object. With mutable
collections, that model becomes observable: two names can point to one list,
and a change through either name changes the one shared object.

### Assignment creates an alias, not a copy

```python
roster = ["Ada", "Grace"]
team = roster
team.append("Alan")

print(roster)
print(team)
print(roster is team)
```

```text
['Ada', 'Grace', 'Alan']
['Ada', 'Grace', 'Alan']
True
```

`team = roster` creates a second name for the existing list. It does not create
a second list. `team.append(...)` therefore changes the object seen through
both names. This relationship is called **aliasing**.

### Equality and identity answer different questions

```python
other_roster = ["Ada", "Grace", "Alan"]

print(roster == other_roster)
print(roster is other_roster)
```

The first line is `True`: both lists contain equal values in equal order. The
second is `False`: they are two distinct list objects.

- `==` asks whether values are equal;
- `is` asks whether both expressions identify the same object.

Use `is` for identity checks such as `value is None`; use `==` for ordinary
value comparison.

### Rebinding moves one name

```python
team = ["Replacement"]

print(roster)
print(team)
```

Rebinding `team` points that name at a new list. It does not edit the old list,
which is still reachable through `roster`.

### A shallow copy duplicates only the outer collection

`list.copy()` creates a new outer list:

```python
original = [1, 2, 3]
shallow = original.copy()
shallow.append(4)

print(original)
print(shallow)
```

```text
[1, 2, 3]
[1, 2, 3, 4]
```

The outer lists are independent. But their elements are not recursively
copied. If an element is itself mutable, both outer lists still refer to that
same inner object:

```python
nested = [["Ada"], ["Grace"]]
shallow_nested = nested.copy()
shallow_nested[0].append("Lovelace")

print(nested)
print(shallow_nested)
```

```text
[['Ada', 'Lovelace'], ['Grace']]
[['Ada', 'Lovelace'], ['Grace']]
```

Mutating the shared inner list is visible through both outer lists. Replacing
an element is different:

```python
shallow_nested[1] = ["Hopper"]
print(nested)
```

`nested` still contains `["Grace"]` at index 1, because replacement changes
only which inner object the copied outer list refers to. A shallow copy is
therefore not a recursively independent deep copy.

`bytearray` follows the same rules as `list`: assignment can alias one mutable
buffer, while `bytearray(existing_buffer)` creates another buffer with copied
contents.

Run the complete companion:

```bash
python lessons/03_collections/03_references_mutation_and_copying.py
```

See
[`03_references_mutation_and_copying.py`](03_references_mutation_and_copying.py)
for list and `bytearray` aliasing side by side.

> **Try one change:** replace
> `shallow_nested[0].append("Lovelace")` with
> `shallow_nested[0] = ["Somerville"]`. Predict whether `nested` changes
> before rerunning.

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
