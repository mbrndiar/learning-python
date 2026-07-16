"""Pytest fixtures for the selected Task project implementation."""

from pathlib import Path

import pytest
from implementation import IMPLEMENTATION, SOURCE_ROOT


@pytest.fixture(scope="session")
def implementation_name() -> str:
    """Return the selected source-root name."""

    return IMPLEMENTATION


@pytest.fixture(scope="session")
def source_root() -> Path:
    """Return the selected source-root path."""

    return SOURCE_ROOT
