"""
Lesson 9.6: Environment, Processes, and Standard Streams

Environment variables are process configuration, not a safe place to display
secrets. A process reads bytes or text from stdin, writes normal results to
stdout, writes diagnostics to stderr, and reports success or failure with its
integer exit status.

When starting another process, pass an argument list. Do not interpolate user
input into a command string: a shell can interpret characters in that input as
new commands. `shell=True` is therefore not the default and is rarely needed.
"""

import os
import subprocess
import sys
from collections.abc import Mapping, Sequence

TOKEN_VARIABLE = "LEARNING_PYTHON_API_TOKEN"
CHILD_MESSAGE_VARIABLE = "LEARNING_PYTHON_CHILD_MESSAGE"


def token_is_configured(environment: Mapping[str, str]) -> bool:
    """Validate an optional token without returning or displaying its value."""
    token = environment.get(TOKEN_VARIABLE)
    if token is None:
        return False
    if token != token.strip() or len(token) < 8:
        raise ValueError(f"{TOKEN_VARIABLE} must contain at least 8 characters")
    return True


def run_child_process() -> subprocess.CompletedProcess[str]:
    """Run deterministic Python code with the current Python interpreter."""
    child_code = (
        "import os, sys; "
        f"print(os.environ[{CHILD_MESSAGE_VARIABLE!r}]); "
        "print('diagnostic from child', file=sys.stderr)"
    )
    command = [sys.executable, "-c", child_code]

    # Copy instead of mutating os.environ. Remove the example secret because
    # child processes should receive only configuration they actually need.
    child_environment = os.environ.copy()
    child_environment.pop(TOKEN_VARIABLE, None)
    child_environment[CHILD_MESSAGE_VARIABLE] = "result from child"

    return subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
        env=child_environment,
        stdin=subprocess.DEVNULL,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the lesson and return the process exit status."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments:
        print("usage: 06_os_processes_and_streams.py", file=sys.stderr)
        return 2

    try:
        configured = token_is_configured(os.environ)
    except ValueError as error:
        # The validation error names the variable and rule, never its value.
        print(f"configuration error: {error}", file=sys.stderr)
        return 2

    print(f"{TOKEN_VARIABLE} configured: {configured}")
    print("stdin supplies input; this noninteractive lesson does not read it.")
    print("stdout carries normal program results.")
    print("stderr carries diagnostics.", file=sys.stderr)

    try:
        child = run_child_process()
    except subprocess.TimeoutExpired:
        print("child process timed out", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"child process exited with status {error.returncode}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"could not start child process: {error}", file=sys.stderr)
        return 1

    print(f"child stdout: {child.stdout.strip()}")
    print(f"child stderr: {child.stderr.strip()}", file=sys.stderr)
    print(f"child exit status: {child.returncode} (zero means success)")
    print("Argument lists keep each value separate; no shell parses user input.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
