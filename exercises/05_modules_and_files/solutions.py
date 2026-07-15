"""
Solutions: 05 Modules and Files
"""

import json
import sys
from contextlib import contextmanager
from pathlib import Path

# Make example_package importable from this solution file.
sys.path.insert(0, str(Path(__file__).parents[2] / "lessons" / "05_modules_and_files"))


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")


def read_lines(path):
    with open(path, encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""


def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(
            f"Cannot withdraw {amount}, balance is only {balance}"
        )
    return balance - amount


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


@contextmanager
def temporary_value(mapping, key, value):
    missing = object()
    previous = mapping.get(key, missing)
    mapping[key] = value
    try:
        yield
    finally:
        if previous is missing:
            del mapping[key]
        else:
            mapping[key] = previous


def describe_greeting(name: str) -> str:
    from example_package.greetings import hello

    return hello(name)


if __name__ == "__main__":
    sample_path = Path(__file__).with_name("sample_exercise.txt")

    write_lines(sample_path, ["alpha", "beta", "gamma"])
    assert read_lines(sample_path) == ["alpha", "beta", "gamma"]
    sample_path.unlink()
    print("write_lines/read_lines: OK")

    assert safe_divide(10, 2) == 5
    assert safe_divide(10, 0) is None
    print("safe_divide: OK")

    assert withdraw(100, 40) == 60
    try:
        withdraw(100, 150)
        raise AssertionError("expected InsufficientFundsError")
    except InsufficientFundsError:
        pass
    print("withdraw: OK")

    json_path = Path(__file__).with_name("sample_exercise.json")
    save_json(json_path, {"name": "Ada", "active": True})
    assert load_json(json_path) == {"name": "Ada", "active": True}
    assert json_path.read_text(encoding="utf-8").endswith("\n")
    json_path.unlink()
    print("save_json/load_json: OK")

    settings = {"mode": "normal"}
    with temporary_value(settings, "mode", "debug"):
        assert settings["mode"] == "debug"
    assert settings == {"mode": "normal"}
    with temporary_value(settings, "new", 1):
        assert settings["new"] == 1
    assert "new" not in settings
    print("temporary_value: OK")

    assert describe_greeting("Ada") == "Hello, Ada!"
    assert describe_greeting("grace hopper") == "Hello, Grace Hopper!"
    print("describe_greeting: OK")

    print("\nAll checks passed!")
