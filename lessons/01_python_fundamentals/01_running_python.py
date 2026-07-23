"""
Chapter 1, Lesson 1: Running Python

Purpose: show how a Python source file becomes running output, and introduce
comments and `print()` as the two tools used throughout the rest of this file.

Prerequisites: none. This is the first lesson in the course.

Read this file top to bottom, predict each `print()` output on paper first,
then run it with:

    python lessons/01_python_fundamentals/01_running_python.py
"""

# Anything after a `#` on a line is a comment: Python ignores it completely.
# Comments explain *why* code does something; the code itself already shows
# *what* it does.

# A statement is one instruction. Python executes statements from top to
# bottom, in order, unless something later in the course changes that order.
print("Hello, World!")

# print() can take more than one value. It prints them separated by a single
# space, then moves to a new line automatically.
print("Learning", "Python", "starts", "here.")

# print() accepts a `sep` keyword argument to change that default separator.
# This does not change how print() joins later calls; it is scoped to the
# single call it is passed to.
print("2026", "07", "23", sep="-")

# A string is text between quotes. Both single and double quotes work; this
# course prefers double quotes and uses single quotes mainly when the text
# itself contains a double quote.
print("Single quotes work too.")
print("A string can contain an apostrophe, like Ada's notebook.")

# Running this file executed every statement above, in source order, exactly
# once. There is no hidden entry point yet -- that idea (`__name__` guards)
# is introduced later, once the course starts writing functions.
