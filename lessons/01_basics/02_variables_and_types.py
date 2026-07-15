"""
Lesson 1.2: Variables and Basic Data Types

Python is dynamically typed: you don't declare a name's permanent type.
Assignment binds a name to an object, and every object has a type. The same
name can later be rebound, although keeping its meaning consistent usually
makes code easier to understand.
"""

# A literal creates a value object; assignment binds a name to that object.
# The name itself does not contain a declared type.
age = 25  # int
height = 1.75  # float

# Strings hold text as Unicode characters, not raw bytes.
name = "Ada"  # str

# bool is its own type even though True and False also behave like 1 and 0 in
# some numeric contexts. Prefer using booleans to express conditions.
is_learning = True  # bool

# None is a unique sentinel representing "no value"; it is not zero or "".
favorite_color = None

# type() inspects the object currently bound to a name. Rebinding the name can
# therefore change what type() reports later.
print("name:", name, "| type:", type(name))
print("age:", age, "| type:", type(age))
print("height:", height, "| type:", type(height))
print("is_learning:", is_learning, "| type:", type(is_learning))
print("favorite_color:", favorite_color, "| type:", type(favorite_color))

# This rebinds the name. It does not modify the None object used above.
favorite_color = "blue"
print("favorite_color is now:", favorite_color)
