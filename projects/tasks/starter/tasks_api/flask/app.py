"""Flask application-factory boundary for milestone four."""

from typing import NoReturn

from flask import Flask
from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_app(service: TaskService) -> Flask:
    """TODO: create a Flask app whose routes close over the injected service."""

    del service
    incomplete("milestone 4 Flask application factory")


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """TODO: run the local Flask server without debug mode or a reloader."""

    del service, host, port
    incomplete("milestone 4 Flask server lifecycle")


__all__ = ["create_app", "serve"]
