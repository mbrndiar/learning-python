"""
Lesson 4.1: Lists and Tuples

Lists are mutable ordered collections; methods can change the same list
object. Tuples are immutable ordered collections, although a tuple may still
contain a mutable object such as a list.
"""

# Lists are mutable: append(), remove(), and sort() below all change this same
# object in place. Any other name bound to the list would observe those changes.
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print("original list:", numbers)

numbers.append(10)
print("after append(10):", numbers)

numbers.remove(1)  # removes the first occurrence of 1
print("after remove(1):", numbers)

# list.sort() mutates `numbers` and returns None. sorted(numbers) would return
# a new list and leave the original order unchanged.
numbers.sort()
print("sorted:", numbers)

print("first element:", numbers[0])
print("last element:", numbers[-1])
# Slicing returns a new list; changing that top-level list would not resize
# `numbers`, although nested mutable objects would still be shared.
print("slice [1:4]:", numbers[1:4])

# A shallow copy duplicates only the outer list. Nested mutable values remain
# shared, so changing one of them is visible through both outer lists.
nested = [["Ada"], ["Grace"]]
shallow_copy = nested.copy()
shallow_copy[0].append("Lovelace")
print("nested after changing its shallow copy:", nested)

# A comprehension builds a new list by evaluating its expression once for
# each input value.
squares = [n**2 for n in numbers]
print("squares:", squares)

# A tuple fixes its sequence of references. The referenced objects themselves
# can still be mutable, so tuple immutability is not recursive.
point = (3, 4)
print("\npoint:", point)
# Unpacking requires the number of targets to match the number of values unless
# a starred target captures the remainder.
x, y = point
print(f"x={x}, y={y}")

try:
    point[0] = 10  # this will raise an error because tuples are immutable
except TypeError as error:
    print("Error modifying tuple:", error)
