"""
Lesson 4.2: Dictionaries and Sets

Dictionaries map unique, hashable keys to values and preserve insertion order.
Sets store unique, hashable values without a promised iteration order.
"""

# Dictionary keys must be hashable so their lookup identity remains stable.
# Values have no such restriction and may be mutable.
person = {
    "name": "Ada Lovelace",
    "occupation": "Mathematician",
    "year_born": 1815,
}

# Bracket lookup expresses "this key must exist" and raises KeyError otherwise.
print("name:", person["name"])
person["occupation"] = "Computer Scientist"  # update a value
person["nationality"] = "British"  # add a new key
print("updated person:", person)

# items() provides key-value pairs that can be unpacked by the loop.
for key, value in person.items():
    print(f"  {key}: {value}")

# get() expresses optional lookup and returns the supplied default instead of
# raising KeyError. Do not use it when a missing key is actually a data error.
print("hobby:", person.get("hobby", "Not specified"))

# Duplicate values collapse into one member. Printed order may vary by run.
languages = {"Python", "JavaScript", "Python", "Go"}
print("\nlanguages (duplicates removed):", languages)

languages.add("Rust")
print("after add:", languages)

other_languages = {"Go", "Rust", "Java"}
# Set algebra creates new sets here; it does not mutate either input set.
print("intersection:", languages & other_languages)
print("union:", languages | other_languages)
print("difference:", languages - other_languages)
