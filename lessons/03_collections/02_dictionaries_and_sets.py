"""
Chapter 3, Lesson 2: Dictionaries and Sets

Purpose: construct dictionaries and sets, look up and update values, test
membership, and observe hashability and set algebra. Dictionary items are
inspected with `list(d.items())` for deterministic printing -- looping over
them is Chapter 4's subject, not this one's.

Prerequisites: 01_lists_and_tuples.py.

Read this file top to bottom, predict each output, then run it:

    python lessons/03_collections/02_dictionaries_and_sets.py
"""

# Step 1: a dict maps unique, hashable keys to values and preserves
# insertion order. Bracket lookup expresses "this key must exist" and
# raises KeyError if it does not.
person = {
    "name": "Ada Lovelace",
    "occupation": "Mathematician",
    "year_born": 1815,
}
print("name:", person["name"])

# Step 2: update an existing key, add a new one, and remove one. All three
# mutate the same dict object.
person["occupation"] = "Computer Scientist"  # update
person["nationality"] = "British"  # add
removed_year = person.pop("year_born")  # remove and return the value
print("\nupdated person:", person)
print("removed year_born:", removed_year)

# Step 3: get() expresses optional lookup -- it returns a default instead of
# raising KeyError. `in` tests key membership without retrieving a value.
print("\nhobby (missing):", person.get("hobby", "Not specified"))
print("'name' in person:", "name" in person)
print("'hobby' in person:", "hobby" in person)

# Step 4: .keys(), .values(), and .items() return *view* objects, not lists.
# Converting one to a list makes its deterministic content printable without
# looping over it -- for loops arrive in Chapter 4.
print("\nkeys:", list(person.keys()))
print("items:", list(person.items()))

# Step 5: hashability. Dictionary (and set) membership requires a stable
# hash, so keys must be immutable-and-hashable types such as str, int, or
# tuple. A list is unhashable because it is mutable; the commented invalid
# dictionary below would raise TypeError.
coordinates_lookup = {(0, 0): "origin", (1, 1): "diagonal"}
print("\ntuple key lookup:", coordinates_lookup[(0, 0)])
# invalid_lookup = {[1, 2]: "invalid"}

# Step 6: a set stores unique, hashable values with no promised iteration
# order. Constructing one from a list is a common way to deduplicate.
languages = {"Python", "JavaScript", "Python", "Go"}
print("\nlanguages (duplicates removed):", sorted(languages))
languages.add("Rust")
languages.discard("Go")  # like remove(), but does not raise if missing
print("after add/discard:", sorted(languages))

other_languages = {"Go", "Rust", "Java"}
print("intersection:", sorted(languages & other_languages))
print("union:", sorted(languages | other_languages))
print("difference:", sorted(languages - other_languages))
print("symmetric difference:", sorted(languages ^ other_languages))

# --- One-variable experiment -------------------------------------------
# Change `other_languages` to an empty set, `set()`, and predict the
# printed intersection, union, and difference before rerunning.
