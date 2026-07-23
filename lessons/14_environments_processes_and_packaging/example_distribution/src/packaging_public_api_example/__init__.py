"""A small, documented public API for the packaging lesson."""

# Re-exporting from the package root gives callers a stable public import path.
from ._greetings import greet

__all__ = ["greet"]
