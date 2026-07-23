"""
Solutions: Chapter 14 - Environments, Processes, and Packaging
"""

import importlib
import os
import subprocess
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOLUTION_DISTRIBUTION = HERE / "solution_distribution"


def parse_process_timeout(environment: Mapping[str, str]) -> int:
    raw_timeout = environment.get("PROCESS_TIMEOUT", "5")
    try:
        timeout = int(raw_timeout)
    except ValueError as error:
        raise ValueError("PROCESS_TIMEOUT must be an integer") from error
    if not 1 <= timeout <= 30:
        raise ValueError("PROCESS_TIMEOUT must be between 1 and 30")
    return timeout


def build_child_command(message: str) -> list[str]:
    child_code = "import sys; print(sys.argv[1])"
    return [sys.executable, "-c", child_code, message]


def run_child_process(
    message: str, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        build_child_command(message),
        stdin=subprocess.DEVNULL,
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
        env=dict(environment),
    )


def verify_console_script(distribution: Path, command: str, target: str) -> None:
    pyproject = distribution / "pyproject.toml"
    with pyproject.open("rb") as stream:
        metadata = tomllib.load(stream)

    scripts = metadata.get("project", {}).get("scripts")
    assert isinstance(scripts, dict) and scripts, (
        f"add a non-empty [project.scripts] table to {pyproject}"
    )
    assert scripts.get(command) == target, (
        f'[project.scripts] must map "{command}" to "{target}" in {pyproject}'
    )

    module_name, _, attribute = target.partition(":")
    source_root = distribution / "src"
    sys.path.insert(0, str(source_root))
    try:
        module = importlib.import_module(module_name)
    finally:
        sys.path.remove(str(source_root))
    entry = getattr(module, attribute, None)
    assert callable(entry), f"{target} does not resolve to a callable"


def assert_subprocess_policy(message: str) -> None:
    environment = {"ONLY_FOR_TEST": "value"}
    expected = subprocess.CompletedProcess(
        build_child_command(message),
        returncode=0,
        stdout=message + "\n",
        stderr="",
    )
    with patch.object(subprocess, "run", return_value=expected) as run:
        assert run_child_process(message, environment) is expected

    positional, keywords = run.call_args
    command = positional[0] if positional else keywords.get("args")
    assert command == build_child_command(message)
    assert keywords.get("stdin") is subprocess.DEVNULL
    assert keywords.get("check") is True
    assert keywords.get("capture_output") is True
    assert keywords.get("text") is True
    timeout = keywords.get("timeout")
    assert type(timeout) in (int, float) and timeout > 0
    assert keywords.get("env") == environment
    assert keywords["env"] is not environment
    assert keywords.get("shell", False) is False


timeout_environment = {"PROCESS_TIMEOUT": "7"}
assert parse_process_timeout(timeout_environment) == 7
assert parse_process_timeout({}) == 5
assert timeout_environment == {"PROCESS_TIMEOUT": "7"}, "must not mutate the mapping"
for bad in ("0", "31", "not a number"):
    try:
        parse_process_timeout({"PROCESS_TIMEOUT": bad})
    except ValueError:
        pass
    else:
        raise AssertionError(f"PROCESS_TIMEOUT={bad!r} should raise ValueError")
print("parse_process_timeout: OK")

message = "hello; this is one argument"
command = build_child_command(message)
assert command[0] == sys.executable
assert command[-1] == message
print("build_child_command: OK")

assert_subprocess_policy(message)
child_environment = {
    name: os.environ[name]
    for name in ("SYSTEMROOT", "WINDIR", "PATH")
    if name in os.environ
}
child_environment["PROCESS_TIMEOUT"] = "5"
child = run_child_process(message, child_environment)
assert child.stdout == message + "\n"
assert child.stderr == ""
assert child.returncode == 0
print("run_child_process: OK")

verify_console_script(SOLUTION_DISTRIBUTION, "timekeeper", "timekeeper_cli:main")
print("console entry point: OK")

print("\nAll checks passed!")
