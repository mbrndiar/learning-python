---
name: python-learning-path
description: Repository-specific Python learning path for the learning-python course. Use when a learner wants to start or resume the 19-module course, run or debug a lesson or exercise, assess Python, unittest, pytest, Ruff, mypy, or process failures, or complete the Task project or either required capstone milestone by milestone.
---

# Python learning path

Use this learning path with
[guided-learning](../guided-learning/SKILL.md). The shared skill owns the
learning cycle; this skill owns this repository's paths, commands, selectors,
diagnostics, and milestone routing.

Read these sources before tutoring:

- [course.toml](course.toml) — authoritative IDs, prerequisites, paths,
  commands, selectors, outcomes, and solution locks;
- [course manifest schema](references/course-schema.md) — interpretation of the
  manifest;
- [assessment policy](references/assessment-policy.md) — deterministic result
  and diagnostic rules;
- [Socratic policy](../guided-learning/references/socratic-policy.md);
- [state model](../guided-learning/references/state-model.md).

Stop rather than guessing if the manifest cannot be parsed with Python 3.11+
`tomllib`, its schema is unsupported, a required path is absent, or an ID,
prerequisite, command, selector, or lock reference is invalid. Run all course
commands from the repository root, as required by the manifest schema.

## Repository contract

- Support Python 3.11 through 3.14. For setup or missing tools, use
  `docs/SETUP.md` and the installation documented at `README.md:35-57`.
- Follow the repository's predict-run-explain-exercise sequence at
  `README.md:59-76` and its smallest-check-first feedback loop at
  `README.md:78-127`.
- Cite repository claims with verified current `path:start-end` ranges. For a
  concept, cite its manifest-declared lesson file and parent lesson README. For
  an exercise, cite the exercise starter and its README. For applied work, cite
  the guide, specification, learner source, and focused test that establish the
  contract.
- Treat `exercises/00_playground/main.py` only as learner-owned scratch space.
  It is not a trackable course unit. Never reset, replace, or clean it.
- Before any edit, name the file and exact intended change and obtain explicit
  learner confirmation. One confirmation covers only that edit.
- Do not commit or push unless the learner explicitly asks.

## Navigate the 19 modules

Use module and concept IDs from the manifest, never titles or directory order as
state keys. Respect prerequisites; the Task project is required after Chapter 18
and before Chapter 19.

| Order | Stable module ID | Read | Focused exercise evaluator |
| --- | --- | --- | --- |
| 1 | `module.python-fundamentals` | `lessons/01_python_fundamentals/README.md` | `python exercises/01_python_fundamentals/exercises.py` |
| 2 | `module.text-and-numbers` | `lessons/02_text_and_numbers/README.md` | `python exercises/02_text_and_numbers/exercises.py` |
| 3 | `module.collections` | `lessons/03_collections/README.md` | `python exercises/03_collections/exercises.py` |
| 4 | `module.flow-and-iteration` | `lessons/04_control_flow/README.md` | `python exercises/04_control_flow/exercises.py` |
| 5 | `module.function-contracts-and-scope` | `lessons/05_functions/README.md` | `python exercises/05_functions/exercises.py` |
| 6 | `module.modules-and-packages` | `lessons/06_modules_and_packages/README.md` | `python exercises/06_modules_and_packages/exercises.py` |
| 7 | `module.exceptions-files-and-paths` | `lessons/07_exceptions_files_and_paths/README.md` | `python exercises/07_exceptions_files_and_paths/exercises.py` |
| 8 | `module.structured-data-and-time` | `lessons/08_structured_data_and_time/README.md` | `python exercises/08_structured_data_and_time/exercises.py` |
| 9 | `module.objects-and-data-models` | `lessons/09_object_oriented_programming/README.md` | `python exercises/09_object_oriented_programming/exercises.py` |
| 10 | `module.iteration-decorators-and-contexts` | `lessons/10_iteration_decorators_and_contexts/README.md` | `python exercises/10_iteration_decorators_and_contexts/exercises.py` |
| 11 | `module.typing-protocols-and-di` | `lessons/11_typing_protocols_and_di/README.md` | `python exercises/11_typing_protocols_and_di/exercises.py` |
| 12 | `module.automated-testing` | `lessons/12_testing/README.md` | `python exercises/12_testing/exercises.py` |
| 13 | `module.debugging-and-cli` | `lessons/13_debugging_and_cli/README.md` | `python exercises/13_debugging_and_cli/exercises.py` |
| 14 | `module.environments-processes-and-packaging` | `lessons/14_environments_processes_and_packaging/README.md` | `python exercises/14_environments_processes_and_packaging/exercises.py` |
| 15 | `module.sql-and-sqlite` | `lessons/15_sql_and_sqlite/README.md` | `python exercises/15_sql_and_sqlite/exercises.py` |
| 16 | `module.http-fundamentals-and-stdlib` | `lessons/16_http_fundamentals_and_stdlib/README.md` | `python exercises/16_http_fundamentals_and_stdlib/exercises.py` |
| 17 | `module.web-apis-with-flask-and-fastapi` | `lessons/17_web_apis_with_flask_and_fastapi/README.md` | `python exercises/17_web_apis_with_flask_and_fastapi/exercises.py` |
| 18 | `module.http-clients-and-transports` | `lessons/18_http_clients_and_transports/README.md` | `python exercises/18_http_clients_and_transports/exercises.py` |
| 19 | `module.concurrency` | `lessons/12_concurrency/README.md` | `python exercises/12_concurrency/exercises.py` |

