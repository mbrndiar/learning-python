"""
Lesson 3.1: Functions

Functions package reusable logic behind a name and a contract. Parameters are
local names bound to arguments supplied by the caller; return passes a result
back and immediately ends the call. A function with no return statement
implicitly returns None.
"""


def greet(name):
    """Return a greeting so the caller decides whether and where to print it."""
    return f"Hello, {name}!"


def add(a, b=0):
    """Add two numbers together.

    Defaults are evaluated once when `def` runs. The immutable integer used
    here is safe; a mutable list or dictionary could retain changes across
    calls, which is why those defaults are normally represented by None.
    """
    return a + b


def describe_person(name, age, city="Unknown"):
    """Demonstrate positional, default and keyword arguments."""
    return f"{name} is {age} years old and lives in {city}."


def divide(numerator, denominator, /):
    """Divide two positional-only arguments.

    The slash marks every parameter before it as positional-only, so calls such
    as divide(numerator=10, denominator=2) are not allowed.
    """
    return numerator / denominator


def make_label(text, *, prefix="Note"):
    """Return a label with a keyword-only prefix.

    The bare star marks every parameter after it as keyword-only.
    """
    return f"{prefix}: {text}"


def format_measurement(value, /, unit="units", *, precision=1):
    """Combine positional-only, positional-or-keyword and keyword-only inputs."""
    return f"{value:.{precision}f} {unit}"


def sum_all(*numbers):
    """Accept positional arguments collected into the tuple `numbers`.

    The tuple exists even when the caller supplies no extra arguments, so the
    function can process all calls through one code path.
    """
    return sum(numbers)


def print_info(**details):
    """Accept keyword arguments collected into the dictionary `details`."""
    for key, value in details.items():
        print(f"  {key}: {value}")


def show_message(message):
    """Print a message and implicitly return None."""
    print(message)


def append_item(items, item):
    """Mutate the list object shared with the caller."""
    items.append(item)


def replace_items(items):
    """Rebind the local parameter without replacing the caller's list."""
    items = ["replacement"]
    return items


if __name__ == "__main__":
    # This block demonstrates the functions only when the file is executed.
    # Importing it from another module defines the functions without printing.
    print(greet("Ada"))
    print("add(2, 3) =", add(2, 3))
    print("add(5) =", add(5))
    print(describe_person("Grace", 34, city="London"))
    print(describe_person("Alan", 40))
    print("divide(10, 2) =", divide(10, 2))
    print(make_label("Read the next lesson", prefix="Task"))
    print(format_measurement(12.345, "cm", precision=2))

    # At a call site, * unpacks an iterable into positional arguments and **
    # unpacks a mapping into keyword arguments.
    person = ("Sam", 28)
    location = {"city": "Bristol"}
    print(describe_person(*person, **location))

    print("sum_all(1, 2, 3, 4) =", sum_all(1, 2, 3, 4))
    print("print_info(...):")
    print_info(language="Python", level="beginner")

    message_result = show_message("This function prints instead of returning.")
    print("show_message returned:", message_result)

    # A call binds parameter names to argument objects, much like assignment.
    # Mutating that object is visible to the caller; assigning a new object to
    # the parameter only rebinds the local name.
    topics = ["signatures"]
    append_item(topics, "return values")
    replacement_topics = replace_items(topics)
    print("After mutation:", topics)
    print("Returned after local rebinding:", replacement_topics)
