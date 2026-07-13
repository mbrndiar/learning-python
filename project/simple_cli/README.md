# Simple CLI Application

`text_stats.py` is a small command-line application that counts lines, words,
and characters. It demonstrates functions, `argparse`, file I/O, error
handling, exit codes, and unit testing.

## Run it

From this directory, pass text directly:

```bash
python text_stats.py --text "Hello from Python"
```

Or read a UTF-8 text file:

```bash
python text_stats.py --file README.md
```

Use the built-in help to discover all options:

```bash
python text_stats.py --help
```

## Run the tests

```bash
python test_text_stats.py
```
