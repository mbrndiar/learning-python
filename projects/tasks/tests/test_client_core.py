"""Contract for the CLI application above urllib, Requests, and HTTPX.

The fake transport isolates command parsing, typed requests, strict response
decoding, stable exit categories, and ownership/cleanup from any HTTP library.
Starter-only checks retain a compileable guided TODO; solution-only checks
define the behavior every concrete transport must expose to the application.
"""

import ast
import json
from collections.abc import Sequence
from io import StringIO
from pathlib import Path
from typing import TextIO, cast

import pytest
from implementation import IMPLEMENTATION
from tasks_cli import (
    TaskTransport,
    TransportConnectionError,
    TransportError,
    TransportFactory,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
    build_url,
    normalize_base_url,
)
from tasks_cli.application import parse_request, run
from tasks_core import IncompleteImplementationError

STARTER = IMPLEMENTATION == "starter"
# The shared parser and type scaffolding remain testable in both trees, while
# command execution is deliberately incomplete until the learner solves it.
solution_only = pytest.mark.skipif(STARTER, reason="solution client-core behavior")
starter_only = pytest.mark.skipif(not STARTER, reason="starter guidance behavior")

TASK = {"id": 7, "title": "Learn REST", "completed": False}
JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}


class _FakeTransport:
    """Record typed requests and inject send or cleanup failures deterministically."""

    def __init__(
        self,
        response: TransportResponse | None = None,
        *,
        failure: Exception | None = None,
        close_failure: Exception | None = None,
    ) -> None:
        self.response = response
        self.failure = failure
        self.close_failure = close_failure
        self.requests: list[TransportRequest] = []
        self.closed = False

    def send(self, request: TransportRequest) -> TransportResponse:
        self.requests.append(request)
        if self.failure is not None:
            raise self.failure
        if self.response is None:
            raise AssertionError("fake response was not configured")
        return self.response

    def close(self) -> None:
        self.closed = True
        if self.close_failure is not None:
            raise self.close_failure


class _FakeFactory:
    def __init__(
        self,
        transport: _FakeTransport,
        *,
        failure: Exception | None = None,
    ) -> None:
        self.transport = transport
        self.failure = failure
        self.calls: list[tuple[str, float]] = []

    def __call__(self, base_url: str, timeout: float) -> TaskTransport:
        self.calls.append((base_url, timeout))
        if self.failure is not None:
            raise self.failure
        return self.transport


def _json_response(status: int, value: object) -> TransportResponse:
    return TransportResponse(
        status,
        JSON_HEADERS,
        json.dumps(value, ensure_ascii=False).encode(),
    )


def _invoke(
    argv: Sequence[str],
    response: TransportResponse | None = None,
    *,
    transport: _FakeTransport | None = None,
    factory: _FakeFactory | None = None,
) -> tuple[int, str, str, _FakeTransport, _FakeFactory]:
    selected_transport = transport or _FakeTransport(response)
    selected_factory = factory or _FakeFactory(selected_transport)
    stdout = StringIO()
    stderr = StringIO()
    exit_code = run(
        argv,
        selected_factory,
        stdout,
        stderr,
        prog="test-tasks-cli",
    )
    return (
        exit_code,
        stdout.getvalue(),
        stderr.getvalue(),
        selected_transport,
        selected_factory,
    )


def _public_surface(path: Path) -> dict[str, str]:
    # AST comparison inspects source without importing the non-selected tree,
    # preserving the harness guarantee that only one implementation is loaded.
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = {
        "AddCommand",
        "ClientRequest",
        "ClientResult",
        "ClientSettings",
        "CompleteCommand",
        "ListCommand",
        "RemoveCommand",
        "ShowCommand",
        "UpdateCommand",
        "build_parser",
        "main",
        "parse_request",
        "run",
    }
    surface: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            if isinstance(node, ast.FunctionDef):
                signature: ast.AST = node.args
            else:
                fields: list[ast.stmt] = [
                    item
                    for item in node.body
                    if isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                ]
                signature = ast.Module(body=fields, type_ignores=[])
            surface[node.name] = ast.dump(signature, include_attributes=False)
    return surface


def test_starter_and_solution_public_client_signatures_match() -> None:
    project_root = Path(__file__).resolve().parents[1]
    starter = _public_surface(project_root / "starter/tasks_cli/application.py")
    solution = _public_surface(project_root / "solution/tasks_cli/application.py")
    assert starter == solution


