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

## 🧩 Progressive syntax and mechanism

1. **Reading a traceback.** The final line is `ExceptionType: message`.
   The frames above are the call stack, deepest last. Find the first frame
   in *your* code and inspect the values there.
2. **Common exceptions.** `ValueError`, `IndexError`, `KeyError`, and
   `AttributeError` cover most everyday failures; the message tells you
   which assumption broke.
3. **`pdb`.** Run `python -m pdb script.py`, then at the `(Pdb)` prompt use
   `break func`, `continue`, `p expr`, `where`, `next`, `step`, `list`, and
   `quit`. `breakpoint()` pauses from inside code; never leave it committed.
4. **Core-behavior function.** Keep the real logic in a plain function that
   does not print, read `argv`, or exit.
5. **`argparse.ArgumentParser`.** Each `add_argument` declares one input: a
   positional argument, an option (`--count`) with `type=`/`default=`, or a
   boolean flag with `action="store_true"`. `--help` and usage text are
   generated for you.
6. **Parsing at the boundary.** `parser.parse_args(argv)` returns a
   `Namespace`. Passing `argv` explicitly keeps the boundary testable;
   `None` reads the real process command line.
7. **Custom validators.** A `type=` callable converts one string and raises
   `argparse.ArgumentTypeError` on bad input, so argparse prints your
   precise validation message and exits with status 2. It also catches
   `ValueError`/`TypeError`, but reports only a generic "invalid value".
8. **Subcommands.** `parser.add_subparsers(dest="command", required=True)`
   creates a command slot; each `add_parser("name")` defines that command's
   own arguments.
9. **`logging`.** A library module calls `logging.getLogger(__name__)` and
   emits records with lazy `%`-style formatting (`logger.info("total %d",
   n)`). The application calls `logging.basicConfig(...)` once to choose the
   level, format, and destination. Log identifiers and context, never
   secrets.

## 📖 Read-predict-run-modify workflow

Read each file top to bottom, predict its output, then run it:

```bash
python lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
python lessons/13_debugging_and_cli/02_argparse_basics.py
python lessons/13_debugging_and_cli/03_subcommands_and_custom_validation.py
python lessons/13_debugging_and_cli/04_logging_and_diagnostics.py
```

### Expected output highlights

- `01_tracebacks_and_pdb.py`: prints one caught example traceback, a table
  of common exceptions and their messages, and the exact `pdb` commands to
  try. It never launches the interactive debugger for you, so it stays
  deterministic; the debugger session is a hands-on lab you run yourself.
- `02_argparse_basics.py`: runs a fixed example
  (`['Ada', '--count', '2', '--shout']`) that prints `HELLO, ADA!` twice,
  then parses any real arguments you pass.
- `03_subcommands_and_custom_validation.py`: shows the `add` and `list`
  subcommands and demonstrates that `--priority 0` is rejected at the
  boundary with exit status 2.
- `04_logging_and_diagnostics.py`: configures logging once, prints DEBUG and
  INFO records for a total calculation, a WARNING when a token is missing,
  and a summary of when to use `print()`, `pdb`, or `logging`.

### Try the pdb lab yourself

Lesson 1 is deterministic on purpose, but debugging is a skill you learn by
doing. Run the guided session and confirm the buggy assumption:

```bash
python -m pdb lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
```

At the `(Pdb)` prompt: `break average`, `continue`, `p numbers`,
`p len(numbers)`, `where`, then `quit`.

Then modify something and predict the new result: change a `parametrize`-style
example in the argparse lesson, or add a `logger.debug(...)` call and confirm
it only appears because the application set `level=logging.DEBUG`.

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
