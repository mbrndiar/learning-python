"""
Exercises: 04 Data Structures

Implement each function below, then run this file directly to check
your work.
"""


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
    print("flatten: OK")

    print("\nAll checks passed!")
