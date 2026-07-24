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

## 📖 How to study this chapter

For each function, separate definition time from call time:

1. read the `def` header as the input contract;
2. identify which names become local parameters;
3. trace the body for one concrete call;
4. identify the returned value and any visible side effect;
5. run the companion and then make the suggested bounded change.

The indented body of a function does not run merely because Python reads its
definition. A call is what creates local bindings and executes that body.

## 1️⃣ Function definitions, calls, and returns

`def` creates a function object and binds it to a name:

```python
def greet(name):
    """Return a greeting for one name."""
    return f"Hello, {name}!"
```

The header ends with a colon. The indented block is the body. `name` is a
**parameter**: a local name that receives an argument when the function is
called.

Reading the definition produces no greeting. A call runs it:

```python
message = greet("Ada")
print(message)
```

1. `"Ada"` is bound to the local parameter `name`;
2. the f-string produces `"Hello, Ada!"`;
3. `return` ends the call and hands that value to the caller;
4. the caller binds it to `message` and prints it.

```text
Hello, Ada!
```

The triple-quoted string immediately inside the function is a **docstring**.
It documents the function's contract for readers and tools.

### Returning a value is different from printing

```python
def announce(message):
    print(f"Announcement: {message}")


result = announce("Lesson started")
print("result:", result)
```

```text
Announcement: Lesson started
result: None
```

`announce` has a visible side effect: it writes output. Because execution
reaches the end without `return value`, the call implicitly returns `None`.
Printing and returning are not interchangeable: returned values can be stored,
combined, asserted, or passed elsewhere; printed output is an effect.

### Pure functions isolate a calculation

```python
def square(number):
    return number**2


assert square(4) == 16
assert square(4) == 16
```

A **pure function** produces its result only from its arguments and has no
observable side effect. Calling it twice with the same input gives the same
result, which makes the contract straightforward to test and compose.

### Annotations document intended types

```python
def to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32
```

`celsius: float` documents the intended argument type; `-> float` documents the
intended return type. Python stores these annotations but does not enforce them
at runtime. The operations in the body still decide what a particular argument
can do.

For example, `to_fahrenheit("100")` is not rejected at the call boundary.
String repetition handles `"100" * 9`, but dividing the resulting string by
`5` raises `TypeError`. A type checker can catch the mismatch before runtime;
Chapter 11 introduces that tooling.

Run the complete companion:

```bash
python lessons/05_functions/01_function_contracts.py
```

See [`01_function_contracts.py`](01_function_contracts.py) for returned values,
side effects, purity, and executable annotation examples.

> **Try one change:** call `to_fahrenheit(20)` and predict the returned value
> before rerunning. Then explain why the annotation did not perform the
> calculation or validate the value itself.

## 2️⃣ Parameter kinds and call-site unpacking

A function's signature controls not only which values it accepts but how the
caller may supply them.

### Defaults make an argument optional

```python
def add(a, b=0):
    return a + b


print(add(2, 3))
print(add(5))
```

The outputs are `5` and `5`. The default is used only when the caller omits
`b`.

Default expressions are evaluated once, when the `def` statement runs.
Immutable defaults such as `0` are safe. A mutable default such as `items=[]`
would be one shared list across calls that omit the argument; later code should
use `None` and create a fresh list inside the function when that behavior is
not intended.

### `/` and `*` constrain the call syntax

```python
def format_measurement(value, /, unit="units", *, precision=1):
    return f"{value:.{precision}f} {unit}"


print(format_measurement(12.345, "cm", precision=2))
```

```text
12.35 cm
```

Read the markers from left to right:

- parameters before `/` are positional-only, so `value=12.345` is invalid;
- parameters between `/` and `*` may be positional or keyword arguments;
- parameters after `*` are keyword-only, so the caller must write
  `precision=2`.

An invalid call shape raises `TypeError` before the body runs.

### `*args` collects extra positional arguments

```python
def sum_all(*numbers):
    return sum(numbers)


print(sum_all(1, 2, 3, 4))
print(sum_all())
```

`numbers` is a tuple containing the supplied positional arguments. It is empty
when none are supplied, so the outputs are `10` and `0`.

### `**kwargs` collects extra keyword arguments

```python
def describe(**details):
    parts = []
    for key, value in details.items():
        parts.append(f"{key}={value}")
    return ", ".join(parts)


print(describe(name="Ada", age=36))
```

`details` is a dict whose insertion order matches the call, producing:

```text
name=Ada, age=36
```

The parameter forms **collect** many supplied arguments into one local
collection: `*args` into a tuple and `**kwargs` into a dict.

### Call-site `*` and `**` spread collections

The same symbols at a call site work in the reverse direction:

```python
def describe_person(name, age, city="Unknown"):
    return f"{name} is {age} years old and lives in {city}."


person = ("Sam", 28)
location = {"city": "Bristol"}
print(describe_person(*person, **location))
```

```text
Sam is 28 years old and lives in Bristol.
```

`*person` supplies two positional arguments; `**location` supplies the keyword
argument `city`. Supplying the same parameter twice -- once positionally and
again by keyword -- raises `TypeError`.

Run the complete companion:

```bash
python lessons/05_functions/02_parameter_kinds_and_unpacking.py
```

See
[`02_parameter_kinds_and_unpacking.py`](02_parameter_kinds_and_unpacking.py)
for all collection and spreading forms in executable calls.

> **Try one change:** change `precision=2` to `precision=1` in the
> `format_measurement` call. Predict both the formatting and why `precision`
> still must be named.

