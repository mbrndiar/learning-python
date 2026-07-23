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

## 🧩 Progressive syntax and mechanism

1. **Annotations are optional and unenforced.** Python runs annotated
   code exactly the same whether or not the hints are honored; only
   external tools (mypy, IDEs) check them.
2. **Unions and `None`.** `X | None` documents that a value may be
   absent; `is None`/`is not None` narrows the union so each branch can
   be treated as one definite type.
3. **Type aliases.** `UserMap = dict[int, str]` names a shape once so
   signatures referencing it stay readable.
4. **Abstract collection types.** `Iterable` promises only "usable with
   `for`"; `Sequence` adds ordered indexing and `len()`; `Mapping`
   promises read-only key lookup -- choose the narrowest one a function
   body actually needs.
5. **`Callable`.** `Callable[[int], int]` annotates a parameter that must
   itself be callable with that exact argument/return shape.
6. **Generic functions.** `TypeVar("T")` plus `Sequence[T] -> T` ties a
   function's return type to whatever type was actually passed in, from
   one shared definition.
7. **`Literal`.** Narrows a type to a closed set of exact values (e.g.
   `Literal["read", "write", "append"]`), not just "any string."
8. **`Annotated`.** Attaches metadata to a type without changing what the
   type itself is at runtime -- the same mechanism a validation
   framework reads to auto-generate checks.
9. **`Self`.** Documents that a method (like a chained builder method)
   returns an instance of whatever class it was actually called on,
   including a subclass.
10. **`Protocol` and structural typing.** A class satisfies a `Protocol`
    by having matching methods, with no inheritance required.
11. **Dependency injection and adapters.** Passing a collaborator into an
    object (instead of constructing one internally) decouples behavior
    from a specific implementation; an adapter translates an existing,
    unrelated interface into the one a `Protocol` requires.

## 📖 Read-predict-run-modify workflow

Work through all four lesson files in order, predicting each output
before running:

```bash
python lessons/11_typing_protocols_and_di/01_annotations_and_narrowing.py
python lessons/11_typing_protocols_and_di/02_collections_callables_and_generics.py
python lessons/11_typing_protocols_and_di/03_literal_annotated_and_self.py
python lessons/11_typing_protocols_and_di/04_protocols_adapters_and_dependency_injection.py
```

### Expected output highlights

- `01_annotations_and_narrowing.py`: `add('2', '3')` prints `23` (string
  concatenation) despite `add`'s `int` hints -- Python never checked
  them.
- `02_collections_callables_and_generics.py`: `total_length` accepts both
  a list and a generator expression, since its body only ever loops;
  `first_and_last` requires indexing, which only the list/tuple calls
  provide.
- `03_literal_annotated_and_self.py`: `type(named_builder).__name__`
  prints `NamedQueryBuilder`, not `QueryBuilder` -- `where()`'s `Self`
  return type followed the actual subclass through a chained call.
- `04_protocols_adapters_and_dependency_injection.py`: the exact same
  `ReminderService` class delivers a reminder through a console, a
  recording test double, and an adapted legacy notifier, without any
  change to `ReminderService` itself.

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
