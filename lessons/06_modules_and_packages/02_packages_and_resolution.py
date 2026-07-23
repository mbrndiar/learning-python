"""
Chapter 6, Lesson 2: Packages and Import Resolution

Purpose: introduce package layout, `__init__.py`, absolute imports, relative
imports, and running a package with `python -m`.

Prerequisites: Lesson 1 (modules and imports). This lesson uses the tiny
`example_package/` that lives alongside this file.

Read this file top to bottom, predict each output, then run it:

    python lessons/06_modules_and_packages/02_packages_and_resolution.py
"""

# Step 1: a *module* is a single .py file; a *package* is a directory that
# groups related modules and is marked by an `__init__.py` file (even an
# empty one). Open example_package/ alongside this file:
#
#   example_package/
#       __init__.py      # runs once, on first import; re-exports the API
#       __main__.py       # runs when the package itself is executed
#       greetings.py      # the public module: hello(), shout_hello()
#       _formatting.py    # an internal module: leading underscore = detail
#
# When Python runs this lesson by file path, it automatically searches the
# directory containing the script. That makes the sibling `example_package`
# importable without any path manipulation.

# Step 2: absolute imports name the full dotted path from a location Python
# already knows how to find (here, this script's automatically searched
# directory).
# __init__.py also re-exports hello and shout_hello, so the package's public
# surface reaches shout_hello without naming the internal greetings module.
# Internal names are still importable explicitly -- the underscore in
# _formatting is a convention, not an enforced boundary.
from example_package import shout_hello
from example_package._formatting import _shout
from example_package.greetings import hello

print("Absolute import -- hello('ada lovelace'):", hello("ada lovelace"))

# Re-exported import -- shout_hello reaches greetings.shout_hello through the
# package's __init__.py instead of its internal module path. Prefer this
# form when a package documents one.
print("Re-exported import -- shout_hello('grace hopper'):", shout_hello("grace hopper"))

# Step 3: relative imports. Open example_package/greetings.py and notice:
#
#   from ._formatting import _shout, _titlecase
#
# The leading dot means "look inside this package" rather than searching
# sys.path for a top-level module named `_formatting`. Relative imports are
# valid ONLY in a module that Python loaded as part of a package -- that is,
# via `import` or `python -m`, which set that module's `__package__`.
# Running a file directly as a script (`python path/to/module.py`) sets
# `__package__` to None, which breaks any relative import inside it. That
# constraint is exactly why package-internal modules are launched with
# `python -m package.module` rather than `python path/to/package/module.py`.
print("Internal helper is still reachable:", _shout("hello"))

# Step 4: `python -m` runs a module or package as the program's entry point
# and sets up package-relative imports correctly, unlike running a .py file
# by its bare path. example_package/__main__.py makes the package itself
# runnable this way. Run the printed command after this lesson; process
# creation itself is taught later, so this file does not hide it behind
# `subprocess.run`.
print("\nNext command:")
print("(cd lessons/06_modules_and_packages && python -m example_package)")

# --- One-variable experiment -------------------------------------------
# Run `python lessons/06_modules_and_packages/example_package/__main__.py`
# instead of the `python -m` command and predict what error appears.
# __main__.py's `from example_package import hello` is an absolute
# import of its own package, which needs example_package's *parent*
# directory on sys.path -- something `-m` arranges automatically from the
# current working directory, but a bare file path does not.
