"""
Chapter 6, Lesson 3: Scripts, Modules, and Public APIs

Purpose: `__name__` and how it distinguishes "run as a script" from
"imported as a module"; import-time side effects; guarded entry points;
re-exports; and `__all__` as a way to declare a small public API.

Prerequisites: Lessons 1-2 (modules, imports, packages). This lesson adds
two tiny sibling files, `greeting_module.py` and `facade.py`, in this same
directory.

Read this file top to bottom, predict each output, then run it:

    python lessons/06_modules_and_packages/03_scripts_modules_and_public_apis.py
"""

# Step 1: every module has a `__name__`. When Python runs a file directly
# (as the program's entry point), that file's `__name__` is set to the
# string "__main__". When the same file is instead *imported*, its
# `__name__` is its module name. This is the only difference -- the code
# runs exactly the same way either time.
print("This file's __name__ right now:", __name__)
# Because this file was run directly, the line above prints "__main__".

# Step 2: import-time side effects. Importing a module runs its top-level
# code immediately, once, in file order -- not just its function
# definitions. Open greeting_module.py: it prints a line at the top level,
# outside any function.
print("\nAbout to import greeting_module for the first time...")
import greeting_module  # noqa: E402 -- import timing is the point of this step

print("...import finished.")

# Step 3: a second import of an already-cached module does not re-run its
# top-level code (Lesson 1 covered the sys.modules cache) -- so importing
# it again prints nothing further.
print("\nImporting greeting_module again (already cached):")
import greeting_module  # noqa: E402, F811 -- re-imported to show no reprint

print("get_greeting result:", greeting_module.get_greeting("Ada"))

# Step 4: a *guarded* entry point. greeting_module.py also defines
# `if __name__ == "__main__": ...` around its own demo output. Because we
# reached it through `import`, that guarded block did NOT run -- only the
# unconditional top-level print from Step 2 did. Running the same file
# directly as a script gives it __name__ == "__main__" instead, so the
# guarded block DOES run. Run the printed command after this lesson to observe
# both lines directly; process creation itself is taught in a later tooling
# chapter.
print("\nNext command:")
print("python lessons/06_modules_and_packages/greeting_module.py")

# Step 5: re-exports and __all__. Open facade.py: it imports
# get_greeting from greeting_module and re-exports it, and declares
# __all__ = ["get_greeting"]. A caller can depend on facade.py's small,
# named surface without knowing (or caring) which module originally
# defined the function -- exactly how example_package/__init__.py
# re-exported hello and shout_hello in Lesson 2, but here at the level of
# a single sibling module instead of a whole package.
import facade  # noqa: E402 -- kept adjacent to the facade demo below
from facade import get_greeting  # noqa: E402

print("\nfacade.get_greeting('Grace'):", get_greeting("Grace"))
print("facade.__all__:", facade.__all__)

# --- One-variable experiment -------------------------------------------
# Add a second function to greeting_module.py (e.g. `def internal_helper():
# ...`) but do NOT add it to facade.py's __all__ or re-export it. Predict:
# can code that only does `from facade import *` reach internal_helper?
# Can code that does `import greeting_module` and then
# `greeting_module.internal_helper()` still reach it? (__all__ only affects
# `import *`; it is not an access boundary -- Lesson 2 showed the same
# point with example_package's leading-underscore module.)
