"""Milestones three-through-five black-box HTTP contract placeholder."""

from typing import NoReturn, Protocol

import pytest


class ServerHandle(Protocol):
    @property
    def base_url(self) -> str: ...

    def close(self) -> None: ...


class ServerFactory(Protocol):
    def __call__(self) -> ServerHandle: ...


def run_http_contract(server_factory: ServerFactory) -> NoReturn:
    """Reserve the shared server contract without starting network resources."""

    del server_factory
    pytest.skip("black-box HTTP behavior begins in milestone 3")


__all__ = ["ServerFactory", "ServerHandle", "run_http_contract"]
