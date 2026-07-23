# 🐞 Exercises: Chapter 13 - Debugging and Command-Line Interfaces

Practice problems for
[`lessons/13_debugging_and_cli/`](../../lessons/13_debugging_and_cli/README.md):
reading tracebacks, interactive debugging, `argparse` boundaries, custom
validators, subcommands, and `logging`.

## 🧩 Tasks in `exercises.py`

Two of these build a **simple parser and its helpers**, and two build the
**custom-validation / subcommand** boundary. Keep them separate as you work.

- `build_arg_parser()` - a simple parser with a required positional `path`
  and an optional `--verbose` flag.
- `positive_int(text)` - a reusable argparse `type=` validator that raises
  `argparse.ArgumentTypeError`.
- `safe_int(text)` - catch only the conversion error you can handle.
- `build_command_parser()` - `add TITLE --priority N` and
  `list --pending-only` subcommands, reusing `positive_int`.
- `configure_logger(verbose)` - select an appropriate logging level.

## ▶️ How to work through it

1. Read [`lessons/13_debugging_and_cli/`](../../lessons/13_debugging_and_cli/README.md)
   first.
2. Open `exercises.py` and implement each function marked `# TODO`. The
   checks run top to bottom and stop at the first failure, so implement the
   functions in order.
3. Run it from the repository root:

   ```bash
   python exercises/13_debugging_and_cli/exercises.py
   ```

   It prints `All checks passed!` once every function is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.

## 🔧 Guided pdb lab

The functions above practice program design. This lab practices interactive
debugging without leaving deliberately broken files in the repository.

Lesson 1 intentionally calls `average([])` and catches the resulting
exception. Reproduce and inspect the failure under the debugger:

```bash
python lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
python -m pdb lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
```

At the `(Pdb)` prompt, run:

```text
break average
continue
p numbers
p len(numbers)
where
quit
```

State the failed assumption in words (an empty sequence has no mean, so the
division by `len(numbers)` is zero) *before* imagining a fix. Then decide
where the guard belongs: at the boundary that builds the input, or inside
`average` itself. This is the same diagnose-then-decide loop you will use on
every real bug for the rest of the course.