For one concept:

1. read the parent module's `lesson_readme` and the concept's `lesson_file`;
2. for a new concept, give the shared policy's short teaching explanation of its
   purpose, syntax, and mechanism, then name the bounded reading passage;
3. ask for an output or behavior prediction and respond with explanatory
   feedback rather than only a verdict;
4. run exactly the concept's manifest `run_command`;
5. distinguish an intentionally demonstrated exception from an unexpected
   failure by checking the cited lesson source and README;
6. ask for the learner's observation and explanation;
7. with confirmation, vary one value or assumption and rerun the same focused
   command;
8. use the manifest review-question source, then the module exercise starter;
9. run the module's exact `validation_commands` entry.

Do not widen to repository-wide Ruff, mypy, or test commands merely because a
focused lesson or exercise failed.

## Diagnose Python and tool output

Apply [assessment-policy.md](references/assessment-policy.md) before choosing a
hint or changing state.

1. Capture the exact command, process exit status, active stable ID, selector,
   first relevant learner-owned location, and a bounded final error summary.
2. Classify the primary failure as syntax, import, Python runtime, assertion,
   unittest, pytest, Ruff, mypy, or process exit.
3. Separately assign responsibility:
   - **learner evidence** when the failure is in the active learner file or its
     behavior and the evaluator environment is usable;
   - **environment/repository error** when the interpreter, dependency, tool,
     working directory, permissions, platform command, harness, or state service
     prevents a valid assessment.
4. Give one hint level only, then wait for a learner response or new evidence.
   Point first to the smallest relevant traceback frame, assertion diff,
   diagnostic code, or contract citation.
5. Never turn an unavailable command, collection error, timeout, unexpected
   skip, nonzero evaluator exit, or inferred code quality into a pass.

## Task project

The required project sits between Chapters 18 and 19
(`projects/tasks/README.md:13-35`). Read its guide and specification paths before
tests. Work one vertical milestone at a time as described at
`projects/tasks/README.md:69-86`.

Always select learner code explicitly with `PROJECT_IMPLEMENTATION=starter`;
the manifest default is `solution` and must never be relied on during learner
assessment.

