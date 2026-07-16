"""Flask application-factory boundary for milestone four."""

import importlib
from typing import NoReturn

from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_app(service: TaskService) -> object:
    """Create the Flask application after the optional dependency is requested."""

    importlib.import_module("flask")
    del service
    incomplete("milestone 4 Flask application factory")


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """Own the educational Flask development-server lifecycle."""

    del service, host, port
    incomplete("milestone 4 Flask server lifecycle")


__all__ = ["create_app", "serve"]
