"""Internal formatting helpers for the exercise package."""


def _shout(text: str) -> str:
    return text.upper() + "!"


def _titlecase(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())
