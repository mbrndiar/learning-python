"""
Lesson 5.5: Packages and Import Styles

A module is a single .py file.  A package is a directory that groups related
modules and is traditionally marked by an __init__.py file.  This lesson uses
the tiny ``example_package/`` that lives alongside this file to demonstrate
absolute imports, relative imports, package-level re-exports, and the leading-
underscore naming convention.

Run from the repository root:

    python lessons/05_modules_and_files/05_packages.py
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Making example_package importable from this standalone lesson script
# ---------------------------------------------------------------------------
# This directory's name starts with a digit, so Python cannot load it as part
# of a dotted package path.  Adding it to sys.path is the pragmatic fix for a
# self-contained lesson script.
#
# In a real project you would NOT manipulate sys.path like this.  Instead you
# would install the package (e.g. ``pip install -e .``) or run modules from
# the project root with ``python -m package.module`` so Python's import
# machinery handles the path automatically.
sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Absolute imports
# ---------------------------------------------------------------------------
# Once the package's parent directory is on sys.path, Python resolves the
# full dotted path from that directory.  These are called absolute imports
# because the path starts at a known root rather than relative to the
# current file.
from example_package.greetings import hello

# The package's __init__.py re-exports hello and shout_hello, so the shorter
# form below is equally valid.  Use whichever path is clearest:
#   from example_package import shout_hello
#
# In a real project the root package would typically be one name (e.g.
# ``myapp``), so absolute imports look like: from myapp.greetings import hello

# ---------------------------------------------------------------------------
# Import-time execution and caching
# ---------------------------------------------------------------------------
# Importing a module runs its top-level code exactly once per process.  The
# resulting module object is stored in sys.modules.  Subsequent imports of the
# same name return the cached object without re-running the file.
cached_after_first_import = "example_package.greetings" in sys.modules

# ---------------------------------------------------------------------------
# Public/internal naming convention
# ---------------------------------------------------------------------------
# Names that begin with a single underscore (e.g. _formatting._shout) signal
# "internal implementation detail—not part of the public API".  Python does
# NOT enforce this: you can still import them explicitly.  It is a convention
# that tools, linters, and human readers respect.
#
# See example_package/_formatting.py for examples.

# ---------------------------------------------------------------------------
# Relative imports (inside a package only)
# ---------------------------------------------------------------------------
# Inside a package module you use a leading dot to refer to siblings:
#
#   from .greetings import hello       # sibling module in this package
#   from ._formatting import _shout    # another sibling (internal)
#   from ..other_pkg import thing      # sibling of the parent package
#
# The dot means "current package".  Without the dot:
#
#   from greetings import hello
#
# Python searches sys.path for a top-level module called ``greetings``.
# That may import the wrong thing or raise ImportError.
#
# Open example_package/greetings.py and notice its own import:
#
#   from ._formatting import _shout, _titlecase
#
# Relative imports work only when a file is loaded as part of a package
# (via ``import`` or ``python -m``).  Running a file directly with
# ``python path/to/package/module.py`` sets __package__ to None, which
# breaks relative imports.  That is why package-internal modules are
# launched with:
#
#   python -m package.module
#
# rather than:
#
#   python path/to/package/module.py

# ---------------------------------------------------------------------------
# __all__ and wildcard imports
# ---------------------------------------------------------------------------
# Both example_package/__init__.py and example_package/greetings.py define
# __all__.  Its only effect is controlling ``from module import *``: names
# absent from __all__ are skipped by a wildcard import.  It is NOT access
# control—any name can still be imported explicitly regardless of __all__.
#
# Wildcard imports (``from module import *``) are discouraged because they
# make it hard to tell where a name came from.  Explicit imports are always
# preferable.

if __name__ == "__main__":
    print(hello("ada lovelace"))

    # Import the re-exported shout_hello from the package's public interface.
    from example_package import shout_hello

    print(shout_hello("grace hopper"))

    # Demonstrate that the module was cached after the first import above.
    print(
        "greetings cached in sys.modules:",
        "example_package.greetings" in sys.modules,
    )

    # Demonstrate that internal helpers can still be imported explicitly.
    from example_package._formatting import _shout

    print("_shout is still reachable:", _shout("hello"))
