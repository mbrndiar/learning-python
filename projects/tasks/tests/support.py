"""Deterministic paths and parser helpers for Task milestone tests."""

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

TEST_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_ROOT.parent
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
FIXTURES = TEST_ROOT / "fixtures"
FIXED_BASE_URL = "http://127.0.0.1:8765"

SERVER_ARGUMENTS = (
    "--host",
    "127.0.0.1",
    "--port",
    "8765",
    "--backend",
    "markdown",
    "--data",
    "tasks.md",
)

CLIENT_COMMANDS = (
    ("add", "Learn REST"),
    ("list", "--completed", "false"),
    ("show", "1"),
    ("update", "1", "--title", "Read the spec", "--completed", "true"),
    ("complete", "1"),
    ("remove", "1"),
)


@contextmanager
def temporary_project_directory() -> Iterator[Path]:
    """Create cleaned test storage below this project, never in system temp."""

    with TemporaryDirectory(prefix=".tasks-test-", dir=TEST_ROOT) as directory:
        yield Path(directory)


def load_json_fixture(*parts: str) -> object:
    """Load one deterministic UTF-8 JSON fixture."""

    return json.loads(FIXTURES.joinpath(*parts).read_text(encoding="utf-8"))


def assert_server_parser(parser: argparse.ArgumentParser) -> None:
    """Assert the common documented server options parse coherently."""

    arguments = parser.parse_args(SERVER_ARGUMENTS)
    assert cast(str, arguments.host) == "127.0.0.1"
    assert cast(int, arguments.port) == 8765
    assert cast(str, arguments.backend) == "markdown"
    assert cast(Path, arguments.data) == Path("tasks.md")


def assert_client_parser(parser: argparse.ArgumentParser) -> None:
    """Assert every documented client command parses without execution."""

    parsed_commands = [
        cast(str, parser.parse_args(command).command) for command in CLIENT_COMMANDS
    ]
    assert parsed_commands == [
        "add",
        "list",
        "show",
        "update",
        "complete",
        "remove",
    ]
