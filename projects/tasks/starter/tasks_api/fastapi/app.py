"""Typed FastAPI boundary for milestone five."""

import importlib
from typing import NoReturn

from fastapi import FastAPI
from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_app(service: TaskService) -> FastAPI:
    """Create the FastAPI application after the dependency is requested."""

    importlib.import_module("fastapi")
    del service
    # TODO(milestone 5): provide the injected service with Depends, add thin
    # typed routes, and centralize shared and unexpected exception handling.
    incomplete("milestone 5 FastAPI application factory")


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """Own the educational Uvicorn lifecycle."""

    del service, host, port
    # TODO(milestone 5): create the app, then run it with local Uvicorn.
    incomplete("milestone 5 FastAPI server lifecycle")


__all__ = ["create_app", "serve"]
