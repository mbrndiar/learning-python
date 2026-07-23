"""
A small facade module used by Lesson 3 to demonstrate re-exporting a name
from another module and declaring a public API with __all__.
"""

from greeting_module import get_greeting

# __all__ documents this module's intended public surface for
# `from facade import *`. It does not block `from facade import
# get_greeting` (already used explicitly elsewhere) nor
# `greeting_module.get_greeting` directly -- it only affects wildcard
# imports.
__all__ = ["get_greeting"]
