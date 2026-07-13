"""
Lesson 2.1: Conditional Statements (if / elif / else)

Conditionals let a program choose one path. Python tests branches from top to
bottom and executes only the first branch whose expression is truthy.
"""

temperature = 22

# Ordering matters: if `temperature > 30` were placed after `> 20`, the more
# specific branch could never run.
if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("It's a pleasant day.")
elif temperature > 10:
    print("It's a bit chilly.")
else:
    print("It's cold outside!")

# A conditional expression is useful for choosing one of two simple values.
# Prefer a normal if statement when either branch needs several operations.
is_weekend = True
plan = "Relax" if is_weekend else "Work"
print("Today's plan:", plan)
