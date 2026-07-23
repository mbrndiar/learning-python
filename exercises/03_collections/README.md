# 📦 Exercises: Chapter 3 - Collections

Practice problems for
[`lessons/03_collections/`](../../lessons/03_collections/README.md). Every
task here is solvable with construction, indexing, membership tests, and
methods -- no `for`, `while`, comprehensions, `zip`, or `def` (Chapter 4
teaches iteration; Chapter 5 teaches `def`).

## 🧩 Tasks in `exercises.py`

- **Task 1 - mutate one byte:** replace one byte inside `bytes` data via a
  `bytearray`, leaving the original untouched.
- **Task 2 - in-place mutation through an alias:** append to a list through
  a second name bound to the same object, and confirm both names see the
  change.
- **Task 3 - unique, sorted values:** deduplicate a list of numbers with
  `set()` and order it with `sorted()`.
- **Task 4 - dict construction, lookup, update, and membership:** add a key,
  update a key, use `.get()` with a default, and test `in`.
- **Task 5 - set algebra:** compute the union, intersection, and difference
  of two tag sets.
- **Task 6 - shallow copy versus shared inner mutation:** show that mutating
  a shared inner list through a shallow copy is visible in the original,
  while replacing an inner element is not.

## ▶️ How to work through it

1. Read
   [`lessons/03_collections/README.md`](../../lessons/03_collections/README.md)
   first.
2. Open `exercises.py` and complete each statement marked `# TODO`.
3. Run it:

   ```bash
   python exercises/03_collections/exercises.py
   ```

4. The first failing `assert` names the incomplete task. Fix it, rerun, and
   repeat until you see `All checks passed!`.
5. Compare with `solutions.py` if you get stuck.

## 🔍 Inputs, outputs, and constraints

- Task 1 must not modify `original_code`; only `updated_code` should differ.
- Task 2 requires mutating the *same* list object through `topics_alias`
  (for example, `topics_alias.append(...)`) rather than rebinding either
  name to a new list.
- Task 4 must not rebind `inventory` to a new dict literal; every step
  mutates the same dict object.
- Task 6 requires one in-place mutation (`grouped_copy[0].append(...)`,
  visible through `grouped`) and one replacement
  (`grouped_copy[1] = [...]`, not visible through `grouped`) -- getting
  either one backwards will fail its assertion.
