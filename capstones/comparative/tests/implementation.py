"""Select one implementation root without mixing starter and solution modules.

The shared suite must exercise either tree as a complete unit.  Putting only the
chosen source root first on ``sys.path`` prevents imports from silently combining
modules from both implementations and hiding an incomplete or incompatible tree.
"""

import os
import sys
from pathlib import Path

IMPLEMENTATION_ENV = "CAPSTONE_IMPLEMENTATION"
VALID_IMPLEMENTATIONS = ("starter", "solution")

IMPLEMENTATION = os.environ.get(IMPLEMENTATION_ENV, "solution")
if IMPLEMENTATION not in VALID_IMPLEMENTATIONS:
    choices = "|".join(VALID_IMPLEMENTATIONS)
    raise RuntimeError(f"{IMPLEMENTATION_ENV} must be {choices}")

SOURCE_ROOT = Path(__file__).resolve().parents[1] / IMPLEMENTATION
# Child processes receive this same root through ``PYTHONPATH`` in support.py, so
# in-process imports and CLI invocations test the identical implementation.
sys.path.insert(0, str(SOURCE_ROOT))
