"""
example_package -- a tiny package used in Chapter 6.

``__init__.py`` marks this directory as a regular Python package and runs
once, the first time any module inside the package is imported. Re-exporting
names here lets callers write ``from example_package import hello`` instead
of the longer ``from example_package.greetings import hello``.

``__all__`` lists the names that ``from example_package import *`` would
expose. It is **not** an access-control mechanism -- callers can still import
anything explicitly. Its purpose is to document the public surface and keep
wildcard imports predictable (wildcard imports are still discouraged even
with ``__all__`` present, because explicit imports show where a name came
from).
"""

from .greetings import hello, shout_hello

__all__ = ["hello", "shout_hello"]
