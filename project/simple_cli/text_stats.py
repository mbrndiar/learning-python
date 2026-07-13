"""Count lines, words, and characters in text from the terminal or a file."""

import argparse
from pathlib import Path


def count_text(text):
    return {
        "lines": len(text.splitlines()),
        "words": len(text.split()),
        "characters": len(text),
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Count lines, words, and characters in text"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Text to count")
    source.add_argument("--file", type=Path, help="UTF-8 text file to count")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        text = args.text if args.text is not None else args.file.read_text("utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Error: {error}")
        return 1

    counts = count_text(text)
    print(f"Lines: {counts['lines']}")
    print(f"Words: {counts['words']}")
    print(f"Characters: {counts['characters']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
