# 🐞 Chapter 13: Debugging and Command-Line Interfaces

**Semantic ID:** `module.debugging-and-cli` · **Prerequisites:**
`module.automated-testing`

## 📍 Where this fits

Chapter 12 gave you tests as a safety net. This chapter is the second of
the three tooling chapters: it teaches you to *diagnose* a failure once a
test (or a user) reports one, and to build the command-line boundary that
turns a script into a usable tool. Chapter 14 then takes the same programs
across process, environment, and packaging boundaries. Everything here uses
only language features you already have; the two new standard-library tools
are `pdb` for interactive inspection and `argparse` for parsing arguments,
plus `logging` for runtime diagnostics.

## 🎯 Learning objectives

After this chapter, you should be able to:

- read a traceback from the bottom up, recognize the most common exception
  types, and locate the first frame in your own code;
- pause a program and inspect its state with `pdb`, using the core commands
  (`break`, `continue`, `p`, `where`, `next`, `step`, `list`, `quit`) and
  `breakpoint()`;
- build a small `argparse` interface with a positional argument, an option
  that takes a value, and a boolean flag, while keeping core behavior in a
  function that knows nothing about argparse;
- reject invalid input at the boundary with a custom `type=` validator that
  raises `argparse.ArgumentTypeError`;
- build a multi-command interface with `add_subparsers`;
- emit runtime diagnostics with `logging` instead of scattered `print()`
  calls, understand severity levels and the library-versus-application
  split, and choose deliberately among `print()`, `pdb`, and `logging`.

## 🧠 Motivation and mental model

Debugging and CLIs are both about *boundaries*. When something fails, the
traceback is the boundary between "what Python was asked to do" and "what
went wrong"; you read it bottom-up because the last line names the actual
error and the frames above it are the call stack that led there. `pdb`
lets you stop at a boundary and ask the running program what it believes
to be true (`p some_value`) instead of guessing from the source.

A command-line interface is the boundary between the operating system and
your program. Good CLIs keep that boundary thin: `argparse` turns raw
`sys.argv` strings into a validated `Namespace`, and your real logic stays
in ordinary functions that take ordinary arguments and return values.
That separation is exactly what made the code in earlier chapters testable,
and it is why parsing lives in its own function you can call with an
explicit argument list from a test.

`logging` is the third boundary tool. A `print()` is a temporary peek; a
log record is a deliberate, filterable diagnostic with a severity level.
Libraries create a named logger and emit records; the *application* decides
once, at its boundary, what level to show and where records go.

## 1️⃣ Tracebacks and interactive debugging with pdb

The final traceback line is always `ExceptionType: message` -- read it
first. The frames above are the call stack, deepest last; find the first
one in *your* code and inspect the values there instead of guessing.
`ValueError`, `IndexError`, `KeyError`, and `AttributeError` cover most
everyday failures, and each message names exactly which assumption broke.
`pdb` lets you pause a running program and ask it what it actually
believes, rather than reasoning only from the source.

```python
def average(numbers: list[float]) -> float:
    """Deliberately buggy for numbers=[] to produce a traceback."""
    return sum(numbers) / len(numbers)


def demo_traceback() -> None:
    try:
        average([])
    except ZeroDivisionError:
        traceback.print_exc(file=sys.stdout)
```

```text
Traceback (most recent call last):
  File ".../01_tracebacks_and_pdb.py", line 32, in demo_traceback
    average([])
  File ".../01_tracebacks_and_pdb.py", line 24, in average
    return sum(numbers) / len(numbers)
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

This lesson **never launches the interactive debugger for you** -- it
only prints the exact `pdb` commands to try, so running it as a plain
script stays deterministic and non-blocking:

```bash
python lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
```

See [`01_tracebacks_and_pdb.py`](01_tracebacks_and_pdb.py) for the full
sequence, including `demo_common_errors`, which catches `ValueError`,
`IndexError`, `KeyError`, and `AttributeError` from four small, deliberate
mistakes and prints each real message.

> **Try one change (a separate, manual shell/tool session -- not
> something the lesson script runs for you):**
>
> ```bash
> python -m pdb lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
> ```
>
> At the `(Pdb)` prompt: `break average`, `continue`, `p numbers`,
> `p len(numbers)`, `where`, then `quit`. This confirms the buggy
> assumption (`numbers` is empty) interactively. Because you launch and
> quit this session yourself, it stays bounded; treat any `breakpoint()`
> the same way -- a manual, temporary aid you remove before committing,
> never something left in committed code.

## 2️⃣ Command-line argument parsing at the boundary

`argparse` turns raw `sys.argv` strings into a validated `Namespace` at
the program's boundary, while the real behavior stays in a plain function
that takes ordinary arguments and knows nothing about argv, printing, or
exit codes -- exactly the separation that keeps it directly testable.
Each `add_argument` call declares one input: a positional argument, an
option with a value (`type=`, `default=`), or a boolean flag
(`action="store_true"`).

```python
def build_greeting(name: str, *, shout: bool = False) -> str:
    message = f"Hello, {name}!"
    return message.upper() if shout else message


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for _ in range(args.count):
        print(build_greeting(args.name, shout=args.shout))
    return 0
