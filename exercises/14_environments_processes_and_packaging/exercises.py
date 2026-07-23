"""
Exercises: Chapter 14 - Environments, Processes, and Packaging

Two kinds of task:

1. Implement three functions that own configuration and a child process
   safely (`parse_process_timeout`, `build_child_command`,
   `run_child_process`).
2. Make one real packaging change: edit
   `starter_distribution/pyproject.toml` to declare a console entry point.

Run the evaluator from the repository root:

    python exercises/14_environments_processes_and_packaging/exercises.py

Each function starter raises NotImplementedError until you implement it, and
the packaging check fails until you add the `[project.scripts]` table. The
packaging check parses the TOML with `tomllib` and resolves the entry point
offline; nothing is installed and no network is used.
"""

import os
import subprocess
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
STARTER_DISTRIBUTION = HERE / "starter_distribution"


def parse_process_timeout(environment: Mapping[str, str]) -> int:
    """Return PROCESS_TIMEOUT as an integer from 1 through 30, default 5.

    Read only from the supplied mapping so callers can test configuration
    without changing the real process environment. Raise ValueError (never a
    bare crash) when the value is not an integer or is out of range.
    """
    # TODO: read environment.get("PROCESS_TIMEOUT", "5"), validate, return int
    raise NotImplementedError


def build_child_command(message: str) -> list[str]:
    """Return an argument-list command that prints message with this Python.

    Use sys.executable and pass message as ONE argument (not shell code), so
    spaces or shell metacharacters in message stay a single literal value.
    """
    # TODO: return [sys.executable, "-c", <code that prints sys.argv[1]>, message]
    raise NotImplementedError


def run_child_process(
    message: str, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    """Run build_child_command safely with a copied explicit environment.

    Use stdin=DEVNULL, check=True, captured text output, and a finite
    timeout, and pass a copy of the supplied environment (never shell=True).
    """
    # TODO: subprocess.run(..., stdin=subprocess.DEVNULL, check=True,
    # capture_output=True, text=True, timeout=<finite>, env=dict(environment))
    raise NotImplementedError


def verify_console_script(distribution: Path, command: str, target: str) -> None:
    """Parse pyproject.toml and confirm command maps to a real callable.

    Reads [project.scripts] with tomllib, requires that `command` maps to
    `target` in "module:attr" form, imports the module from the
    distribution's src/ directory, and confirms the attribute is callable.
    Raises AssertionError with a clear message on any failure.
    """
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
        import importlib

        module = importlib.import_module(module_name)
    finally:
        sys.path.remove(str(source_root))
    entry = getattr(module, attribute, None)
    assert callable(entry), f"{target} does not resolve to a callable"


def assert_subprocess_policy(message: str) -> None:
    """Check every subprocess ownership decision without starting a child."""
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
    assert command == build_child_command(message), "run the argument-list command"
    assert keywords.get("stdin") is subprocess.DEVNULL, "own stdin with DEVNULL"
    assert keywords.get("check") is True, "require a zero exit status"
    assert keywords.get("capture_output") is True, "capture stdout and stderr"
    assert keywords.get("text") is True, "decode captured output as text"
    timeout = keywords.get("timeout")
    assert type(timeout) in (int, float) and timeout > 0, "use a finite timeout"
    assert keywords.get("env") == environment, "pass the supplied environment"
    assert keywords["env"] is not environment, "copy the supplied environment"
    assert keywords.get("shell", False) is False, "never invoke a command shell"


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

verify_console_script(STARTER_DISTRIBUTION, "timekeeper", "timekeeper_cli:main")
print("console entry point: OK")

print("\nAll checks passed!")
