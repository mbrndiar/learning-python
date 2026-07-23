# 🧩 Chapter 5: Function Contracts and Scope

**Semantic ID:** `module.function-contracts-and-scope` · **Prerequisites:**
`module.flow-and-iteration`

## 📍 Where this fits

Chapters 1-4 built every program as a flat sequence of top-level statements,
loops, and branches -- useful logic could only be reused by copying it.
This chapter introduces `def`: packaging logic behind a name and a call
contract (parameters in, a return value out), so it can be reused, tested,
composed, and reasoned about independently of where it is called from. This
is the first chapter in the whole course where you write your own
function definitions.

## 🎯 Learning objectives

After this chapter, you should be able to:

- define a function with `def`, call it, and explain the difference
  between a pure function and one with side effects;
- read and write basic `name: type -> type` annotations, and explain that
  Python does not enforce them at runtime;
- use default values, positional-only (`/`) and keyword-only (`*`)
  parameters, `*args`, and `**kwargs`;
- unpack a list or dict into a function call with `*`/`**`;
- explain the LEGB name-lookup order and trace a closure that captures an
  enclosing variable, including one that uses `nonlocal`;
- pass a function as a value (a callback), as with `sorted(..., key=...)`;
- write a small `lambda` only where a full `def` would be overkill;
- explain the difference between mutating a parameter and rebinding it;
- write a recursive function with a correct base case and progress, and
  explain when an iterative version would be clearer.

## 🧠 Motivation and mental model

A function is a contract: given these inputs, in this shape, I will
produce that output (or perform that effect), and nothing else you didn't
ask for. Naming a piece of logic and giving it a contract is what allows
you to stop thinking about *how* `sorted(..., key=len)` sorts, and start
thinking only about *what* `len` contributes to each comparison. Every
concept in this chapter builds toward that: parameters describe the
contract's inputs, `return` describes its output, scope describes what a
function can see and change, and higher-order functions describe how
functions themselves become interchangeable inputs.

## 🧩 Progressive syntax and mechanism

1. **Definition, call, return.** `def name(parameters): body`; a call
   creates a fresh set of local bindings and runs the body up to a
   `return` (or the end, which returns `None`); pure functions avoid
   observable side effects.
2. **Basic annotations.** `def f(x: int) -> int:` documents the intended
   contract without runtime enforcement.
3. **Parameter kinds.** Default values (evaluated once, at `def` time);
   `/` for positional-only; `*` for keyword-only; `*args` for extra
   positional arguments as a tuple; `**kwargs` for extra keyword arguments
   as a dict.
4. **Call-site unpacking.** `f(*a_list, **a_dict)` spreads an existing
   collection into positional/keyword arguments -- the reverse direction
   of `*args`/`**kwargs` collecting them.
5. **Scope: LEGB.** Local names shadow Enclosing, Global, and Built-in
   names; a closure remembers its enclosing scope's variables after that
   call has returned; `nonlocal` is required to assign (not just read) an
   enclosing variable.
6. **Functions as values.** Functions can be stored, put in collections,
   and passed as callbacks; `lambda parameters: expression` is a small
   anonymous function, used only for short throwaway callbacks.
7. **Mutation versus rebinding.** Mutating a mutable parameter in place is
   visible to the caller; assigning a new object to the parameter name
   only rebinds that local name.
8. **Recursion.** A base case that stops the recursion, and progress that
   moves every call closer to it; each active call holds its own stack
   frame; recursion suits naturally recursive shapes (like nested data)
   more than simple accumulation, where iteration is usually clearer.

## 📖 Read-predict-run-modify workflow

Work through the four lesson files in order, predicting each output before
running:

```bash
python lessons/05_functions/01_function_contracts.py
python lessons/05_functions/02_parameter_kinds_and_unpacking.py
python lessons/05_functions/03_scope_closures_and_higher_order.py
python lessons/05_functions/04_recursion.py
```

### Expected output highlights

- `01_function_contracts.py`: `announce("Lesson started")` prints its
  message and returns `None`; `announce_result` is asserted `is None`.
- `02_parameter_kinds_and_unpacking.py`:
  `format_measurement(12.345, "cm", precision=2)` prints `"12.35 cm"` --
  standard `round-half-to-even`-adjacent float formatting, not a typo.
- `03_scope_closures_and_higher_order.py`: `double` and `triple` are two
  independent closures from two separate calls to `make_multiplier`, and
  do not share captured state; `counter()` increases by one on each call
  because of `nonlocal`.
- `04_recursion.py`: `sum_nested([1, [2, 3], [4, [5, 6]]])` returns `21`
  by recursing into each nested list in turn.

## 🔁 Transition to Chapter 6

This chapter packaged logic behind function contracts within a single
file. Chapter 6, Modules and Packages, packages *files* behind import
contracts, so functions (and everything else) can be reused across files
and projects, not just within one script.

## ⚠️ Common mistakes

- Forgetting that a mutable default argument is evaluated once, at `def`
  time, and shared across every call that doesn't override it (an
  immutable default, as used in this chapter, avoids the pitfall).
- Assigning to an enclosing variable inside a nested function without
  `nonlocal`, causing `UnboundLocalError` instead of the intended update.
- Assuming annotations like `-> float` are enforced; they are not checked
  at runtime.
- Confusing "mutating a parameter in place" (visible to the caller) with
  "rebinding a parameter to a new object" (local only).
- Writing a recursive function with a base case that is never reached, or
  a recursive call that does not shrink the problem, causing
  `RecursionError`.

## 🧾 Summary

- `def` creates a function contract: parameters in, a return value (or
  `None`) out.
- Parameter kinds (`/`, `*`, `*args`, `**kwargs`) and call-site unpacking
  (`*`, `**`) control exactly how arguments may be supplied.
- LEGB governs name lookup; closures and `nonlocal` let a nested function
  read and update its enclosing scope.
- Functions are ordinary values -- they can be passed as callbacks, and
  `lambda` covers short, throwaway cases.
- Recursion needs a base case and progress toward it; it is not always the
  clearer choice over iteration.

## ❓ Review questions (closed notes)

1. What is the difference between a pure function and one with side
   effects?
2. What does the `/` in a parameter list mean? What does a bare `*` mean?
3. Why does `nonlocal` exist, and what error appears without it in
   `make_counter`'s `increment`?
4. What is the difference between mutating a parameter and rebinding it?
5. What two properties must a recursive function have to terminate
   correctly?
6. When would you prefer an iterative solution over a recursive one?

## 📚 Authoritative references

- [Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [More on Defining Functions (parameter kinds)](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions)
- [Unpacking Argument Lists](https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists)
- [Python Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
- [Lambda Expressions](https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions)
- [`sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit) and
  [Design and History FAQ: recursion limit](https://docs.python.org/3/faq/design.html)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/05_functions/`](../../exercises/05_functions/README.md).