```

```text
Fixed example (['Ada', '--count', '2', '--shout']):
HELLO, ADA!
HELLO, ADA!

`input()` reads one typed line; it is commented out so this
lesson runs non-interactively. Try it locally by uncommenting:

Now parsing the real command line (if you passed any):
Hello, World!
```

`parser.parse_args(argv)` returns the `Namespace`; passing `argv`
explicitly (as the fixed example does) keeps that call testable, while
`None` reads the real process command line (the second block above, run
with no arguments, so it falls back to the positional default
`"World"`).

Run the complete companion (a runnable script that also parses the real
command line after its fixed example):

```bash
python lessons/13_debugging_and_cli/02_argparse_basics.py
```

See [`02_argparse_basics.py`](02_argparse_basics.py) for the full
sequence, including `build_parser`, which wires the positional argument,
`--count`, and `--shout` together.

> **Try one change:** run the same script with your own arguments, e.g.
> `python lessons/13_debugging_and_cli/02_argparse_basics.py Grace
> --count 1`. Predict the result: only the second, real-argv section
> changes to `Hello, Grace!`; the fixed example's two `HELLO, ADA!` lines
> are unaffected, because they call `run([...])` with an explicit list,
> not the real command line.

## 3️⃣ Subcommands and custom validation

A `type=` callable converts and validates one string argument; raising
`argparse.ArgumentTypeError("must be positive")` gives argparse a precise
usage message. argparse also catches a plain `ValueError`/`TypeError` from
a validator, but downgrades it to a generic "invalid value" -- use
`ArgumentTypeError` when the message itself matters.
`parser.add_subparsers(dest="command", required=True)` creates a command
slot, and each `commands.add_parser("name")` defines that subcommand's own
arguments independently.

```python
def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


commands = parser.add_subparsers(dest="command", required=True)
add_parser = commands.add_parser("add", help="Add a note")
add_parser.add_argument("--priority", type=positive_int, default=1, ...)
```

```text
Example: add a note with a valid priority
add: text='Read argparse docs' priority=3

Example: list with a flag
list: pending_only=True

