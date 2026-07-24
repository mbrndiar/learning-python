# 🧬 Chapter 11: Typing, Protocols, and Dependency Injection

**Semantic ID:** `module.typing-protocols-and-di` · **Prerequisites:**
`module.iteration-decorators-and-contexts`

## 📍 Where this fits

Every function signature so far has stayed informally typed -- Chapter
9's `BankAccount.deposit` and Chapter 10's decorators worked correctly,
but nothing in the code itself documented their expected shapes for a
tool (or another developer) to check. This chapter makes contracts
explicit: narrowing a union type, writing a function generic over
`Iterable`/`Sequence`/`Callable`, and depending on a `Protocol` instead of
one concrete class. These are exactly the tools the course's later
chapters (SQL, HTTP clients, and any validation-heavy framework) rely on
to describe interfaces precisely.

## 🎯 Learning objectives

After this chapter, you should be able to:

- explain that annotations are optional and not enforced by Python at
  runtime, and describe what a static type checker uses them for;
- write and narrow a union type (`X | None`), and explain why an `if`
  check that rules out `None` lets a checker treat the remaining branch
  as a definite type;
- define and use a type alias for a recurring annotation shape;
- choose among `Iterable`, `Sequence`, and `Mapping` for a parameter,
  based on what the function body actually requires;
- annotate a callback parameter with `Callable[[ArgTypes], ReturnType]`;
- write a generic function with `TypeVar` whose return type is tied to
  its input type;
- use `Literal` for a closed set of exact allowed values, `Annotated` for
  attaching metadata to a type, and `Self` for a method that must return
  an instance of whatever class it was actually called on;
- define a `Protocol` describing required behavior structurally, inject
  a collaborator that satisfies it instead of constructing one
  internally, and write an adapter for an existing class that does not
  match the Protocol's exact method names.

## 🧠 Motivation and mental model

A type annotation is a promise a static tool can check before your code
ever runs -- it costs nothing at runtime (Python still runs
`add("2", "3")` without complaint) but catches a whole category of bugs
earlier, on your editor's red squiggly line instead of in production.
Depending on a `Protocol` rather than one concrete class is the same idea
applied to object design: `ReminderService` never needs to know whether
it is talking to a real console, a legacy system through an adapter, or a
test double that just records calls -- only that whatever it received
has a `send` method with the right shape. That is dependency injection:
give an object its collaborator, don't let it go find one itself.

## 1️⃣ Annotations, unions, narrowing, and type aliases

A type annotation documents expected types but is **not enforced by
Python itself at runtime** -- only external tools (mypy, IDEs) check
them:

```python
def add(a: int, b: int) -> int:
    """A function with hinted parameter types and a return type."""
    return a + b


print(add(2, 3))
print(add("2", "3"))
```

```text
5
23
```

`add('2', '3')` still concatenates at runtime, returning `'23'` -- it
violates `add`'s `int` hints, and Python runs it anyway. Annotations are
documentation for tools, not a runtime contract like a function's actual
behavior.

### Unions, `None`, and narrowing

```python
def shout_if_present(maybe_name: str | None) -> str:
    if maybe_name is None:
        return "(no name)"
    # Here, maybe_name is narrowed to str -- .upper() is always valid on
    # this branch, which is exactly what the `is None` check ruled out.
    return maybe_name.upper()


print(shout_if_present("ada"))
print(shout_if_present(None))
```

```text
ADA
(no name)
```

`str | None` documents that a value may be absent -- the union of type
`str` and the singleton type of `None`. Inside `if maybe_name is not None`
(or, equivalently, the branch past an `is None` check that returns
early), a type checker treats `maybe_name` as `str`, even though its
declared type is `str | None`. This is not special syntax -- it is the
type checker reading the same `if` a human reader already relies on to
reason about the code.

### Type aliases name a recurring shape

```python
UserMap = dict[int, str]


def describe_users(users: UserMap) -> list[str]:
    return [f"{user_id}: {name}" for user_id, name in sorted(users.items())]


print(describe_users({1: "Ada", 2: "Grace"}))
```

```text
['1: Ada', '2: Grace']
```

`UserMap = dict[int, str]` names a shape once so signatures referencing
it stay readable, instead of repeating `dict[int, str]` everywhere.

Run the complete companion:

