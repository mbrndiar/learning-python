"""
A small sibling module used by Lesson 3 to demonstrate import-time side
effects and a guarded entry point. Not a lesson file to run on its own,
though running it directly is exactly what Lesson 3 demonstrates.
"""

print("greeting_module: top-level code is executing (import-time side effect)")


def get_greeting(name: str) -> str:
    """Return a friendly greeting for *name*."""
    return f"Greetings, {name}!"


# This block only runs when Python set this module's __name__ to
# "__main__" -- that is, when this file is executed directly, not when it
# is imported. Guarding demo/CLI code like this lets a file serve both as
# an importable library and a runnable script.
if __name__ == "__main__":
    print("greeting_module: running as a script ->", get_greeting("Direct Run"))