Example: an invalid priority is rejected at the boundary
argparse exited with status 2 (2 means usage error)
```

An invalid value at this boundary makes `parse_args` call `sys.exit(2)`
-- status 2 is argparse's usage-error convention. The companion's own
`try`/`except SystemExit` block around the last example is what lets the
lesson keep running afterward and print that final line.

Run the complete companion:

```bash
python lessons/13_debugging_and_cli/03_subcommands_and_custom_validation.py
```

See
[`03_subcommands_and_custom_validation.py`](03_subcommands_and_custom_validation.py)
for the full sequence, including the `list` subcommand's independent
`--pending-only` flag.

> **Try one change:** pass an invalid priority to the parser yourself,
> without the companion's `try`/`except` safety net, to see the raw usage
> error and process exit status directly:
>
> ```bash
> python -c "
> import sys; sys.path.insert(0, 'lessons/13_debugging_and_cli')
> mod = __import__('03_subcommands_and_custom_validation')
> mod.build_parser().parse_args(['add', 'x', '--priority', '0'])
> "; echo "exit status: $?"
> ```
>
> Predict the result: argparse prints its own usage text to stderr, and
> the exit status is `2` -- the exact code the companion's internal
> example already reports, now observed directly instead of caught.

## 4️⃣ Logging and diagnostics

A module creates its own logger with `logging.getLogger(__name__)` and
never configures handlers or the global level itself -- **the application
owns that configuration**, once, at its entry point. `logger.debug("...
%d ...", value)` uses lazy `%`-style formatting: the message is only
built if the level is enabled, so a disabled debug call costs almost
nothing. Log identifiers and context, never secret values.

```python
logger = logging.getLogger(__name__)


def calculate_total(prices: list[float]) -> float:
    logger.debug("calculating total for %d prices", len(prices))
    total = sum(prices)
    logger.info("calculated total %.2f", total)
    return total


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
```

```text
DEBUG __main__: calculating total for 3 prices
INFO __main__: calculated total 20.00
INFO __main__: authenticating user ada
INFO __main__: authenticating user grace
WARNING __main__: missing token for user grace
```

Because `main()` -- the application's boundary, not `calculate_total` or
`authenticate` -- calls `basicConfig(level=logging.DEBUG, ...)`, both
`DEBUG` and `INFO` records appear here; `authenticate` logs the username
but never the token value, even when it is missing.

Run the complete companion:

```bash
python lessons/13_debugging_and_cli/04_logging_and_diagnostics.py
```

See
[`04_logging_and_diagnostics.py`](04_logging_and_diagnostics.py) for the
full sequence, including the printed comparison of `print()`, `pdb`, and
`logging`.

> **Try one change:** predict which lines disappear if `main()`'s
> `basicConfig(level=logging.DEBUG, ...)` were changed to
> `level=logging.WARNING`. Both `logger.debug` and `logger.info` calls
> stop appearing (their level is below the new threshold), while
> `logger.warning("missing token for user %s", "grace")` still prints --
> only the application's configured level changed, not any call site.

## 🔁 Transition ahead

Chapter 14 takes these command-line programs across the remaining
boundaries: virtual environments and `pip`, standard streams and exit
status, owning a subprocess safely, the automated quality gates (Ruff,
mypy, pytest, coverage) and CI that check them, and packaging a distribution
with a documented public API.

## ⚠️ Common mistakes

- Reading a traceback top-down and fixing a frame in library code instead of
  the first frame in your own code.
- Leaving a `breakpoint()` or `import pdb; pdb.set_trace()` in committed code.
- Mixing parsing and logic: calling `print()` or `sys.exit()` from inside the
  function that should just compute and return a value.
- Raising `ValueError` from a `type=` validator when the CLI needs a precise
  explanation; argparse catches it, but replaces it with a generic
  "invalid value" message. Use `ArgumentTypeError` for the deliberate text.
- Forgetting `required=True` on `add_subparsers`, so running with no command
  produces a confusing `AttributeError` later.
- Building an f-string inside a `logger.debug(...)` call, defeating logging's
  lazy formatting; pass the arguments instead.
- Calling `logging.basicConfig()` from a library, or logging a password or
  token value.

## 🧾 Summary

- Read tracebacks bottom-up; the last line is the real error, the frames are
  the call stack.
- `pdb` pauses a program so you can inspect its actual state instead of
  guessing.
- `argparse` is a thin boundary that validates input; the real work stays in
  plain, testable functions.
- Custom `type=` validators raise `ArgumentTypeError`; `add_subparsers`
  builds multi-command tools.
- `logging` provides filterable, severity-tagged diagnostics; the library
  emits, the application configures, and secrets never appear in a record.

## ❓ Review questions (closed notes)

1. In what order do you read a traceback, and how do you find the frame that
   matters most?
2. Which `pdb` commands set a breakpoint, resume execution, print a value,
   and show the call stack?
3. Why should the core behavior of a CLI live in a function that never
   touches `argparse` or `sys.exit`?
4. What exception should a custom `type=` validator raise, and what does
   argparse do when it is raised?
5. What does `add_subparsers(dest=..., required=True)` provide, and why is
   `required=True` important?
6. Why do you pass arguments to `logger.info("...", value)` instead of
   building an f-string, and who is responsible for `basicConfig`?
7. When would you choose `print()`, `pdb`, or `logging`?

## 📚 Authoritative references

- [`pdb` — The Python Debugger](https://docs.python.org/3/library/pdb.html)
- [`traceback` — Print or retrieve a stack traceback](https://docs.python.org/3/library/traceback.html)
- [`argparse` — Parser for command-line options](https://docs.python.org/3/library/argparse.html)
- [`logging` — Logging facility for Python](https://docs.python.org/3/library/logging.html)
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)

Once you can answer the review questions and have run all four lesson files,
continue to
[`exercises/13_debugging_and_cli/`](../../exercises/13_debugging_and_cli/README.md).
