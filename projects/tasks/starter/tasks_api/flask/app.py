"""Flask application-factory boundary for milestone four."""

from typing import NoReturn

from flask import Flask
from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_app(service: TaskService) -> Flask:
    """TODO: create a Flask app whose thin routes use the injected service.

    Let Flask provide request/response mechanics, but keep the shared contract
    explicit: validate the JSON boundary, return documented statuses/envelopes,
    and centralize expected and unexpected exception translation.
    """

    del service
    incomplete("milestone 4 Flask application factory")


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """TODO: own one local Flask server without debug mode or a reloader.

    The reloader starts extra process state that would obscure ownership and make
    the educational launcher and its tests nondeterministic.
    """

    del service, host, port
    incomplete("milestone 4 Flask server lifecycle")


__all__ = ["create_app", "serve"]
