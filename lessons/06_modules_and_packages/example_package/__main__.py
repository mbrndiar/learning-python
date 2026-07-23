"""
Package entry point for ``python -m example_package``.

A package that defines ``__main__.py`` can be executed directly with
``python -m example_package``: Python imports the package (running
``__init__.py``) and then runs this module as ``__main__``. This is the
standard way to give a package a runnable command without exposing an
internal module path.
"""

from example_package import hello

if __name__ == "__main__":
    print(hello("package runner"))
