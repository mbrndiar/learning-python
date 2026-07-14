"""
Lesson 1.2: Variables and Basic Data Types

Python is dynamically typed: you don't declare a name's permanent type.
Assignment binds a name to an object, and every object has a type. The same
name can later be rebound, although keeping its meaning consistent usually
makes code easier to understand.
"""

# Numbers
age = 25  # int
height = 1.75  # float

# Text
name = "Ada"  # str

# Boolean
is_learning = True  # bool

# None is a unique sentinel representing "no value"; it is not zero or "".
favorite_color = None

print("name:", name, "| type:", type(name))
print("age:", age, "| type:", type(age))
print("height:", height, "| type:", type(height))
print("is_learning:", is_learning, "| type:", type(is_learning))
print("favorite_color:", favorite_color, "| type:", type(favorite_color))

# This rebinds the name. It does not modify the None object used above.
favorite_color = "blue"
print("favorite_color is now:", favorite_color)
