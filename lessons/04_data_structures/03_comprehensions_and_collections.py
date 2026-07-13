"""
Lesson 4.3: Comprehensions and the `collections` Module

This lesson dives deeper into comprehensions (list, dict and set) and
introduces some of the most useful classes from the `collections` module.
"""

from collections import Counter, defaultdict, namedtuple, OrderedDict


# --- Comprehensions -------------------------------------------------------
numbers = range(1, 11)

# List comprehension with a condition
even_squares = [n ** 2 for n in numbers if n % 2 == 0]

# Dict comprehension
square_lookup = {n: n ** 2 for n in numbers}

# Set comprehension (duplicates are removed automatically)
remainders = {n % 3 for n in numbers}

# Nested comprehension: flatten a list of lists
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [value for row in matrix for value in row]

# Generator expression: like a list comprehension, but lazy (computed
# on demand instead of all at once), saving memory for large sequences.
sum_of_squares = sum(n ** 2 for n in numbers)


# --- collections.Counter --------------------------------------------------
text = "the quick brown fox jumps over the lazy dog the fox runs"
word_counts = Counter(text.split())


# --- collections.defaultdict ----------------------------------------------
def group_by_first_letter(words):
    """Group words by their first letter using defaultdict(list)."""
    groups = defaultdict(list)
    for word in words:
        groups[word[0]].append(word)
    return groups


# --- collections.namedtuple -----------------------------------------------
Point = namedtuple("Point", ["x", "y"])


if __name__ == "__main__":
    print("even_squares:", even_squares)
    print("square_lookup:", square_lookup)
    print("remainders:", remainders)
    print("flattened matrix:", flattened)
    print("sum_of_squares:", sum_of_squares)

    print("\nword_counts:", word_counts)
    print("most common 2:", word_counts.most_common(2))

    grouped = group_by_first_letter(["apple", "avocado", "banana", "cherry", "blueberry"])
    print("\ngrouped by first letter:")
    for letter, words in grouped.items():
        print(f"  {letter}: {words}")

    p1 = Point(3, 4)
    print("\nnamedtuple point:", p1)
    print("p1.x =", p1.x, "| p1.y =", p1.y)

    ordered = OrderedDict()
    ordered["first"] = 1
    ordered["second"] = 2
    ordered["third"] = 3
    print("\nOrderedDict:", ordered)
