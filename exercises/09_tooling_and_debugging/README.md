# Exercises: Module 9 - Tooling and Debugging

Practice problems for [`lessons/09_tooling_and_debugging/`](../../lessons/09_tooling_and_debugging/README.md):
virtual environments, debugging, CLI arguments and `pytest`.

## Tasks in `exercises.py`

- `build_arg_parser()` - build an `argparse.ArgumentParser` with a
  required positional argument and an optional flag.
- `build_command_parser()` - add `add` and `list` subcommands.
- `positive_int(text)` - implement a reusable argparse validator.
- `safe_int(text)` - catch only the conversion error you can handle.
- `configure_logger(verbose)` - select an appropriate logging level.

## How to work through it

1. Read [`lessons/09_tooling_and_debugging/`](../../lessons/09_tooling_and_debugging/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/09_tooling_and_debugging/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