## 3️⃣ Scope, closures, and higher-order functions

Every function call creates a local namespace. When Python reads a name, it
searches scopes in **LEGB** order:

1. **Local** -- the current function call;
2. **Enclosing** -- surrounding function calls;
3. **Global** -- the module;
4. **Built-in** -- names such as `len` and `print`.

### A local binding can shadow an outer name

```python
topic = "outer"


def show_local_shadow():
    topic = "inner"
    return topic


print(show_local_shadow())
print(topic)
```

```text
inner
outer
```

Assignment inside the function creates a local `topic`. It does not rebind the
global name with the same spelling.

### A closure remembers its enclosing bindings

```python
def make_multiplier(factor):
    def multiplier(number):
        return number * factor

    return multiplier


double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))
print(triple(5))
```

`make_multiplier(2)` returns the inner function itself, not the result of
calling it. That function closes over its enclosing `factor` value. Separate
factory calls create independent enclosing bindings, so the outputs are `10`
and `15`.

### `nonlocal` permits rebinding an enclosing name

Reading an enclosing name needs no declaration. Assigning to it does:

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


counter = make_counter()
print(counter())
print(counter())
```

The output is `1` and then `2`. `nonlocal count` says that assignment should
update the nearest enclosing function binding. Without it, `count += 1` would
treat `count` as local while also trying to read it before assignment, raising
`UnboundLocalError`.

### Functions are values and can be callbacks

Writing a function name without parentheses refers to the function object:

```python
def shout(text):
    return text.upper() + "!"


operation = shout
print(operation("hello"))
```

The output is `HELLO!`. Because functions are values, they can be stored in
lists or passed to another function. A function that accepts or returns a
function is called **higher-order**:

```python
words = ["banana", "kiwi", "apple", "fig"]
by_length = sorted(words, key=len)
print(by_length)
```

`sorted` calls the `key` callback once per word and compares the returned
lengths. The result is `['fig', 'kiwi', 'apple', 'banana']`. Passing `len` is
different from calling `len(...)`; `sorted` chooses the argument later.

For a short, single-expression callback, `lambda` creates an anonymous
function:

```python
by_last_letter = sorted(words, key=lambda word: word[-1])
print(by_last_letter)
```

```text
['banana', 'apple', 'fig', 'kiwi']
```

Prefer `def` when the operation needs a name, docstring, multiple statements,
or reuse.

### Parameters follow mutation and rebinding rules

Parameters are local names bound to the caller's argument objects:

```python
def append_marker(items):
    items.append("done")


def replace_with_new_list(items):
    items = ["replacement"]
    return items


tracked = ["step-1"]
append_marker(tracked)
replacement = replace_with_new_list(tracked)

print(tracked)
print(replacement)
```

```text
['step-1', 'done']
['replacement']
```

The first function mutates the caller's list object. The second only rebinds
its local parameter and returns the new list; `tracked` remains unchanged by
that rebinding.

Run the complete companion:

```bash
python lessons/05_functions/03_scope_closures_and_higher_order.py
```

See
[`03_scope_closures_and_higher_order.py`](03_scope_closures_and_higher_order.py)
for executable checks of each scope and identity boundary.

> **Try one change:** replace `key=len` with
> `key=lambda word: len(word)`. Predict whether the order changes and explain
> why two different function objects can implement the same callback
> contract.

## 4️⃣ Recursion

A recursive function calls itself with a smaller instance of the same problem.
Correct recursion requires:

1. a **base case** that returns without another recursive call;
2. **progress** that moves every recursive call toward that base case.

### Factorial exposes the two requirements

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

For `factorial(3)`, calls build up until the base case:

```text
factorial(3)
3 * factorial(2)
3 * 2 * factorial(1)
3 * 2 * 1
6
```

Each active call has its own **stack frame**, including its own local `n`.
After `factorial(1)` returns, pending calls unwind in reverse order.

If the base case were missing, or the recursive argument did not get closer to
it, calls would continue until Python raised `RecursionError`.

### Iteration can be clearer for linear accumulation

```python
def factorial_iterative(n):
    result = 1
    for factor in range(2, n + 1):
        result *= factor
    return result
```

For a straight running product, this version states the mechanism directly and
does not consume one stack frame per factor. Recursion is not automatically
more elegant merely because it is possible.

### Nested data has a recursive shape

A nested list may contain either a number or another list needing the same
treatment:

```python
def sum_nested(values):
    total = 0
    for value in values:
        if isinstance(value, list):
            total += sum_nested(value)
        else:
            total += value
    return total


print(sum_nested([1, [2, 3], [4, [5, 6]]]))
print(sum_nested([]))
```

The outputs are `21` and `0`. An empty list reaches the base behavior
immediately: the loop has no passes, so the initial total is returned. A nested
list makes progress because the recursive call receives one inner, shallower
value rather than the unchanged outer input.

Python intentionally limits recursion depth (roughly one thousand calls under
the default configuration) so runaway recursion raises `RecursionError` before
exhausting the process's memory. Increasing that limit is not a substitute for
a missing base case or progress.

Run the complete companion:

```bash
python lessons/05_functions/04_recursion.py
```

See [`04_recursion.py`](04_recursion.py) for recursive and iterative factorial
side by side and a nested-list traversal.

> **Try one change:** call
> `sum_nested([1, [2, [3, [4, [5]]]]])`. Predict the total and explain why
> nesting depth changes the number of active calls.

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
