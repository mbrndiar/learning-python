"""
Chapter 10, Lesson 1: Iterables, Iterators, and StopIteration

Purpose: distinguish an *iterable* (an object `iter()` can be called on)
from an *iterator* (an object `next()` can be called on, remembering
where it is); implement the iterator protocol (`__iter__`/`__next__`)
directly; and see `StopIteration` as the protocol's ordinary completion
signal, which a `for` loop catches for you automatically.

Prerequisites: Chapter 9 (objects and data models) -- this lesson defines
a class with `__iter__`/`__next__`, building directly on Chapter 9's
`Playlist.__iter__` example.

Read this file top to bottom, predict each output, then run it:

    python lessons/10_iteration_decorators_and_contexts/01_iterables_iterators_and_stopiteration.py
"""

# Step 1: a list is iterable (iter(list) works) but is not itself an
# iterator -- calling iter() on it produces a separate iterator object
# that tracks position independently of the list.
numbers = [10, 20, 30]
iterator_a = iter(numbers)
iterator_b = iter(numbers)
print("next(iterator_a):", next(iterator_a))
print("next(iterator_a) again:", next(iterator_a))
print("next(iterator_b) (independent position):", next(iterator_b))

# Step 2: next() raises StopIteration when an iterator is exhausted. A
# for loop calls next() repeatedly and catches StopIteration internally
# -- that is the entire mechanism a for loop uses under the hood.
final_iterator = iter([1, 2])
next(final_iterator)
next(final_iterator)
try:
    next(final_iterator)
except StopIteration:
    print("\nStopIteration raised once the iterator is exhausted")


class CountUp:
    """A custom iterator implemented directly with the iterator protocol.

    Implementing __iter__ and __next__ lets an object work with `for`
    loops, `next()`, and other iteration tools -- exactly like the list
    iterator above, but with custom logic controlling what "next" means.
    """

    def __init__(self, start, stop):
        self.current = start
        self.stop = stop

    def __iter__(self):
        # Returning self makes this object its own iterator. Once
        # exhausted, the same CountUp instance cannot restart --
        # a fresh CountUp(...) is needed to count again.
        return self

    def __next__(self):
        if self.current >= self.stop:
            # StopIteration is the protocol's normal completion signal,
            # not an error condition to work around.
            raise StopIteration
        value = self.current
        self.current += 1
        return value


# Step 3: a for loop over CountUp(1, 4) calls iter() once (getting the
# instance itself back) and then next() repeatedly until StopIteration.
print("\nfor loop over CountUp(1, 4):")
for value in CountUp(1, 4):
    print(" ", value)

# Step 4: next() can also be called manually, one value at a time.
manual = iter(CountUp(5, 7))
print("\nManual iteration with next():")
print(" ", next(manual))
print(" ", next(manual))
try:
    next(manual)
except StopIteration:
    print("  StopIteration raised: no more values")

# --- One-variable experiment -------------------------------------------
# Change CountUp(1, 4) in the for loop above to CountUp(4, 4) (an empty
# range) and predict what the loop prints. The __next__ method's first
# comparison (self.current >= self.stop) is what decides this -- no
# change to the for loop itself is needed.
