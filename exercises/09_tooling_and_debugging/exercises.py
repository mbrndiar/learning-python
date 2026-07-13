"""
Exercises: 09 Tooling and Debugging

Implement each function below, then run this file directly to check
your work.
"""

import argparse


def build_arg_parser():
    """Return an argparse.ArgumentParser with:
    - a required positional argument "path"
    - an optional "--verbose" flag (True/False, default False)
    """
    # TODO: implement this function
    raise NotImplementedError


def safe_call(func, *args, **kwargs):
    """Call func(*args, **kwargs). If it raises any Exception, return
    the string "Error: <message>" instead of letting it propagate."""
    # TODO: implement this function
    raise NotImplementedError


if __name__ == "__main__":
    parser = build_arg_parser()
    parsed = parser.parse_args(["myfile.txt", "--verbose"])
    assert parsed.path == "myfile.txt"
    assert parsed.verbose is True
    parsed_default = parser.parse_args(["myfile.txt"])
    assert parsed_default.verbose is False
    print("build_arg_parser: OK")

    assert safe_call(lambda: 1 / 0) == "Error: division by zero"
    assert safe_call(lambda a, b: a + b, 2, 3) == 5
    print("safe_call: OK")

    print("\nAll checks passed!")
