"""
Exercises: 04 Data Structures

Implement each function below, then run this file directly to check
your work.
"""

from collections import Counter, defaultdict


def unique_sorted(numbers):
    """Return a sorted list of the unique values in `numbers`."""
    # TODO: implement this function
    raise NotImplementedError


def invert_dict(mapping):
    """Return a new dict with keys and values swapped.

    Example: {"a": 1, "b": 2} -> {1: "a", 2: "b"}
    """
    # TODO: implement this function
    raise NotImplementedError


def word_frequencies(words):
    """Return a dict mapping each word to how many times it appears
    in the list `words`."""
    # TODO: implement this function
    raise NotImplementedError


def flatten(nested_list):
    """Flatten a list of lists into a single list, one level deep.

    Example: [[1, 2], [3], [4, 5]] -> [1, 2, 3, 4, 5]
    """
    # TODO: implement this function
    raise NotImplementedError


def most_common_words(words, count):
    """Return the `count` most common (word, frequency) pairs.

    Preserve Counter.most_common() ordering for ties.
    """
    # TODO: implement this function with collections.Counter
    raise NotImplementedError


def group_by_length(words):
    """Return a normal dict mapping word lengths to lists of words."""
    # TODO: implement this function with defaultdict(list)
    raise NotImplementedError


if __name__ == "__main__":
    assert unique_sorted([3, 1, 2, 1, 3]) == [1, 2, 3]
    print("unique_sorted: OK")

    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    print("invert_dict: OK")

    assert word_frequencies(["a", "b", "a", "c", "b", "a"]) == {
        "a": 3,
        "b": 2,
        "c": 1,
    }
    print("word_frequencies: OK")

    assert flatten([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]
    assert flatten([]) == []
    print("flatten: OK")

    assert most_common_words(["b", "a", "b", "c", "a", "b"], 2) == [
        ("b", 3),
        ("a", 2),
    ]
    print("most_common_words: OK")

    assert group_by_length(["a", "to", "be", "cat"]) == {
        1: ["a"],
        2: ["to", "be"],
        3: ["cat"],
    }
    print("group_by_length: OK")

    print("\nAll checks passed!")
