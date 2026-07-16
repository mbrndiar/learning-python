"""Milestones three-through-five client contract placeholder."""

from typing import NoReturn

import pytest
from tasks_cli.transport import TransportFactory


def run_client_contract(transport_factory: TransportFactory) -> NoReturn:
    """Reserve the shared client contract without asserting HTTP behavior."""

    del transport_factory
    pytest.skip("client transport behavior begins in milestone 3")


__all__ = ["run_client_contract"]
