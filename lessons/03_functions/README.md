# 🧩 Module 3: Functions

How to package reusable logic into functions, and a few more advanced
function-related tools.

## 🎯 Learning objectives

After this module, you should be able to define focused functions, pass
arguments according to an explicit call contract, explain mutation versus
rebinding, return results, reason about scope, and recognize closures, lambdas,
and recursion.

## 🛠️ Defining a function

A function is an object created by `def`. Parameters name incoming values;
`return` sends one result to the caller and immediately ends the call. A
function with no explicit `return` returns `None`.

```python
def area(width, height=1):
    """Return the area of a rectangle."""
    return width * height

area(4, 3)         # positional arguments
area(width=4)      # keyword argument and default height
```

Arguments are bound to local names. Python passes object references by
assignment: mutating a passed list is visible to the caller, but rebinding the
local parameter is not. Avoid mutable default values:

```python
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Make the call contract visible

A parameter before `/` is positional-only. A parameter after a bare `*` is
keyword-only. Parameters between them accept either form:

```python
def connect(host, /, port=443, *, timeout=5.0):
    return host, port, timeout

connect("example.com", 8443, timeout=2.0)
```

This is useful when a parameter name is an implementation detail or when a
keyword makes an option clearer at the call site. It is separate from `*args`
and `**kwargs`, which collect an arbitrary number of arguments.

## 🔭 Scope and the LEGB rule

Name lookup proceeds through Local, Enclosing, Global, and Built-in scopes.
Assignment inside a function creates a local name unless `global` or
`nonlocal` says otherwise. Prefer returning values over modifying globals.
A closure is an inner function that retains access to names from an enclosing
function even after that function returns. Each call can create a separate
captured environment: `make_multiplier(2)` and `make_multiplier(3)` return
functions with the same code but different remembered `factor` values.

## 🧰 Flexible calls and higher-order functions

`*args` collects extra positional arguments into a tuple; `**kwargs` collects
extra keyword arguments into a dictionary. The same `*` and `**` syntax
unpacks iterables and mappings at a call site, where Python then applies the
ordinary signature rules. Functions can be assigned, stored, passed to other
functions, and returned. A `lambda` is a single expression that creates an
anonymous function; use `def` when logic or documentation is nontrivial.

Recursion solves a problem through smaller instances of itself. It requires a
base case and progress toward that case. Python does not optimize tail calls,
so iteration is usually safer for deeply repeated work.

Follow a small call before trusting the abstraction:

```text
factorial(4)
→ 4 * factorial(3)
→ 4 * 3 * factorial(2)
→ 4 * 3 * 2 * factorial(1)
→ 24
```

The return values resolve in the opposite direction from the calls. The lesson's
recursive Fibonacci function is intentionally simple, but it repeats the same
subproblems many times. Use it to understand the call tree, not as an efficient
implementation for large inputs.

## 📚 Concepts covered

- **`01_functions.py`** - defining and calling functions, positional-only and
  keyword-only parameters, defaults, argument unpacking, variable-length
  arguments, binding by assignment, and explicit or implicit return values.
- **`02_lambdas_closures_and_recursion.py`** - lambda expressions
  (small anonymous functions, often used with `sorted()`, `map()` and
  `filter()`), closures (including the `nonlocal` keyword) and recursive
  functions.

## ▶️ Running

```bash
python lessons/03_functions/01_functions.py
python lessons/03_functions/02_lambdas_closures_and_recursion.py
```

Once you've read through both files, practice what you learned in
[`exercises/03_functions/`](../../exercises/03_functions/README.md).

## ⚠️ Common mistakes

- Printing a value when the caller needs the function to return it.
- Calling a positional-only parameter by name, or omitting the name of a
  keyword-only argument.
- Calling a function in a default argument and expecting it to run per call.
- Using a list or dictionary as a default parameter.
- Expecting rebinding a parameter to replace the caller's object.
- Forgetting the base case in recursion.
- Giving a function multiple unrelated responsibilities.

## ❓ Review questions

1. What does a function return when it reaches the end without `return`?
2. In what order does Python resolve an unqualified name?
3. Why can a mutable default argument retain data between calls?
4. How do `*args` and `**kwargs` differ?
5. How do `/` and a bare `*` constrain a call?
6. Why can mutating a passed list affect the caller while rebinding the
   parameter cannot?
7. What two properties must a terminating recursive function have?