def test_base_url_and_explicit_request_url_encoding() -> None:
    request = TransportRequest(
        "GET",
        "/tasks/a b/雪",
        query={"state": "not true", "tag": "a/b&c"},
    )

    assert normalize_base_url("HTTPS://EXAMPLE.COM/api///") == (
        "https://example.com/api"
    )
    assert build_url("HTTPS://EXAMPLE.COM/api///", request) == (
        "https://example.com/api/tasks/a%20b/%E9%9B%AA?state=not%20true&tag=a%2Fb%26c"
    )


@pytest.mark.parametrize(
    ("argv", "expected_request", "response", "expected_stdout"),
    [
        (
            ["add", "Learn REST"],
            TransportRequest("POST", "/tasks", json_body={"title": "Learn REST"}),
            _json_response(201, TASK),
            '{"id": 7, "title": "Learn REST", "completed": false}\n',
        ),
        (
            ["list"],
            TransportRequest("GET", "/tasks"),
            _json_response(200, [TASK]),
            '[{"id": 7, "title": "Learn REST", "completed": false}]\n',
        ),
        (
            ["list", "--completed", "false"],
            TransportRequest("GET", "/tasks", query={"completed": "false"}),
            _json_response(200, [TASK]),
            '[{"id": 7, "title": "Learn REST", "completed": false}]\n',
        ),
        (
            ["show", "7"],
            TransportRequest("GET", "/tasks/7"),
            _json_response(200, TASK),
            '{"id": 7, "title": "Learn REST", "completed": false}\n',
        ),
        (
            ["update", "7", "--title", "Read spec"],
            TransportRequest(
                "PATCH",
                "/tasks/7",
                json_body={"title": "Read spec"},
            ),
            _json_response(200, {**TASK, "title": "Read spec"}),
            '{"id": 7, "title": "Read spec", "completed": false}\n',
        ),
        (
            ["update", "7", "--completed", "false"],
            TransportRequest(
                "PATCH",
                "/tasks/7",
                json_body={"completed": False},
            ),
            _json_response(200, TASK),
            '{"id": 7, "title": "Learn REST", "completed": false}\n',
        ),
        (
            ["complete", "7"],
            TransportRequest(
                "PATCH",
                "/tasks/7",
                json_body={"completed": True},
            ),
            _json_response(200, {**TASK, "completed": True}),
            '{"id": 7, "title": "Learn REST", "completed": true}\n',
        ),
        (
            ["remove", "7"],
            TransportRequest("DELETE", "/tasks/7"),
            TransportResponse(204, {}, b""),
            '{"deleted": 7}\n',
        ),
    ],
)
@solution_only
def test_commands_build_typed_requests_and_render_stable_stdout(
    argv: list[str],
    expected_request: TransportRequest,
    response: TransportResponse,
    expected_stdout: str,
) -> None:
    exit_code, stdout, stderr, transport, factory = _invoke(argv, response)

    assert exit_code == 0
    assert stdout == expected_stdout
    assert stderr == ""
    assert transport.requests == [expected_request]
    assert transport.closed
    assert factory.calls == [("http://127.0.0.1:8000", 5.0)]


@solution_only
def test_normalized_base_url_and_finite_timeout_reach_factory() -> None:
    result = _invoke(
        [
            "--base-url",
            "HTTPS://EXAMPLE.COM/api///",
            "--timeout",
            "0.25",
            "list",
        ],
        _json_response(200, []),
    )

    assert result[0:3] == (0, "[]\n", "")
    assert result[4].calls == [("https://example.com/api", 0.25)]


@pytest.mark.parametrize(
    "argv",
    [
        ["show", "0"],
        ["update", "1"],
        ["--timeout", "0", "list"],
        ["--timeout", "-1", "list"],
        ["--timeout", "nan", "list"],
        ["--timeout", "inf", "list"],
        ["--base-url", "ftp://example.com", "list"],
        ["--base-url", "http://", "list"],
        ["--base-url", "http://user@example.com", "list"],
        ["--base-url", "http://example.com?debug=true", "list"],
        ["--base-url", "http://example.com/#fragment", "list"],
    ],
)
@solution_only
def test_usage_failures_are_concise_and_do_not_create_transport(
    argv: list[str],
) -> None:
    transport = _FakeTransport()
    factory = _FakeFactory(transport)

    exit_code, stdout, stderr, _, _ = _invoke(
        argv,
        transport=transport,
        factory=factory,
    )

    assert exit_code == 2
    assert stdout == ""
    assert stderr.startswith("usage: ")
    assert stderr.count("\n") == 1
    assert factory.calls == []
    assert not transport.closed


