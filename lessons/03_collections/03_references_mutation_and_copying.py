"""
Chapter 3, Lesson 3: References, Mutation, and Copying

Purpose: distinguish aliasing (two names, one object) from equality; show
how in-place mutation is visible through every alias; and contrast a
shallow copy with a deep, independent one. `bytearray` reappears here as
another basic mutable sequence with the same aliasing rules as lists.

Prerequisites: 01_lists_and_tuples.py, 02_dictionaries_and_sets.py.

Read this file top to bottom, predict each output, then run it:

    python lessons/03_collections/03_references_mutation_and_copying.py
"""

# Step 1: assignment binds a name to an existing object; it does not copy
# it. `roster` and `team` are two different names for the *same* list, so a
# mutation through either name is visible through both.
roster = ["Ada", "Grace"]
team = roster
team.append("Alan")
print("roster:", roster)
print("team:", team)
print("roster is team:", roster is team)  # same object, not just equal

# `is` tests object identity; `==` tests equality of value. Two distinct,
# equal lists are `==` but not `is`.
other_roster = ["Ada", "Grace", "Alan"]
print("roster == other_roster:", roster == other_roster)
print("roster is other_roster:", roster is other_roster)

# Step 2: rebinding a name (assigning a *new* object to it) breaks the
# alias -- it does not affect any other name that still points to the
# original object.
team = ["Replacement"]
print("\nafter rebinding team, roster is still:", roster)
print("team is now:", team)

# Step 3: list.copy() (or list(original)) creates a *shallow* copy: a new
# outer list containing the same inner references. Mutating the new outer
# list does not affect the original...
original = [1, 2, 3]
shallow = original.copy()
shallow.append(4)
print("\noriginal after mutating its shallow copy:", original)
print("shallow:", shallow)

# ...but if an element is itself mutable, both the original and the shallow
# copy still share that same inner object.
nested = [["Ada"], ["Grace"]]
shallow_nested = nested.copy()
shallow_nested[0].append("Lovelace")  # mutates the inner list, shared by both
print("\nnested after mutating shallow_nested's inner list:", nested)
print("shallow_nested:", shallow_nested)

# Replacing an inner element (rather than mutating it) does not reach back,
# because that rebinds shallow_nested[1] to a brand-new list.
shallow_nested[1] = ["Hopper"]
print("nested unaffected by replacing shallow_nested[1]:", nested)

# Step 4: bytearray follows the same aliasing rules as list. Two names for
# one bytearray share mutations; bytearray(original) makes an independent
# copy, just like list.copy() does for lists.
buffer = bytearray(b"cat")
alias = buffer
independent_copy = bytearray(buffer)

alias[0] = ord("h")
independent_copy[0] = ord("b")
print("\nbuffer (mutated through alias):", buffer)
print("alias:", alias)
print("independent_copy (unaffected by alias mutation):", independent_copy)

# --- One-variable experiment -------------------------------------------
# In Step 3, change `shallow_nested[0].append("Lovelace")` to
# `shallow_nested[0] = ["Somerville"]` (replacement instead of mutation) and
# predict whether `nested` changes before rerunning.