| Milestone | Focused learner command |
| --- | --- |
| `milestone.tasks.domain-and-contracts` | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m1_domain.py -q` |
| `milestone.tasks.persistence` | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m2_persistence.py -q` |
| `milestone.tasks.stdlib-http` | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m3_stdlib.py -q` |
| `milestone.tasks.flask` | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m4_flask.py -q` |
| `milestone.tasks.fastapi-and-parity` | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m5_fastapi_and_parity.py -q` |

For each milestone, read its manifest outcome and matching specification/test,
ask for a plan, run the focused command as a baseline, confirm before edits, run
the same command after each bounded slice, and require a demonstration and
explanation before advancing. After all five milestones, run the manifest's
learner-selected full pytest command and other learner-safe validation commands.
Defer any validation command that traverses `projects/tasks/solution` while its
lock is active.

## Required capstones

Start both only after all modules and the Task project. The capstone placement
and source-root rules are documented at `README.md:147-159`,
`capstones/comparative/README.md:9-21`, and
`capstones/idiomatic/README.md:9-23`.

Always select learner code explicitly with `CAPSTONE_IMPLEMENTATION=starter`;
the manifest default is `solution`.

### Comparative configuration store

Read `capstones/comparative/README.md` and all manifest
`specification_paths`. Verify the frozen specification checksum before
conformance work.

| Milestone | Focused learner command |
| --- | --- |
| `milestone.comparative-kv.domain` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m1_*.py' -v` |
| `milestone.comparative-kv.cli` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m2_*.py' -v` |
| `milestone.comparative-kv.sqlite` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m3_*.py' -v` |
| `milestone.comparative-kv.mutations` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m4_*.py' -v` |
| `milestone.comparative-kv.processes` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m5_*.py' -v` |

Milestone 5 owns independent-process races, timeouts, and cleanup; diagnose its
child-process failure separately from the enclosing unittest result
(`capstones/comparative/README.md:87-90`).

### Idiomatic ingestion and reporting

Read `capstones/idiomatic/README.md` and `capstones/idiomatic/SPEC.md`.

| Milestone | Focused learner command |
| --- | --- |
| `milestone.idiomatic-ingest-report.domain` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m1_*.py' -v` |
| `milestone.idiomatic-ingest-report.sources-and-application` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m2_*.py' -v` |
| `milestone.idiomatic-ingest-report.sqlite` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m3_*.py' -v` |
| `milestone.idiomatic-ingest-report.reporting` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m4_*.py' -v` |
| `milestone.idiomatic-ingest-report.http-and-integration` | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m5_*.py' -v` |

The HTTP milestone uses injected loopback transport and must not require public
network access (`capstones/idiomatic/README.md:51-65`).

For either capstone, use the same milestone loop as the Task project. After all
five milestones, run the capstone's exact manifest learner harness and
learner-safe quality commands. Defer commands that traverse its `solution_root`
while locked.

## Solution locks and learner ownership

Resolve every starter or solution path through the manifest's
`solution_lock_group`.

- While locked, do not read, quote, summarize, diff, search, import, compile,
  lint, type-check, or otherwise inspect any declared solution path.
- A module solution becomes eligible only after its exact unit validation
  passes. A project or capstone solution becomes eligible only for the matching
  milestone after that exact milestone command passes.
- A genuine-attempt learner request may use the tutor-core post-attempt unlock
  path. Confirm the requested scope first, then call `unlock-solution`. The
  helper requires the manifest-derived attempt threshold; use
  `solution_unlock_after=1` unless the manifest explicitly requires more. If the
  helper returns a conflict, the solution remains locked.
- Passing makes only the matching scope eligible; never inspect future
  milestones. Do not open a solution automatically. Compare only when requested,
  and compare behavior and trade-offs rather than requiring identical code.
- An unlock is not evidence of mastery.

## Runtime adapter and learner state

Use the production manifest CLI at
`.agents/skills/python-learning-path/scripts/course_adapter.py`. Do not import
the adapter test module or call test helpers at runtime. Run these commands from
the repository root and inspect their executable interface before use:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py --help
python .agents/skills/python-learning-path/scripts/course_adapter.py validate --help
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection --help
python .agents/skills/guided-learning/scripts/learning_state.py --help
python .agents/skills/guided-learning/scripts/learning_state.py <command> --help
```

The default manifest and repository root are already derived from the production
script location. Validate them before starting or resuming:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py validate
```

