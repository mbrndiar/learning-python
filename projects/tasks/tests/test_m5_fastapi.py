"""Milestone five parser and placeholder checks for FastAPI and HTTPX."""

import pytest
from implementation import IMPLEMENTATION
from support import SERVER_ARGUMENTS, assert_client_parser, assert_server_parser
from tasks_api.fastapi.__main__ import build_parser as build_server_parser
from tasks_api.fastapi.__main__ import main as server_main
from tasks_cli.httpx.__main__ import build_parser as build_client_parser
from tasks_cli.httpx.__main__ import main as client_main
from tasks_core import IncompleteImplementationError

CLIENT_INCOMPLETE = (
    r"milestone 5 httpx call.*intentionally incomplete"
    if IMPLEMENTATION == "solution"
    else r"client command execution.*intentionally incomplete"
)


def test_fastapi_and_httpx_launchers_parse_without_optional_imports() -> None:
    assert_server_parser(build_server_parser())
    assert_client_parser(build_client_parser())


def test_fastapi_and_httpx_launchers_have_explicit_incomplete_smoke() -> None:
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 5 FastAPI server lifecycle.*intentionally incomplete",
    ):
        server_main(SERVER_ARGUMENTS)

    with pytest.raises(
        IncompleteImplementationError,
        match=CLIENT_INCOMPLETE,
    ):
        client_main(["complete", "1"])
