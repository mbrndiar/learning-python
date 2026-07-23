"""
Solutions: Chapter 4 - Flow and Iteration

Reference solutions for exercises/04_control_flow/exercises.py.

Run this file directly:

    python exercises/04_control_flow/solutions.py
"""

from collections import Counter, defaultdict

# --- Task 1: FizzBuzz, 1..15 ------------------------------------------------
fizzbuzz_lines = []
for number in range(1, 16):
    if number % 15 == 0:
        fizzbuzz_lines.append("FizzBuzz")
    elif number % 3 == 0:
        fizzbuzz_lines.append("Fizz")
    elif number % 5 == 0:
        fizzbuzz_lines.append("Buzz")
    else:
        fizzbuzz_lines.append(str(number))

assert fizzbuzz_lines[:5] == ["1", "2", "Fizz", "4", "Buzz"]
assert fizzbuzz_lines[-1] == "FizzBuzz"
print("Task 1 (FizzBuzz): OK")

# --- Task 2: count even numbers --------------------------------------------
readings = [3, 8, 15, 22, 41, 6, 7]
even_count = 0
for value in readings:
    if value % 2 == 0:
        even_count += 1

assert even_count == 3
print("Task 2 (count evens): OK")

# --- Task 3: first negative, stop looking once found -----------------------
measurements = [12, 4, -7, 30, -2]
for value in measurements:
    if value < 0:
        first_negative = value
        break
else:
    first_negative = None

assert first_negative == -7
print("Task 3 (first negative, with break/else): OK")

# --- Task 4: sum while skipping multiples of three (continue) -------------
skip_multiples_of_three_total = 0
for number in range(1, 21):
    if number % 3 == 0:
        continue
    skip_multiples_of_three_total += number

assert skip_multiples_of_three_total == 147
print("Task 4 (sum skipping multiples of three): OK")

# --- Task 5: index of first match, via enumerate ---------------------------
fruit_order = ["mango", "fig", "kiwi", "kiwi", "date"]
for index, fruit in enumerate(fruit_order):
    if fruit == "kiwi":
        kiwi_index = index
        break
else:
    kiwi_index = -1

assert kiwi_index == 2
print("Task 5 (index of first match via enumerate): OK")

# --- Task 6: pair two lists with zip ---------------------------------------
items = ["bolts", "washers", "nuts"]
quantities = [50, 120, 75]
shipment_lines = [f"{name} x{quantity}" for name, quantity in zip(items, quantities)]

assert shipment_lines == ["bolts x50", "washers x120", "nuts x75"]
print("Task 6 (pair two lists with zip): OK")

# --- Task 7: invert a dictionary --------------------------------------------
id_by_role = {"admin": 1, "editor": 2, "viewer": 3}
role_by_id = {value: key for key, value in id_by_role.items()}

assert role_by_id == {1: "admin", 2: "editor", 3: "viewer"}
print("Task 7 (invert a dictionary): OK")

# --- Task 8: manual word frequencies ---------------------------------------
tags = ["bug", "feature", "bug", "docs", "bug", "feature"]
tag_counts = {}
for tag in tags:
    tag_counts[tag] = tag_counts.get(tag, 0) + 1

assert tag_counts == {"bug": 3, "feature": 2, "docs": 1}
print("Task 8 (manual word frequencies): OK")

# --- Task 9: most common tags, via Counter ---------------------------------
top_two_tags = Counter(tags).most_common(2)

assert top_two_tags == [("bug", 3), ("feature", 2)]
print("Task 9 (most common tags via Counter): OK")

# --- Task 10: group words by length, via defaultdict -----------------------
catalog = ["ax", "saw", "bit", "drill", "nail", "rope"]
grouped_by_length = defaultdict(list)
for word in catalog:
    grouped_by_length[len(word)].append(word)
by_length = dict(grouped_by_length)

assert by_length == {
    2: ["ax"],
    3: ["saw", "bit"],
    4: ["nail", "rope"],
    5: ["drill"],
}
print("Task 10 (group by length via defaultdict): OK")

print("\nAll checks passed!")
