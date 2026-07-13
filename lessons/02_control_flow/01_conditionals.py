"""
Lesson 2.1: Conditional Statements (if / elif / else)

Conditionals let your program make decisions.
"""

temperature = 22

if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("It's a pleasant day.")
elif temperature > 10:
    print("It's a bit chilly.")
else:
    print("It's cold outside!")

# Conditional (ternary) expression
is_weekend = True
plan = "Relax" if is_weekend else "Work"
print("Today's plan:", plan)
