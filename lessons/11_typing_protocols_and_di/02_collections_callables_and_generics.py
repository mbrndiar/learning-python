"""
Chapter 11, Lesson 2: Collections, Callables, and Generics

Purpose: use the abstract collection types `Iterable`, `Sequence`, and
`Mapping` to describe what a parameter needs to support instead of which
concrete type it is; annotate a callback parameter with `Callable`; and
write a generic function with `TypeVar` whose return type is tied to its
input type.

Prerequisites: Lesson 1 (annotations and narrowing).

Read this file top to bottom, predict each output, then run it:

    python lessons/11_typing_protocols_and_di/02_collections_callables_and_generics.py
"""

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TypeVar


# Step 1: Iterable is the broadest collection contract -- only "can be
# iterated with for", nothing about length or indexing. A function that
# only loops over its argument should accept the broadest type its body
# actually requires, so callers are not forced into one concrete type.
def total_length(names: Iterable[str]) -> int:
    """Return the total character count across every name."""
    return sum(len(name) for name in names)


print("total_length(['Ada', 'Grace']):", total_length(["Ada", "Grace"]))
print(
    "total_length(name for name in ('Ada', 'Grace')):",
    total_length(name for name in ("Ada", "Grace")),
)
# Both a list and a generator satisfy Iterable[str] -- total_length's
# body never asked for indexing or a known length, so it does not
# require either.


# Step 2: Sequence adds ordered, indexable access (len(), obj[i],
# slicing) without requiring mutability -- both list and tuple satisfy
# it, but a plain generator does not.
def first_and_last(items: Sequence[str]) -> tuple[str, str]:
    """Return the first and last elements of an ordered sequence."""
    return items[0], items[-1]


print("\nfirst_and_last(['a', 'b', 'c']):", first_and_last(["a", "b", "c"]))
print("first_and_last(('x', 'y', 'z')):", first_and_last(("x", "y", "z")))


# Step 3: Mapping describes a read-only key-lookup contract -- a plain
# dict satisfies it, but the annotation itself promises nothing about
# mutating the argument, documenting the function's actual intent.
def describe_scores(scores: Mapping[str, int]) -> str:
    """Describe scores sorted by name, without mutating `scores`."""
    return ", ".join(f"{name}={score}" for name, score in sorted(scores.items()))


print(
    "\ndescribe_scores({'Ada': 90, 'Grace': 95}):",
    describe_scores({"Ada": 90, "Grace": 95}),
)


# Step 4: Callable[[ArgTypes], ReturnType] annotates a parameter that
# must itself be callable -- a function passed as a value, exactly like
# the decorators Chapter 10 wrote, but now with the shape documented.
def apply_twice(operation: Callable[[int], int], value: int) -> int:
    """Apply `operation` to `value` twice in a row."""
    return operation(operation(value))


print("\napply_twice(lambda x: x + 3, 10):", apply_twice(lambda x: x + 3, 10))


# Step 5: a generic function. TypeVar("T") introduces a placeholder type
# that a type checker fills in per call -- first([1, 2, 3]) is understood
# as returning int, while first(["a", "b"]) is understood as returning
# str, from the SAME function definition.
T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    """Return the first element, generic over the sequence's element type."""
    return items[0]


print("\nfirst([1, 2, 3]):", first([1, 2, 3]))
print("first(['a', 'b']):", first(["a", "b"]))

# --- One-variable experiment -------------------------------------------
# Try calling first_and_last on a generator expression, e.g.
# first_and_last(x for x in "abc"), and predict the runtime error. A
# generator supports neither items[0] nor items[-1] -- exactly the
# capability Sequence promises and Iterable does not, which is why
# first_and_last's parameter is annotated Sequence, not Iterable.