@solution_only
def test_help_uses_injected_stdout_without_creating_transport() -> None:
    transport = _FakeTransport()
    factory = _FakeFactory(transport)

    exit_code, stdout, stderr, _, _ = _invoke(
        ["--help"],
        transport=transport,
        factory=factory,
    )

    assert exit_code == 0
    assert stdout.startswith("usage: test-tasks-cli")
    assert stderr == ""
    assert factory.calls == []


@pytest.mark.parametrize(
    ("failure", "expected_stderr"),
    [
        (
            TransportTimeoutError("deadline exceeded"),
            "connection: timeout: deadline exceeded\n",
        ),
        (
            TransportConnectionError("connection refused"),
            "connection: connection refused\n",
        ),
        (TransportError("exchange failed"), "transport: exchange failed\n"),
        (RuntimeError("library detail"), "transport: request failed\n"),
    ],
)
@solution_only
def test_transport_failures_are_stable_and_never_escape(
    failure: Exception,
    expected_stderr: str,
) -> None:
    # Library-neutral errors retain their category; unexpected implementation
    # details are deliberately collapsed before reaching process stderr.
    transport = _FakeTransport(failure=failure)

    exit_code, stdout, stderr, selected, _ = _invoke(
        ["list"],
        transport=transport,
    )

    assert (exit_code, stdout, stderr) == (5, "", expected_stderr)
    assert selected.closed
    assert len(selected.requests) == 1


@solution_only
def test_factory_and_cleanup_failures_are_transport_failures() -> None:
    # Construction and close are part of transport ownership just as much as
    # send(), so neither lifecycle edge may escape the CLI boundary.
    transport = _FakeTransport(
        _json_response(200, []),
        close_failure=RuntimeError("library close detail"),
    )
    failed_factory = _FakeFactory(
        transport,
        failure=RuntimeError("library constructor detail"),
    )

    factory_result = _invoke(
        ["list"],
        transport=transport,
        factory=failed_factory,
    )

    assert factory_result[0:3] == (5, "", "transport: request failed\n")
    assert not transport.closed

    cleanup_result = _invoke(["list"], transport=transport)

    assert cleanup_result[0:3] == (5, "", "transport: request failed\n")
    assert cleanup_result[3].closed


@pytest.mark.parametrize(
    ("argv", "status", "code"),
    [
        (["update", "7", "--completed", "true"], 400, "invalid_json"),
        (["show", "7"], 404, "not_found"),
        (["show", "7"], 405, "method_not_allowed"),
        (["show", "7"], 422, "validation_error"),
        (["show", "7"], 500, "internal_error"),
    ],
)
@solution_only
def test_documented_api_errors_use_api_exit_category(
    argv: list[str],
    status: int,
    code: str,
) -> None:
    response = _json_response(
        status,
        {"error": {"code": code, "message": "documented failure"}},
    )

    exit_code, stdout, stderr, transport, _ = _invoke(argv, response)

    assert exit_code == 3
    assert stdout == ""
    assert stderr == f"api: {status} {code}: documented failure\n"
    assert transport.closed


@pytest.mark.parametrize(
    "value",
    [
        {"id": 7, "title": "Learn REST", "completed": False, "extra": 1},
        {"id": 7, "title": "Learn REST"},
        {"id": True, "title": "Learn REST", "completed": False},
        {"id": 0, "title": "Learn REST", "completed": False},
        {"id": "7", "title": "Learn REST", "completed": False},
        {"id": 7, "title": "", "completed": False},
        {"id": 7, "title": " padded ", "completed": False},
        {"id": 7, "title": "two\nlines", "completed": False},
        {"id": 7, "title": "control\u0000", "completed": False},
        {"id": 7, "title": "x" * 121, "completed": False},
        {"id": 7, "title": "Learn REST", "completed": 0},
    ],
)
@solution_only
def test_task_response_rejects_unknown_missing_and_wrong_fields(
    value: object,
) -> None:
    result = _invoke(["show", "7"], _json_response(200, value))

    assert result[0] == 4
    assert result[1] == ""
    assert result[2].startswith("malformed-response: ")


@pytest.mark.parametrize(
    "value",
    [
        TASK,
        [{**TASK, "extra": True}],
        [
            {"id": 2, "title": "Second", "completed": False},
            {"id": 1, "title": "First", "completed": False},
        ],
        [TASK, TASK],
    ],
)
@solution_only
def test_list_response_rejects_wrong_shape_or_order(value: object) -> None:
    result = _invoke(["list"], _json_response(200, value))

    assert result[0] == 4
    assert result[1] == ""
    assert result[2].startswith("malformed-response: ")


