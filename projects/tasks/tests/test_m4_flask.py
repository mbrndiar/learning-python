"""Milestone four parser and placeholder checks for Flask and Requests."""

import pytest
from implementation import IMPLEMENTATION
from support import SERVER_ARGUMENTS, assert_client_parser, assert_server_parser
from tasks_api.flask.__main__ import build_parser as build_server_parser
from tasks_api.flask.__main__ import main as server_main
from tasks_cli.requests.__main__ import build_parser as build_client_parser
from tasks_cli.requests.__main__ import main as client_main
from tasks_core import IncompleteImplementationError

CLIENT_INCOMPLETE = (
    r"milestone 4 requests call.*intentionally incomplete"
    if IMPLEMENTATION == "solution"
    else r"client command execution.*intentionally incomplete"
)


def test_flask_and_requests_launchers_parse_without_optional_imports() -> None:
    assert_server_parser(build_server_parser())
    assert_client_parser(build_client_parser())


def test_flask_and_requests_launchers_have_explicit_incomplete_smoke() -> None:
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 4 Flask server lifecycle.*intentionally incomplete",
    ):
        server_main(SERVER_ARGUMENTS)

    with pytest.raises(
        IncompleteImplementationError,
        match=CLIENT_INCOMPLETE,
    ):
        client_main(["show", "1"])
