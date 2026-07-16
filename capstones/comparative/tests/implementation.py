"""Select exactly one comparative capstone source root for shared tests."""

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
sys.path.insert(0, str(SOURCE_ROOT))
