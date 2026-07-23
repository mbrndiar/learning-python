"""
Chapter 11, Lesson 3: Literal, Annotated, and Self

Purpose: introduce three typing tools that later chapters' frameworks
(Pydantic-style validation, dependency-injected services) rely on:
`Literal` for a closed set of exact allowed values, `Annotated` for
attaching metadata to a type without changing what the type itself is,
and `Self` for a method that returns an instance of whatever class it
was actually called on.

Prerequisites: Lesson 2 (collections, callables, and generics).

Read this file top to bottom, predict each output, then run it:

    python lessons/11_typing_protocols_and_di/03_literal_annotated_and_self.py
"""

from dataclasses import dataclass, field
from typing import Annotated, Literal, Self

# Step 1: Literal narrows a type to a specific, closed set of exact
# values -- not just "a str", but only these particular strings. A type
# checker rejects a call passing any other string, even though Python
# itself does not check this at runtime.
Mode = Literal["read", "write", "append"]


def open_mode_label(mode: Mode) -> str:
    """Describe a file-opening mode from a closed set of valid modes."""
    return f"opening in {mode!r} mode"


print(open_mode_label("read"))
print(open_mode_label("write"))
# open_mode_label("delete") would be flagged by a type checker (Mode does
# not include "delete") even though Python runs it without complaint --
# exactly the same "not enforced at runtime" property Lesson 1 covered.


# Step 2: Annotated attaches metadata to a type without changing what the
# type itself is -- `Annotated[int, "a positive count"]` is still `int`
# to every runtime check; the metadata is for tools and readers, such as
# a validation framework (the kind Chapter 8's boundary validation, and
# later a web framework, might read to auto-generate a check).
PositiveInt = Annotated[int, "must be greater than zero"]


def repeat_label(label: str, count: PositiveInt) -> str:
    """Repeat `label`, `count` times, separated by commas."""
    if count <= 0:
        raise ValueError("count must be greater than zero")
    return ", ".join([label] * count)


print("\nrepeat_label('hi', 3):", repeat_label("hi", 3))


# Step 3: Self documents a method that returns an instance of whatever
# class it was actually called on -- important for a fluent/builder-style
# method that a subclass calls and expects a same-subclass return value.
@dataclass
class QueryBuilder:
    """A minimal builder demonstrating Self-typed chained methods."""

    table: str
    # field(default_factory=list) gives each QueryBuilder its own list,
    # following the dataclass mutable-default rule Chapter 9 explained.
    filters: list = field(default_factory=list)

    def where(self, condition: str) -> Self:
        """Add a filter and return self, so calls can be chained."""
        # Returning Self (not "QueryBuilder") means a subclass calling
        # where() gets back an instance of the SUBCLASS, exactly like
        # Chapter 9's Circle.unit_circle() constructed cls(1), not
        # Circle(1).
        self.filters.append(condition)
        return self

    def describe(self) -> str:
        clauses = " AND ".join(self.filters) if self.filters else "1=1"
        return f"SELECT * FROM {self.table} WHERE {clauses}"


class NamedQueryBuilder(QueryBuilder):
    """A subclass whose chained where() calls should still return itself."""

    def label(self) -> str:
        return f"[{self.table} query]"


builder = QueryBuilder("users").where("active = true").where("age >= 18")
print("\n", builder.describe(), sep="")

named_builder = NamedQueryBuilder("orders").where("status = 'open'")
print("Chained call kept the subclass type:", type(named_builder).__name__)
print(named_builder.label())

# --- One-variable experiment -------------------------------------------
# Change where()'s return annotation from Self to "QueryBuilder" (a
# string forward reference to the base class) and predict what a type
# checker would say about named_builder.label() afterward -- Python
# itself would still run it fine, since annotations do not change
# runtime behavior, but a checker would no longer know the chained
# result is a NamedQueryBuilder specifically.
