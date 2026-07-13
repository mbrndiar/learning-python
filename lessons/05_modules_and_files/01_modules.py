"""
Lesson 5.1: Modules and Imports

Python's standard library provides many useful modules.
You can also organize your own code into modules and import it.
"""

import math
import random
# This form imports one name directly instead of the whole module namespace.
from datetime import date

# A module name makes the origin of its attributes explicit.
print("Square root of 16:", math.sqrt(16))
print("Value of pi:", math.pi)

# Without a fixed seed, repeated runs can produce different values.
print("Random number between 1 and 10:", random.randint(1, 10))

# Because date was imported directly, this call does not need datetime.date.
print("Today's date:", date.today())
