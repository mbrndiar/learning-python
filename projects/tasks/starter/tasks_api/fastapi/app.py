"""Typed FastAPI boundary for milestone five."""

import importlib
from typing import NoReturn

from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_app(service: TaskService) -> object:
    """Create the FastAPI application after the dependency is requested."""

    importlib.import_module("fastapi")
    del service
    incomplete("milestone 5 FastAPI application factory")


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """Own the educational Uvicorn lifecycle."""

    del service, host, port
    incomplete("milestone 5 FastAPI server lifecycle")


__all__ = ["create_app", "serve"]