Successful stdout is compact JSON with `status: "valid"`. Adapter exit 0 means
success, 2 means invalid CLI usage, 3 means invalid TOML/manifest, and 4 means an
I/O failure. Parse stdout only after exit 0. The optional source overrides are
exactly `--manifest PATH` and `--repository-root PATH`, for example:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py validate --manifest .agents/skills/python-learning-path/course.toml --repository-root .
```

### First initialization

Prefer the normalized Git remote identity. After `validate` succeeds, use the
adapter's stdout-to-stdin projection pipeline; `--concepts -` is the state
helper's documented stdin contract:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection |
  python .agents/skills/guided-learning/scripts/learning_state.py init-course \
    --remote "$(git remote get-url origin)" \
    --commit "$(git rev-parse HEAD)" \
    --concepts -
```

If the repository has no Git remote, use the explicit local fallback and surface
the helper warning:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection |
  python .agents/skills/guided-learning/scripts/learning_state.py init-course \
    --local-fallback "$(git rev-parse --show-toplevel)" \
    --commit "$(git rev-parse HEAD)" \
    --concepts -
```

This pipeline is portable because the adapter emits the helper's JSON shape on
standard output and the helper reads it from standard input; it needs no
temporary projection file or Python module import. Never pass `course.toml`
directly to `init-course`.

The production projection owns stable-ID flattening, prerequisite order, and
manifest-derived `solution_unlock_after`. Do not duplicate that transformation
in tutor code. Map observations to the narrowest projected concept, module,
milestone, project, or capstone ID, and use the manifest owner-to-lock-group
mapping only when deciding which solution path scope may be inspected.

### Changed commit and resume

The remote or local path identifies the course; `git rev-parse HEAD` identifies
its version. On every newly observed commit, rerun `validate` and the appropriate
initialization pipeline with the new SHA before reading or writing state. The
same-commit initialization is idempotent. Stable-ID mastery and reviews carry
across commits, attempts retain their original commit, and solution unlocks are
commit-specific.

For a remote-backed resume, use the same current identity and SHA:

```text
python .agents/skills/guided-learning/scripts/learning_state.py status \
  --remote "$(git remote get-url origin)" \
  --commit "$(git rev-parse HEAD)"
python .agents/skills/guided-learning/scripts/learning_state.py due-reviews \
  --remote "$(git remote get-url origin)" \
  --commit "$(git rev-parse HEAD)"
python .agents/skills/guided-learning/scripts/learning_state.py next-objective \
  --remote "$(git remote get-url origin)" \
  --commit "$(git rev-parse HEAD)"
```

For a repository without a remote, replace the exact `--remote ...` pair in
each command with
`--local-fallback "$(git rev-parse --show-toplevel)"`. Read `status`, prefer any
`due-reviews` result, then use `next-objective` when no review is due.

Use `record-attempt`, `record-hint`, `record-mastery`, and `unlock-solution`
exactly as documented by their `--help`. Never query or edit the SQLite database
directly.

### Runtime failure behavior

Treat process status and compact JSON stdout as the runtime API:

- if `validate` is nonzero or its exit-0 stdout is not valid JSON with
  `status: "valid"`, stop before projection;
- `state-projection` writes JSON only on success; never merge stderr into the
  pipeline;
- if projection is empty/invalid or either side fails, `init-course` must not be
  reported successful;
- parse state-helper stdout only after exit 0; nonzero or invalid JSON means no
  initialization, resume, or mutation occurred;
- report only the operation and concise non-sensitive error, then continue
  read-only tutoring when useful. Do not invent flags, repair state manually, or
  fall back to importing test modules.

Follow the detailed mapping and failure rules in
[assessment-policy.md](references/assessment-policy.md).
