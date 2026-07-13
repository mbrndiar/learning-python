"""
Lesson 1.2: Variables and Basic Data Types

Python is dynamically typed: you don't need to declare a variable's type,
it is inferred from the value you assign to it.
"""

# Numbers
age = 25            # int
height = 1.75        # float

# Text
name = "Ada"         # str

# Boolean
is_learning = True   # bool

# None represents "no value"
favorite_color = None

print("name:", name, "| type:", type(name))
print("age:", age, "| type:", type(age))
print("height:", height, "| type:", type(height))
print("is_learning:", is_learning, "| type:", type(is_learning))
print("favorite_color:", favorite_color, "| type:", type(favorite_color))

# You can reassign a variable to a different type at any time.
favorite_color = "blue"
print("favorite_color is now:", favorite_color)
