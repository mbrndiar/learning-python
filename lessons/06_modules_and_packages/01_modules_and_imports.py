"""
Chapter 6, Lesson 1: Modules and Imports

Purpose: introduce a module as an ordinary object, the import cache in
`sys.modules`, the four import forms, and why namespacing avoids collisions
between names defined in different modules.

Prerequisites: Chapters 1-5 (values through functions). This is the first
lesson in the whole course to use `import` deliberately as its subject,
rather than as an incidental tool.

Read this file top to bottom, predict each output, then run it:

    python lessons/06_modules_and_packages/01_modules_and_imports.py
"""

import math
import random as rng  # "import ... as ...": bind a chosen local name
import sys
from datetime import date  # "from ... import ...": bind one name directly
from datetime import timedelta as delta  # combine both: aliased direct import

# Step 1: `import math` (above) binds the name `math` to a *module object*. A
# module object is not special syntax -- it is a regular Python object, with
# its own type, that happens to hold the names defined by executing math's
# source (mostly written in C for math, but the model is the same as a .py
# file).
print("type(math):", type(math))
print("math.pi:", math.pi)
print("math.sqrt(16):", math.sqrt(16))

# Step 2: the first `import math` anywhere in this process ran math's
# top-level code once and stored the resulting module object in
# `sys.modules`, keyed by module name. Every later `import math` -- in this
# file or any other module in the same process -- looks up that cached
# object instead of re-running it.
assert "math" in sys.modules
assert sys.modules["math"] is math
cached_math = sys.modules["math"]
print("\nCached module is the same object:", cached_math is math)

# --- One-variable experiment -------------------------------------------
# Change `import math` to `import math as m` above and use `m.pi` below.
# The cache key in sys.modules is still "math" -- only the *local name*
# bound in this file changes. The module itself is identical either way.


# Step 3: the four import forms bind names differently, but every one of
# them causes the target module to be imported (and cached) the same way --
# `import random as rng`, `from datetime import date`, and `from datetime
# import timedelta as delta` above are three of the four forms; plain
# `import math` above was the first.
print("\nrandom module aliased as rng:", type(rng))
print("date imported directly:", date(2024, 1, 1).isoformat())
print("timedelta aliased as delta:", delta(days=1))


# Step 4: namespacing. Importing the whole module (`import math`) keeps its
# names behind `math.`, so `math.sqrt` cannot collide with an unrelated
# `sqrt` defined elsewhere. Importing a name directly (`from math import
# sqrt`) drops that prefix -- convenient, but now `sqrt` in this file's
# namespace *is* math's function, and a later `sqrt = ...` would shadow it.
def sqrt(value):
    """A module-level function that happens to share math.sqrt's name."""
    return f"custom sqrt of {value}"


print("\nLocal sqrt(9):", sqrt(9))
print("math.sqrt(9):", math.sqrt(9))
# Because math was imported as a whole module, the two `sqrt`s coexist
# without conflict -- this is exactly what namespacing buys you. Had this
# file instead done `from math import sqrt`, the def above would have
# silently replaced it, and math.sqrt would need `math.sqrt(9)` again to
# reach the original (which remains reachable through the module object).

# Step 5: dir() lists every name currently bound in a module's namespace.
# It is a debugging/exploration tool, not something you call in ordinary
# code -- but it makes the "module holds names" model concrete.
sample_names = [name for name in dir(rng) if name in ("randint", "choice", "seed")]
print("\nA few names inside the random module:", sorted(sample_names))

rng.seed(0)  # fix the seed so this lesson's output is reproducible
print("\nSeeded random number between 1 and 10:", rng.randint(1, 10))
