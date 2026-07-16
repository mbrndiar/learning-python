"""Shared invocation helpers for every Task client transport."""

from collections.abc import Sequence
from io import StringIO

from tasks_cli.application import run
from tasks_cli.transport import TransportFactory


def invoke_client(
    transport_factory: TransportFactory,
    base_url: str,
    argv: Sequence[str],
) -> tuple[int, str, str]:
    """Run one real client invocation with captured process streams."""

    stdout = StringIO()
    stderr = StringIO()
    exit_code = run(
        ["--base-url", base_url, "--timeout", "2", *argv],
        transport_factory,
        stdout,
        stderr,
        prog="test-tasks-client",
    )
    return exit_code, stdout.getvalue(), stderr.getvalue()


__all__ = ["invoke_client"]
