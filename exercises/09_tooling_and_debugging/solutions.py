"""
Solutions: 09 Tooling and Debugging
"""

import argparse


def build_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--verbose", action="store_true")
    return parser


def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as error:
        return f"Error: {error}"


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
