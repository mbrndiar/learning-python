"""
Lesson 2.2: Loops (for / while)

Loops let you repeat actions without duplicating code.
"""

# for loop over a range of numbers
print("Counting from 1 to 5:")
for i in range(1, 6):
    print(i)

# for loop over a list
fruits = ["apple", "banana", "cherry"]
print("\nFruits:")
for fruit in fruits:
    print("-", fruit)

# while loop
print("\nCountdown:")
countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Liftoff!")

# break and continue
print("\nSkip even numbers, stop at 7:")
for number in range(1, 10):
    if number == 7:
        break
    if number % 2 == 0:
        continue
    print(number)