```bash
python lessons/11_typing_protocols_and_di/01_annotations_and_narrowing.py
```

See
[`01_annotations_and_narrowing.py`](01_annotations_and_narrowing.py) for
the full sequence, including a `Point` class with a string forward
reference (`"Point"`) in its own method annotation.

> **Try one change:** move `maybe_name.upper()` in `shout_if_present`
> so it runs *before* the `if maybe_name is None:` check, instead of
> after. Predict what happens when this runs with `None` -- and
> separately, predict what mypy (not Python itself) would say about that
> reordered code, given `maybe_name`'s declared type is `str | None` at
> that point.

## 2️⃣ Typed collections, `Callable`, and generic functions

`Iterable`, `Sequence`, and `Mapping` describe what a parameter needs to
support, not which concrete type it is -- choose the narrowest one a
function body actually requires.

```python
from collections.abc import Iterable, Sequence


def total_length(names: Iterable[str]) -> int:
    return sum(len(name) for name in names)


def first_and_last(items: Sequence[str]) -> tuple[str, str]:
    return items[0], items[-1]


print(total_length(["Ada", "Grace"]))
print(total_length(name for name in ("Ada", "Grace")))
print(first_and_last(["a", "b", "c"]))
```

```text
8
8
('a', 'c')
```

`total_length` only ever loops over `names`, so it accepts the broadest
type its body actually requires (`Iterable[str]`) -- both a list and a
generator expression satisfy it, since neither indexing nor a known
length is ever needed. `first_and_last` requires indexing (`items[0]`,
`items[-1]`), which `Sequence` promises and `Iterable` does not -- a
plain generator would fail here, which is exactly the distinction that
makes `Iterable` vs. `Sequence` observable, not just a naming choice.

### `Callable` and a generic function with `TypeVar`

```python
from collections.abc import Callable, Sequence
from typing import TypeVar


def apply_twice(operation: Callable[[int], int], value: int) -> int:
    return operation(operation(value))


T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    return items[0]


print(apply_twice(lambda x: x + 3, 10))
print(first([1, 2, 3]))
print(first(["a", "b"]))
```

```text
16
1
a
```

`Callable[[int], int]` annotates a parameter that must itself be
callable with that exact argument/return shape -- a function passed as a
value, exactly like Chapter 10's decorators, but now with the shape
documented. `TypeVar("T")` introduces a placeholder type a checker fills
in per call: `first([1, 2, 3])` is understood as returning `int`, while
`first(["a", "b"])` is understood as returning `str`, from the *same*
function definition -- no per-type duplicate needed.

Run the complete companion:

```bash
python lessons/11_typing_protocols_and_di/02_collections_callables_and_generics.py
```

See
[`02_collections_callables_and_generics.py`](02_collections_callables_and_generics.py)
for the full sequence, including a `Mapping`-typed `describe_scores`.

> **Try one change:** call `first_and_last` on a generator expression,
> e.g. `first_and_last(x for x in "abc")`, and predict the runtime error.
> A generator supports neither `items[0]` nor `items[-1]` -- exactly the
> capability `Sequence` promises and `Iterable` does not, which is why
> `first_and_last`'s parameter is annotated `Sequence`, not `Iterable`.

## 3️⃣ `Literal`, `Annotated`, and `Self`

`Literal` narrows a type to a specific, closed set of exact values -- a
type checker rejects a call passing any other value, even though Python
itself does not check this at runtime:

```python
from typing import Literal

Mode = Literal["read", "write", "append"]


def open_mode_label(mode: Mode) -> str:
    return f"opening in {mode!r} mode"


print(open_mode_label("read"))
```

```text
opening in 'read' mode
```

`open_mode_label("delete")` would be flagged by a type checker (`Mode`
does not include `"delete"`) even though Python runs it without
complaint -- the same "not enforced at runtime" property as concept 1.

### `Annotated` attaches metadata without changing the runtime type

```python
from typing import Annotated

PositiveInt = Annotated[int, "must be greater than zero"]


def repeat_label(label: str, count: PositiveInt) -> str:
    if count <= 0:
        raise ValueError("count must be greater than zero")
    return ", ".join([label] * count)


print(repeat_label("hi", 3))
```

```text
hi, hi, hi
```

