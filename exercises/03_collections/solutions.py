"""
Solutions: Chapter 3 - Collections

Reference implementation for exercises/03_collections/exercises.py.
Try to solve the exercises yourself before checking this file!
"""

# --- Task 1: mutate one byte, leave the original bytes untouched ----------
original_code = b"A1B2"

mutable_code = bytearray(original_code)
mutable_code[1] = ord("X")
updated_code = bytes(mutable_code)

assert updated_code == b"AXB2"
assert original_code == b"A1B2"
print("Task 1 (mutate one byte): OK")

# --- Task 2: in-place list mutation is visible through every alias --------
topics = ["variables", "loops"]
topics_alias = topics

topics_alias.append("recursion")

assert topics == ["variables", "loops", "recursion"]
assert topics_alias == topics
assert topics_alias is topics
print("Task 2 (in-place mutation through an alias): OK")

# --- Task 3: unique, sorted values -----------------------------------------
readings = [7, 3, 7, 1, 3, 9, 1]

unique_readings = sorted(set(readings))

assert unique_readings == [1, 3, 7, 9]
print("Task 3 (unique, sorted values): OK")

# --- Task 4: dict construction, lookup, update, and membership ------------
inventory = {"pencils": 12, "erasers": 4}

inventory["rulers"] = 6
inventory["erasers"] = 10
stapler_count = inventory.get("staplers", 0)
has_pencils = "pencils" in inventory

assert inventory == {"pencils": 12, "erasers": 10, "rulers": 6}
assert stapler_count == 0
assert has_pencils is True
print("Task 4 (dict construction, lookup, update, membership): OK")

# --- Task 5: set algebra ----------------------------------------------------
backend_tags = {"python", "sql", "testing"}
frontend_tags = {"javascript", "testing", "css"}

shared_tags = backend_tags & frontend_tags
all_tags = backend_tags | frontend_tags
backend_only_tags = backend_tags - frontend_tags

assert shared_tags == {"testing"}
assert all_tags == {"python", "sql", "testing", "javascript", "css"}
assert backend_only_tags == {"python", "sql"}
print("Task 5 (set algebra): OK")

# --- Task 6: shallow copy versus shared inner mutation ---------------------
grouped = [["red", "green"], ["small", "medium"]]
grouped_copy = grouped.copy()

grouped_copy[0].append("blue")
grouped_copy[1] = ["large"]

assert grouped == [["red", "green", "blue"], ["small", "medium"]]
assert grouped_copy == [["red", "green", "blue"], ["large"]]
print("Task 6 (shallow copy versus shared inner mutation): OK")

print("\nAll checks passed!")
