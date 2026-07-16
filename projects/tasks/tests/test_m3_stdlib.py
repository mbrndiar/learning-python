"""Milestone three parser and placeholder checks for stdlib adapters."""

import pytest
from support import SERVER_ARGUMENTS, assert_client_parser, assert_server_parser
from tasks_api.stdlib.__main__ import build_parser as build_server_parser
from tasks_api.stdlib.__main__ import main as server_main
from tasks_cli.urllib.__main__ import build_parser as build_client_parser
from tasks_cli.urllib.__main__ import main as client_main
from tasks_core import IncompleteImplementationError


def test_stdlib_launchers_parse_the_documented_commands() -> None:
    assert_server_parser(build_server_parser())
    assert_client_parser(build_client_parser())


def test_stdlib_launchers_smoke_to_intentional_incomplete_behavior() -> None:
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 3 standard-library server lifecycle.*intentionally incomplete",
    ):
        server_main(SERVER_ARGUMENTS)

    with pytest.raises(
        IncompleteImplementationError,
        match=r"client command execution.*intentionally incomplete",
    ):
        client_main(["list"])
