"""
Solutions: 04 Data Structures
"""


def unique_sorted(numbers):
    return sorted(set(numbers))


def invert_dict(mapping):
    return {value: key for key, value in mapping.items()}


def word_frequencies(words):
    frequencies = {}
    for word in words:
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies


def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]


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
