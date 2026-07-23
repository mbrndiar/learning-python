"""Implementation details for the public greeting API."""


def greet(name: str, *, excited: bool = False) -> str:
    """Return a greeting for ``name``.

    Args:
        name: Person to greet. Surrounding whitespace is ignored.
        excited: End the greeting with an exclamation mark instead of a period.

    Returns:
        A greeting containing the cleaned name.

    Raises:
        ValueError: If ``name`` is empty or contains only whitespace.
    """
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("name must not be empty")

    punctuation = "!" if excited else "."
    return f"Hello, {cleaned_name}{punctuation}"
