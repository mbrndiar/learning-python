"""Session fixtures exposing the implementation selected during collection.

``implementation`` mutates the import path before test modules import public
packages.  These fixtures share that single decision without re-selecting a
tree per test, which would mix starter and solution modules in ``sys.modules``.
"""

from pathlib import Path

import pytest
from implementation import IMPLEMENTATION, SOURCE_ROOT


@pytest.fixture(scope="session")
def implementation_name() -> str:
    """Return the stable starter-or-solution choice for marker-aware tests."""

    return IMPLEMENTATION


@pytest.fixture(scope="session")
def source_root() -> Path:
    """Return the sole public-package root used by this pytest session."""

    return SOURCE_ROOT