`Annotated[int, "must be greater than zero"]` is still `int` to every
runtime check -- the metadata is for tools and readers, such as a
validation framework. Because that metadata is not enforced,
`repeat_label` still validates `count` itself with an explicit `if`
check and a raised `ValueError`; static hints never replace runtime
validation at a boundary like this.

### `Self` follows the actual subclass through a chained call

```python
from dataclasses import dataclass, field
from typing import Self


@dataclass
class QueryBuilder:
    table: str
    filters: list = field(default_factory=list)

    def where(self, condition: str) -> Self:
        self.filters.append(condition)
        return self

    def describe(self) -> str:
        clauses = " AND ".join(self.filters) if self.filters else "1=1"
        return f"SELECT * FROM {self.table} WHERE {clauses}"


class NamedQueryBuilder(QueryBuilder):
    def label(self) -> str:
        return f"[{self.table} query]"


named_builder = NamedQueryBuilder("orders").where("status = 'open'")
print(type(named_builder).__name__)
print(named_builder.label())
```

```text
NamedQueryBuilder
[orders query]
```

`type(named_builder).__name__` prints `NamedQueryBuilder`, not
`QueryBuilder` -- `where()`'s `Self` return type documents that a
chained call on a subclass instance returns an instance of that same
subclass, so `named_builder.label()` (defined only on
`NamedQueryBuilder`) is still callable afterward. Returning `Self` (not
the string `"QueryBuilder"`) is the same idea as Chapter 9's
`Circle.unit_circle()` constructing `cls(1)` rather than `Circle(1)`.

Run the complete companion:

```bash
python lessons/11_typing_protocols_and_di/03_literal_annotated_and_self.py
```

See
[`03_literal_annotated_and_self.py`](03_literal_annotated_and_self.py)
for the full sequence, including chained `.where()` calls on the base
`QueryBuilder`.

> **Try one change:** change `where()`'s return annotation from `Self`
> to `"QueryBuilder"` (a string forward reference to the base class) and
> predict what a type checker would say about `named_builder.label()`
> afterward -- Python itself would still run it fine, since annotations
> do not change runtime behavior, but a checker would no longer know the
> chained result is a `NamedQueryBuilder` specifically.

## 4️⃣ `Protocol`, adapters, and dependency injection

A `Protocol` describes required behavior structurally, by shape, not
inheritance: any object with a matching method satisfies it, whether or
not it inherits from anything related to it.

```python
from dataclasses import dataclass
from typing import Protocol


class MessageSender(Protocol):
    def send(self, recipient: str, message: str) -> None: ...


@dataclass
class ReminderService:
    sender: MessageSender  # injected, not constructed internally

    def remind(self, recipient: str, task: str) -> None:
        self.sender.send(recipient, f"Reminder: {task}")


class ConsoleSender:
    def send(self, recipient: str, message: str) -> None:
        print(f"To {recipient}: {message}")


class RecordingSender:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> None:
        self.messages.append((recipient, message))


ReminderService(ConsoleSender()).remind("Ada", "finish the typing lesson")

recording_sender = RecordingSender()
ReminderService(recording_sender).remind("Lin", "test without real I/O")
print(recording_sender.messages)
```

```text
To Ada: Reminder: finish the typing lesson
[('Lin', 'Reminder: test without real I/O')]
```

Neither `ConsoleSender` nor `RecordingSender` inherits from
`MessageSender` -- each is accepted purely because it defines a matching
`send(recipient, message)` method. The exact same `ReminderService`
class delivers a reminder through a console and through a
recording test double, without any change to `ReminderService` itself:
this is dependency injection -- `ReminderService` receives its
collaborator instead of constructing one internally (`self.sender =
ConsoleSender()` inside `__init__` would remove that flexibility).

### An adapter translates an unrelated interface

```python
class LegacyNotifier:
    """Pretend this older class is depended on elsewhere and cannot change."""

    def notify(self, text: str) -> None:
        print(text)


class LegacyNotifierAdapter:
    def __init__(self, notifier: LegacyNotifier) -> None:
        self.notifier = notifier

    def send(self, recipient: str, message: str) -> None:
        self.notifier.notify(f"[{recipient}] {message}")


adapted_sender = LegacyNotifierAdapter(LegacyNotifier())
ReminderService(adapted_sender).remind("Grace", "review the capstone")
```

```text
[Grace] Reminder: review the capstone
```

