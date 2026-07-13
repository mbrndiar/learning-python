# Module 3: Functions

How to package reusable logic into functions, and a few more advanced
function-related tools.

## Learning objectives

After this module, you should be able to define focused functions, pass
arguments correctly, return results, reason about scope, and recognize
closures, lambdas, and recursion.

## Defining a function

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

## Scope and the LEGB rule

Name lookup proceeds through Local, Enclosing, Global, and Built-in scopes.
Assignment inside a function creates a local name unless `global` or
`nonlocal` says otherwise. Prefer returning values over modifying globals.
A closure is an inner function that retains access to names from an enclosing
function even after that function returns.

## Flexible calls and higher-order functions

`*args` collects extra positional arguments into a tuple; `**kwargs` collects
extra keyword arguments into a dictionary. The same `*` and `**` syntax
unpacks iterables and mappings at a call site. Functions can be assigned,
stored, passed to other functions, and returned. A `lambda` is a single
expression that creates an anonymous function; use `def` when logic or
documentation is nontrivial.

Recursion solves a problem through smaller instances of itself. It requires a
base case and progress toward that case. Python does not optimize tail calls,
so iteration is usually safer for deeply repeated work.

## Concepts covered

- **`01_functions.py`** - defining and calling functions, default and
  keyword arguments, and variable-length arguments with `*args` and
  `**kwargs`.
- **`02_lambdas_closures_and_recursion.py`** - lambda expressions
  (small anonymous functions, often used with `sorted()`, `map()` and
  `filter()`), closures (including the `nonlocal` keyword) and recursive
  functions.

## Running

```bash
python lessons/03_functions/01_functions.py
python lessons/03_functions/02_lambdas_closures_and_recursion.py
```

Once you've read through both files, practice what you learned in
[`exercises/03_functions/`](../../exercises/03_functions/README.md).

## Common mistakes

- Printing a value when the caller needs the function to return it.
- Calling a function in a default argument and expecting it to run per call.
- Using a list or dictionary as a default parameter.
- Forgetting the base case in recursion.
- Giving a function multiple unrelated responsibilities.

## Review questions

1. What does a function return when it reaches the end without `return`?
2. In what order does Python resolve an unqualified name?
3. Why can a mutable default argument retain data between calls?
4. How do `*args` and `**kwargs` differ?
5. What two properties must a terminating recursive function have?
