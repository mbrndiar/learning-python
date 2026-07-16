"""Select one implementation tree before any public Task package is imported.

The starter and solution intentionally expose the same import surface, so the
suite switches only the source root rather than duplicating tests.  The starter
is expected to fail selected milestone behavior with explicit guided errors;
choosing it here must not accidentally fall through to completed solution code.
"""

import os
import sys
from pathlib import Path

IMPLEMENTATION_ENV = "PROJECT_IMPLEMENTATION"
VALID_IMPLEMENTATIONS = ("starter", "solution")

IMPLEMENTATION = os.environ.get(IMPLEMENTATION_ENV, "solution")
if IMPLEMENTATION not in VALID_IMPLEMENTATIONS:
    choices = "|".join(VALID_IMPLEMENTATIONS)
    raise RuntimeError(f"{IMPLEMENTATION_ENV} must be {choices}")

SOURCE_ROOT = Path(__file__).resolve().parents[1] / IMPLEMENTATION
# Prepending is the isolation boundary: every later ``tasks_*`` import must
# resolve from the selected tree even when another copy is already importable.
sys.path.insert(0, str(SOURCE_ROOT))

__all__ = [
    "IMPLEMENTATION",
    "IMPLEMENTATION_ENV",
    "SOURCE_ROOT",
    "VALID_IMPLEMENTATIONS",
]
