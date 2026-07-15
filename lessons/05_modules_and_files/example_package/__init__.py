"""
example_package – a tiny package used in lesson 5.2.

``__init__.py`` marks this directory as a regular Python package and can
re-export names so callers use ``from example_package import hello`` instead
of the longer ``from example_package.greetings import hello``.

``__all__`` lists the names that ``from example_package import *`` would
expose.  It is **not** an access-control mechanism—callers can still import
anything explicitly.  Its main purpose is to document the public surface and
to keep wildcard imports predictable (which is why wildcard imports are still
discouraged even when ``__all__`` is present).
"""

from .greetings import hello, shout_hello

__all__ = ["hello", "shout_hello"]