@pytest.mark.parametrize(
    "response",
    [
        TransportResponse(200, {"Content-Type": "text/plain"}, b"{}"),
        TransportResponse(200, {}, b"{}"),
        TransportResponse(
            200,
            {"Content-Type": "application/json; charset=iso-8859-1"},
            json.dumps(TASK).encode(),
        ),
        TransportResponse(200, JSON_HEADERS, b"\xff"),
        TransportResponse(200, JSON_HEADERS, b"{"),
        TransportResponse(
            200,
            JSON_HEADERS,
            b'{"id":7,"id":8,"title":"x","completed":false}',
        ),
        TransportResponse(
            200,
            JSON_HEADERS,
            b'{"id":7,"title":"x","completed":NaN}',
        ),
        _json_response(201, TASK),
    ],
)
@solution_only
def test_success_response_rejects_content_json_and_status_failures(
    response: TransportResponse,
) -> None:
    # Each case is superficially successful HTTP but violates the common wire
    # contract; accepting library-specific permissiveness would break parity.
    result = _invoke(["show", "7"], response)

    assert result[0] == 4
    assert result[1] == ""
    assert result[2].startswith("malformed-response: ")


@pytest.mark.parametrize(
    "value",
    [
        {"unexpected": {}},
        {"error": "not an object"},
        {"error": {"message": "missing code"}},
        {"error": {"code": "not_found", "message": "x", "extra": True}},
        {"error": {"code": "not_found", "message": "x", "details": []}},
        {"error": {"code": "not_found", "message": "x", "details": None}},
        {"error": {"code": "validation_error", "message": "wrong code"}},
        {"error": {"code": "not_found", "message": ""}},
        {"error": {"code": "not_found", "message": 7}},
    ],
)
@solution_only
def test_api_error_response_rejects_unknown_missing_and_wrong_fields(
    value: object,
) -> None:
    result = _invoke(["show", "7"], _json_response(404, value))

    assert result[0] == 4
    assert result[1] == ""
    assert result[2].startswith("malformed-response: ")


@solution_only
def test_error_status_not_documented_for_operation_is_malformed() -> None:
    result = _invoke(
        ["show", "7"],
        _json_response(
            400,
            {"error": {"code": "invalid_json", "message": "not valid here"}},
        ),
    )

    assert result[0] == 4
    assert result[1] == ""
    assert result[2] == "malformed-response: unexpected HTTP status: 400\n"


@solution_only
def test_delete_requires_exact_empty_204_response() -> None:
    nonempty = _invoke(
        ["remove", "7"],
        TransportResponse(204, {}, b" "),
    )
    api_error = _invoke(
        ["remove", "7"],
        _json_response(
            404,
            {"error": {"code": "not_found", "message": "task 7 was not found"}},
        ),
    )

    assert nonempty[0:2] == (4, "")
    assert nonempty[2].startswith("malformed-response: ")
    assert api_error[0:3] == (
        3,
        "",
        "api: 404 not_found: task 7 was not found\n",
    )


@starter_only
def test_starter_run_reaches_a_compileable_guided_todo() -> None:
    factory = cast(TransportFactory, _FakeFactory(_FakeTransport()))

    with pytest.raises(
        IncompleteImplementationError,
        match=r"client command execution.*intentionally incomplete",
    ):
        run(["list"], factory, StringIO(), StringIO(), prog="test-tasks-cli")


def test_parse_request_preserves_false_instead_of_treating_it_as_omitted() -> None:
    request = parse_request(["update", "7", "--completed", "false"])
    command = cast(object, request.command)

    assert getattr(command, "completed") is False
    assert getattr(command, "title") is None


def test_transport_request_rejects_unsafe_typed_values() -> None:
    with pytest.raises(ValueError, match="path"):
        TransportRequest("GET", "tasks")
    with pytest.raises(ValueError, match="JSON-compatible"):
        TransportRequest("POST", "/tasks", json_body={"value": float("nan")})


def test_run_signature_accepts_injected_output_streams() -> None:
    stdout: TextIO = StringIO()
    stderr: TextIO = StringIO()
    factory = cast(TransportFactory, _FakeFactory(_FakeTransport()))

    if STARTER:
        with pytest.raises(IncompleteImplementationError):
            run(["list"], factory, stdout, stderr)
    else:
        transport = _FakeTransport(_json_response(200, []))
        assert run(["list"], _FakeFactory(transport), stdout, stderr) == 0
        assert cast(StringIO, stdout).getvalue() == "[]\n"
        assert cast(StringIO, stderr).getvalue() == ""