`LegacyNotifier` already exists and cannot be changed, but its method is
called `notify()`, not `send()`, so it does not satisfy `MessageSender`
as written. `LegacyNotifierAdapter` wraps it, translating one interface
into the other at a single boundary -- the same `ReminderService` still
works unchanged, now with a third, entirely unrelated implementation.
`Protocol` compatibility is checked structurally: an object with an
extra, differently-named method still fails to satisfy a `Protocol`
requiring that method under its expected name, which is exactly why an
adapter (not a cast) is needed here.

Run the complete companion:

```bash
python lessons/11_typing_protocols_and_di/04_protocols_adapters_and_dependency_injection.py
```

See
[`04_protocols_adapters_and_dependency_injection.py`](04_protocols_adapters_and_dependency_injection.py)
for the full sequence, including a `hasattr()` check showing why that
alone cannot verify full Protocol compatibility.

> **Try one change:** write a third sender, e.g. a `RaisingSender` whose
> `send()` always raises `RuntimeError`, and pass it to
> `ReminderService(...).remind(...)`. Predict: does anything about
> `ReminderService` itself need to change to accept this new sender? (No
> -- `ReminderService` only ever calls `self.sender.send(...)`; any
> object providing that method is accepted, which is the entire point of
> depending on a `Protocol` instead of one concrete class.)

## 🔁 Transition ahead

This chapter completes the composition and language-mechanisms arc.
Later chapters describing SQL rows, HTTP request/response bodies, and
concurrent tasks build directly on the vocabulary from here: a repository
class depending on a `Protocol` instead of one database driver, a generic
function processing rows of a `TypeVar`-parameterized shape, and a
`Literal`-typed status field validated at a JSON boundary exactly like
Chapter 8's `validate_record`.

## ⚠️ Common mistakes

- Expecting Python to raise an error at runtime when an annotation is
  violated -- only a separate type-checking tool does that.
- Accepting a wider type (like `list`) than a function body actually
  needs, forcing every caller to build one instead of passing whatever
  iterable they already have.
- Writing `Callable` without its argument list (`Callable[..., int]` when
  the exact signature is in fact known), losing a checker's ability to
  verify the callback's parameters.
- Constructing a collaborator internally (`self.sender = ConsoleSender()`
  inside `__init__`) instead of accepting it as a parameter, which
  removes the ability to substitute a test double or a different
  implementation.
- Forgetting that `Protocol` compatibility is structural: an object with
  an extra, differently-named method still fails to satisfy a Protocol
  requiring that method under its expected name -- an adapter is needed,
  not a cast.

## 🧾 Summary

- Annotations document intent for static tools; Python itself never
  enforces them at runtime.
- Narrowing a union (`is None`/`is not None`) lets both a type checker
  and a human reader treat each branch as one definite type.
- `Iterable`/`Sequence`/`Mapping`/`Callable` describe what a parameter
  must support, independent of its concrete type; `TypeVar` ties a
  generic function's return type to its input.
- `Literal`, `Annotated`, and `Self` are the vocabulary later validation
  and builder-style frameworks are built on.
- `Protocol` plus dependency injection decouples behavior from one
  concrete implementation; an adapter lets an existing, unrelated class
  satisfy a Protocol it was never written against.

## ❓ Review questions (closed notes)

1. Does Python raise an error at runtime when a call violates a type
   hint? What tool would catch it instead?
2. What does narrowing a union type actually change, and what triggers
   it?
3. What is the difference between requiring `Iterable[str]` and requiring
   `Sequence[str]` for a parameter?
4. Why does a generic function using `TypeVar` need only one definition
   instead of one per concrete type?
5. What does `Annotated` add to a type that a plain type alone does not
   provide, and does it change runtime behavior?
6. Why does dependency injection make `ReminderService` easier to test?
7. When is an adapter needed instead of relying on `Protocol` compatibility
   directly?

## 📚 Authoritative references

- [`typing` -- Support for type hints](https://docs.python.org/3/library/typing.html)
- [`collections.abc` -- Abstract Base Classes for Containers](https://docs.python.org/3/library/collections.abc.html)
- [`typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [`typing.Self`](https://docs.python.org/3/library/typing.html#typing.Self)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/11_typing_protocols_and_di/`](../../exercises/11_typing_protocols_and_di/README.md).
