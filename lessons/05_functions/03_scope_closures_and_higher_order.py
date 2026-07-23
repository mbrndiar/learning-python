"""
Chapter 5, Lesson 3: Scope, Closures, and Higher-Order Functions

Purpose: cover the LEGB name-lookup order, closures and `nonlocal`,
functions as first-class values, callbacks, lambdas, and the difference
between mutating a parameter and rebinding it.

Prerequisites: 02_parameter_kinds_and_unpacking.py.

Read this file top to bottom, predict each output, then run it:

    python lessons/05_functions/03_scope_closures_and_higher_order.py
"""

# Step 1: LEGB -- Local, Enclosing, Global, Built-in -- is the order Python
# searches when a name is read. A name assigned inside a function is Local
# to that function by default, and does not affect a same-named variable
# outside it.
topic = "outer"


def show_local_shadow():
    topic = "inner"  # a new Local name, unrelated to the outer `topic`
    return topic


assert show_local_shadow() == "inner"
assert topic == "outer"  # unaffected by the function's local assignment


# Step 2: a closure is a function that remembers variables from the scope
# it was defined in, even after that outer call has returned. Each call to
# make_multiplier creates a distinct enclosing `factor` -- the returned
# functions do not share state with each other.
def make_multiplier(factor):
    def multiplier(number):
        return number * factor  # `factor` is found in the Enclosing scope

    return multiplier


double = make_multiplier(2)
triple = make_multiplier(3)
assert double(5) == 10
assert triple(5) == 15


# Step 3: assigning to an enclosing variable from inside a nested function
# needs `nonlocal` -- without it, `count += 1` would try to create a new
# Local `count` before it has a value, raising UnboundLocalError.
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


counter = make_counter()
assert counter() == 1
assert counter() == 2
assert counter() == 3


# Step 4: functions are ordinary values -- they can be stored in variables,
# put into collections, and passed to other functions as arguments (this
# is called a callback). A "higher-order function" is one that accepts or
# returns another function, like sorted() with its `key` callback.
def shout(text):
    return text.upper() + "!"


def whisper(text):
    return text.lower() + "..."


greeters = [shout, whisper]  # a list of function objects, not calls
assert greeters[0]("hello") == "HELLO!"
assert greeters[1]("HELLO") == "hello..."

words = ["banana", "kiwi", "apple", "fig"]
by_length = sorted(words, key=len)  # `len` itself, passed as a callback
assert by_length == ["fig", "kiwi", "apple", "banana"]


# Step 5: a lambda is a small, anonymous, single-expression function --
# used here only after `def` is well established, and only for short
# throwaway callbacks. Anything needing a docstring, multiple statements,
# or reuse in several places should be a `def` instead.
by_last_letter = sorted(words, key=lambda word: word[-1])
assert by_last_letter == ["banana", "apple", "fig", "kiwi"]


# Step 6: passing a mutable object (like a list) to a function lets the
# function mutate it in place -- visible to the caller. But *rebinding*
# the parameter name inside the function (assigning it a brand-new object)
# only changes the local name; the caller's object is untouched.
def append_marker(items):
    items.append("done")  # mutates the caller's list in place


def replace_with_new_list(items):
    items = ["replacement"]  # rebinds the local name only
    return items


tracked = ["step-1"]
append_marker(tracked)
assert tracked == ["step-1", "done"]  # visible: mutation, not rebinding

replaced = replace_with_new_list(tracked)
assert tracked == ["step-1", "done"]  # unaffected: only the parameter was rebound
assert replaced == ["replacement"]

# --- One-variable experiment -------------------------------------------
# Change Step 4's `key=len` to `key=lambda word: len(word)` and predict
# whether `by_length` changes -- `len` and `lambda word: len(word)` are
# different objects but describe the same computation.

print("double(5) =", double(5))
print("triple(5) =", triple(5))
print("counter() x3 already called; next:", counter())
print("by_length:", by_length)
print("by_last_letter:", by_last_letter)
print("tracked after append_marker + replace_with_new_list:", tracked)
