"""
Chapter 4, Lesson 1: Conditions and Truthiness

Purpose: give `if`/`elif`/`else` full treatment as multi-branch statements
(Chapter 1 only used a bounded conditional-expression preview), trace how
branches are chosen, and combine comparisons with membership tests.

Prerequisites: Chapter 3 (collections, for the `in` membership examples).

Read this file top to bottom, predict each output, then run it:

    python lessons/04_control_flow/01_conditions_and_truthiness.py
"""

# Step 1: an `if` statement tests branches from top to bottom and runs only
# the first one whose condition is truthy. Order matters: a more specific
# condition must come before a more general one that would otherwise always
# match first.
temperature = 22

if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("It's a pleasant day.")
elif temperature > 10:
    print("It's a bit chilly.")
else:
    print("It's cold outside!")

# Step 2: any condition Python can evaluate to truthy/falsy is valid --
# not only comparisons. An empty collection, empty string, or zero is
# falsy; a non-empty one is truthy.
pending_tasks = []
if pending_tasks:
    print("\nThere is work to do.")
else:
    print("\nNothing pending.")

pending_tasks.append("write report")
if pending_tasks:
    print("There is work to do.")
else:
    print("Nothing pending.")

# Step 3: membership (`in`) combines naturally with a condition. It works on
# strings, lists, tuples, dicts (tests keys), and sets.
allowed_roles = {"admin", "editor"}
current_role = "editor"
if current_role in allowed_roles:
    print(f"\n{current_role!r} may proceed.")
else:
    print(f"\n{current_role!r} is not authorized.")

# Step 4: conditions can be combined with `and`/`or`/`not`, and chained
# comparisons (from Chapter 2) work the same way inside an `if`.
age = 25
has_ticket = True
if 18 <= age < 65 and has_ticket:
    print("\nStandard admission.")
elif age >= 65 and has_ticket:
    print("\nSenior admission.")
else:
    print("\nAdmission denied.")

# Step 5: nested conditionals trace one branch at a time. Reading a nested
# `if` means finding the first true condition at the outer level, then
# repeating that process one level deeper.
account_balance = 120
requested_amount = 50
is_frozen = False

if is_frozen:
    print("\nAccount is frozen; no withdrawals allowed.")
else:
    if requested_amount <= account_balance:
        print(f"\nWithdrawal of {requested_amount} approved.")
    else:
        print(f"\nInsufficient funds for {requested_amount}.")

# --- One-variable experiment -------------------------------------------
# Change `requested_amount` to 200 (greater than account_balance) and
# predict which branch prints before rerunning.
