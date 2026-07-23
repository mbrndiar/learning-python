"""
Chapter 14, Lesson 3: Owning a Subprocess Safely

Purpose: start another program correctly. Use the current interpreter
(`sys.executable`), pass an argument list (never a shell string), give the
child an explicit allowlisted environment, own its stdin, capture its text
output, set a finite timeout, require success with `check=True`, and map the
distinct failure modes to a clear error taxonomy.

Prerequisites: Chapter 7 (exceptions) and Lesson 2 (streams and exit
status). This lesson runs one short, deterministic child that only echoes a
message; it performs no installs and no network access.

Run it from the repository root:

    python lessons/14_environments_processes_and_packaging/03_subprocess_ownership.py
"""

import os
import subprocess
import sys


# Step 1: build the command as an ARGUMENT LIST. Each element is one
# argument, so the message stays a single value even if it contains spaces
# or shell metacharacters. There is no shell to reinterpret it. Using
# sys.executable runs the same Python that started this process.
def build_child_command(message: str) -> list[str]:
    """Return an argument-list command that prints one literal argument."""
    child_code = "import sys; print(sys.argv[1])"
    return [sys.executable, "-c", child_code, message]


# Step 2: build an explicit environment for the child by copying only what
# it needs, instead of forwarding every parent variable. Windows system
# roots are preserved when present; the lesson-owned message is the only
# application configuration passed in.
def build_child_environment() -> dict[str, str]:
    """Return a minimal allowlisted environment for the child process."""
    return {
        name: os.environ[name]
        for name in ("SYSTEMROOT", "WINDIR", "PATH")
        if name in os.environ
    }


# Step 3: run the child with every ownership decision made explicitly.
def run_child(message: str) -> subprocess.CompletedProcess[str]:
    """Run one child process with explicit ownership of every boundary."""
    return subprocess.run(
        build_child_command(message),
        env=build_child_environment(),
        # We own stdin: DEVNULL guarantees the child cannot block waiting for
        # input that will never arrive.
        stdin=subprocess.DEVNULL,
        # Capture both streams as decoded text instead of raw bytes.
        capture_output=True,
        text=True,
        # A finite timeout prevents a hung child from hanging this process.
        timeout=5,
        # check=True turns a nonzero exit into CalledProcessError instead of
        # silently continuing with a failed result.
        check=True,
    )


# Step 4: the error taxonomy. Each subprocess failure mode is a distinct
# exception; handle each specifically and return a matching exit status
# rather than catching everything the same way.
def main() -> int:
    """Demonstrate the subprocess and report a status for each outcome."""
    try:
        completed = run_child("result from child")
    except subprocess.TimeoutExpired:
        print("child process timed out", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        # The child ran but exited nonzero.
        print(f"child exited with status {error.returncode}", file=sys.stderr)
        return 1
    except OSError as error:
        # The child could not even be started (e.g. executable not found).
        print(f"could not start child process: {error}", file=sys.stderr)
        return 1

    print(f"child stdout: {completed.stdout.strip()}")
    print(f"child exit status: {completed.returncode} (zero means success)")
    print(
        "\nKey ownership decisions:\n"
        "  - sys.executable + argument list, never a shell string;\n"
        "  - explicit allowlisted env instead of the full parent environment;\n"
        "  - stdin=DEVNULL so the child cannot block on input;\n"
        "  - capture_output + text to read decoded stdout/stderr;\n"
        "  - a finite timeout and check=True to fail loudly, not silently."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
