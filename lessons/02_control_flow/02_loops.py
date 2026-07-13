"""
Lesson 2.2: Loops (for / while)

Loops let you repeat actions without duplicating code. A for loop consumes an
iterable; a while loop repeats for as long as its condition remains truthy.
"""

# range's stop value is exclusive, so range(1, 6) yields 1 through 5.
print("Counting from 1 to 5:")
for i in range(1, 6):
    print(i)

# for loop over a list
fruits = ["apple", "banana", "cherry"]
print("\nFruits:")
for fruit in fruits:
    print("-", fruit)

# The body must eventually make the condition false unless an intentional
# infinite loop is exited with break.
print("\nCountdown:")
countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Liftoff!")

# break exits the nearest loop. continue skips the rest of only the current
# iteration and asks the loop for its next value.
print("\nSkip even numbers, stop at 7:")
for number in range(1, 10):
    if number == 7:
        break
    if number % 2 == 0:
        continue
    print(number)
