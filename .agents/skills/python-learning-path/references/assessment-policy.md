# Python assessment policy

This policy adapts the shared skill's evidence rules to the commands and stable
IDs in `../course.toml`.

## Deterministic-first decisions

1. Select the active manifest ID and its exact focused command before running
   anything.
2. Never mark an attempt `passed` unless that exact command ran to completion
   with process exit status 0. Expected nonzero behavior inside a test counts
   only when the enclosing evaluator exits 0.
3. A nonzero exit, timeout, interruption, unavailable tool, invalid selector,
   collection failure, or unrun command is never a pass.
4. One passing example proves only that observed behavior. It does not prove all
   required outcomes, explanation, transfer, or durable mastery.
5. Prefer the focused lesson, exercise, or milestone command. Run wider
   validation only after focused success and only when it does not traverse a
   locked solution path.
6. Keep observed facts separate from inference. A likely misconception can
   choose the next question, but it cannot change the command result.

Use these state outcomes:

- `passed` — the exact active evaluator exited 0;
- `failed` — the evaluator was usable and learner-owned syntax, import,
  behavior, assertion, lint, typing, or process behavior violated its contract;
- `error` — the environment, repository harness, permissions, dependency,
  platform, timeout, or state service prevented a valid assessment;
- `skipped` — the learner deliberately deferred the attempt or a prerequisite
  prevented it; an unexpected framework skip is insufficient evidence, not a
  pass.

## Stable evidence target

Map each observation to the narrowest manifest ID:

| Observation | Stable ID |
| --- | --- |
| lesson prediction, run, explanation, or focused experiment | matching `concept.*` |
| module review or module exercise command | parent `module.*` |
| one Task project milestone command | matching `milestone.tasks.*` |
| completed Task project integration gate | `project.tasks-rest-api-clients` |
| one comparative capstone milestone command | matching `milestone.comparative-kv.*` |
| comparative final gate | `capstone.comparative-kv` |
| one idiomatic capstone milestone command | matching `milestone.idiomatic-ingest-report.*` |
| idiomatic final gate | `capstone.idiomatic-ingest-report` |

Never create IDs from titles, paths, test names, or display order. Bind evidence
to the current Git commit. Uncommitted learner changes are observed workspace
state, not part of that commit.

## Diagnostic classification

First identify the primary diagnostic category, then decide whether it is a
learner `failed` attempt or an environment/repository `error`.

### Syntax

- `SyntaxError`, `IndentationError`, and `TabError` in the active learner file
  are `python-syntax` and normally `failed`.
- Report the exception type, learner file, line, and concise parser message.
  Point to the token or indentation boundary; do not rewrite the solution.
- A syntax failure in the interpreter's libraries, an installed dependency, a
  locked reference tree, or an unchanged harness is `error` and requires
  environment/repository triage.

### Imports

- `ModuleNotFoundError` or `ImportError` for a declared third-party dependency
  or tool that is not installed is `environment-import` and `error`. Cite
  `README.md:35-57` or the relevant declared requirements.
- An import of a learner package that fails because of its name, package layout,
  public API, circular dependency, or selected source root is `learner-import`
  and `failed`.
- Verify the repository root, supported interpreter, active environment, and
  explicit `PROJECT_IMPLEMENTATION=starter` or
  `CAPSTONE_IMPLEMENTATION=starter` selector before blaming learner code.
- Never add the solution root to `PYTHONPATH` to make learner evaluation pass.

### Python runtime

- Classify the final exception and first relevant learner-owned traceback frame.
  Typical examples include `NameError`, `TypeError`, `ValueError`, `KeyError`,
  `IndexError`, `AttributeError`, `OSError`, and domain exceptions.
- If valid inputs reach learner code and its behavior violates the active
  contract, record `python-runtime` and `failed`.
- Missing files created by setup, denied permissions, unsupported platform
  behavior, external service failures, exhausted resources, or harness defects
  are `environment-runtime` and `error`.
- Some lessons intentionally demonstrate exceptions. Check the active lesson
  source and README before treating the exception as a failure.

### Assertions and direct exercise scripts

- A bare `AssertionError` or exercise assertion in learner code is
  `assertion-failure` and `failed`; capture the assertion location and a bounded
  expected/actual summary when available.
- Do not infer the expected implementation from `solutions.py`.
- An assertion from the unchanged harness can still describe a learner behavior
  failure. It is an environment error only when the harness itself cannot
  establish or evaluate its documented precondition.
- A direct exercise script passes only when its exact manifest command exits 0.

### unittest

- `OK` is a pass only with exit status 0 for the exact command.
- `FAILED (failures=N)` is `unittest-failure` and learner `failed`; summarize
  failing test names and the first useful assertion difference.
- `FAILED (errors=N)` requires classification of each leading error as syntax,
  import, runtime, setup, teardown, timeout, or process failure. Use `failed`
  when learner-owned and `error` when assessment infrastructure is responsible.
- An unexpected skip, zero discovered tests, interruption, or killed process is
  insufficient evidence and never mastery.

### pytest

- Exit 0 is a pass for the exact selected command.
- Test failures (normally exit 1) are `pytest-failure` and `failed`; report the
  focused node/test name, concise assertion diff, and first learner frame.
- Interrupted collection (exit 2), internal error (exit 3), usage error
  (exit 4), or no tests collected (exit 5) is not a pass. Classify the root cause
  as learner failure only when learner syntax/import/collection code caused it;
  otherwise record `error`.
- Expected skips declared by the harness do not prove skipped behavior. An
  unexpected skip or deselection makes the affected outcome unobserved.

### Ruff

- For `ruff format --check`, a nonzero result reporting files that would be
  reformatted is `ruff-format` and learner `failed`.
- For `ruff check`, group only the relevant diagnostic codes and locations
  (`E4`, `E7`, `E9`, `F`, `I`, or `UP` under this repository's configuration).
  A learner-file diagnostic is `ruff-lint` and `failed`.
- Missing Ruff, unreadable files, or invalid unchanged configuration is
  `environment-tool` and `error`.
- Do not run Ruff over a locked solution root.

### mypy

- Exit 0 with mypy's successful result is a pass for the exact target.
- Type errors in the learner target are `mypy-type` and `failed`; summarize the
  error code, location, and contract mismatch without dumping all output.
- Missing imports must be split between an absent declared dependency
  (`environment-import`, `error`) and an incorrect learner package/API
  (`learner-import` or `mypy-type`, `failed`).
- Invalid unchanged configuration, unsupported mypy, or unreadable target is
  `environment-tool` and `error`.
- Do not type-check a locked solution root.

### Process exits, signals, and timeouts

- Record both the enclosing evaluator exit and, when exposed by a test, the
  learner child process's exit category.
- A learner CLI may intentionally return a documented nonzero code. It passes
  only when the enclosing focused test verifies that exact code and exits 0.
- An unexpected nonzero code, signal termination, stderr protocol violation,
  malformed output, leaked child, or learner-caused timeout is `process-exit`
  and `failed`.
- Tool absence, platform-command absence, evaluator timeout, resource
  exhaustion, or harness cleanup failure is `environment-process` and `error`
  unless the focused evidence attributes it to learner ownership.
- Never run learner-provided shell strings. Preserve the repository's
  argument-list subprocess boundaries.

## Environment versus misconception

Use this order:

1. Verify the exact repository root, Python 3.11-3.14, declared dependency
   installation, tool availability, required local fixtures, and explicit
   learner selector.
2. Reproduce with the smallest manifest command.
3. Locate the first failing boundary:
   interpreter/tool setup, test collection/harness, learner import, learner
   execution, assertion/contract, or child process.
4. Attribute `failed` only when evidence reaches learner-owned code or behavior
   under a valid evaluator. Otherwise use `error`.
5. State a suspected misconception only as inference and ask one discriminating
   question or propose one small check.

Do not repair environments by reading a locked solution, changing selectors to
`solution`, weakening tests, suppressing diagnostics, or broadening imports.

## Bounded, safe diagnostic summaries

Report:

- active stable ID and exact command;
- selector and exit status;
- observed category and `passed`/`failed`/`error`/`skipped` decision;
- at most the focused failing test names or first relevant learner locations;
- a concise assertion difference or final exception;
- whether the cause is observed learner evidence, observed environment failure,
  or labeled inference;
- the next single hint or check.

Do not persist or repeat full output dumps, source files, conversations,
environment listings, headers, credentials, tokens, private endpoints, database
contents, or unrelated local state. Redact secret-looking values and
credential-bearing URLs. Store only the structured outcome and concise
repository citation supported by the state helper.

## Mastery decision

A passing command is necessary but not sufficient for mastery:

- keep helper mastery `in_progress` after a failed/error attempt;
- mark `practiced` after the exact deterministic check passes when support was
  guided or explanation/transfer evidence is incomplete;
- mark `mastered` only after the exact deterministic contract passes, the learner
  explains the mechanism, and an independent analogous exercise or later recall
  demonstrates transfer;
- use later recall to schedule or update review; do not erase older evidence.

The helper's canonical levels are `not_started`, `in_progress`, `practiced`, and
`mastered`. Use canonical names rather than the compatibility aliases `unseen`
and `learning`.

## Runtime adapter and state helper contract

Use only the production CLIs. Never import
`.agents/skills/python-learning-path/tests/test_course_manifest.py` or any
other test module to validate or project runtime state.

Inspect the live interfaces and run validation from the repository root:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py --help
python .agents/skills/python-learning-path/scripts/course_adapter.py validate --help
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection --help
python .agents/skills/guided-learning/scripts/learning_state.py --help
python .agents/skills/guided-learning/scripts/learning_state.py <command> --help
python .agents/skills/python-learning-path/scripts/course_adapter.py validate
```

The adapter defaults to this repository's manifest and root. Its only source
overrides are `--manifest PATH` and `--repository-root PATH`. Exit 0 returns
compact JSON, exit 2 is CLI usage, exit 3 is invalid TOML/manifest, and exit 4 is
I/O failure. Parse stdout only after exit 0 and require validation JSON with
`status: "valid"`.

After validation, initialize a remote-backed course with the portable
stdout-to-stdin pipeline:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection |
  python .agents/skills/guided-learning/scripts/learning_state.py init-course \
    --remote "$(git remote get-url origin)" \
    --commit "$(git rev-parse HEAD)" \
    --concepts -
```

When no Git remote exists, use:

```text
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection |
  python .agents/skills/guided-learning/scripts/learning_state.py init-course \
    --local-fallback "$(git rev-parse --show-toplevel)" \
    --commit "$(git rev-parse HEAD)" \
    --concepts -
```

Do not pass TOML directly to the state helper. `state-projection` is the sole
runtime owner of stable assessment nodes, prerequisite flattening, deterministic
order, and lock thresholds. It emits all manifest concept, module, project,
milestone, and capstone assessment IDs; it does not emit lock-group IDs. Never
reimplement this projection in tutor code, import a test fixture to obtain it,
or auto-pass parent nodes.

The chosen remote or local path is the course identity and the current Git SHA
is the course version. On first use and every changed commit:

1. run `validate` and require exit 0 plus valid success JSON;
2. rerun `state-projection | ... init-course --concepts -` with the current SHA;
3. require state-helper exit 0 and valid JSON before claiming initialization.

Same-commit initialization is idempotent. Stable-ID mastery and reviews carry
across commits; attempts retain their original commit and unlocks remain
commit-specific.

Resume with the same identity and current SHA. Read `status`, then
`due-reviews`, then `next-objective` when no review is due:

```text
python .agents/skills/guided-learning/scripts/learning_state.py status --remote "$(git remote get-url origin)" --commit "$(git rev-parse HEAD)"
python .agents/skills/guided-learning/scripts/learning_state.py due-reviews --remote "$(git remote get-url origin)" --commit "$(git rev-parse HEAD)"
python .agents/skills/guided-learning/scripts/learning_state.py next-objective --remote "$(git remote get-url origin)" --commit "$(git rev-parse HEAD)"
```

For local identity, replace the exact remote pair with
`--local-fallback "$(git rev-parse --show-toplevel)"`.

Use the remaining executable command contract:

- `record-attempt ... --concept <stable-id> --outcome
  passed|failed|error|skipped` records the deterministic decision;
- `record-hint ... --concept <stable-id> --hint-level 0|1|2|3|4` records the one
  shared hint level just given;
- `record-mastery ... --concept <stable-id> --level
  not_started|in_progress|practiced|mastered` updates mastery; use
  `--review-in-days` or `--review-result again|hard|good|easy` only with
  `practiced` or `mastered`;
- `unlock-solution ... --concept <stable-id>` records an eligible unlock.

Shared hint levels 0 through 4 map directly to the same helper value. Level 5
is an `unlock-solution` event and must never be passed to `record-hint`.

Fail closed at every process boundary:

- do not start projection after failed or invalid `validate` output;
- never merge adapter stderr into the projection pipeline;
- empty or invalid projection JSON must make initialization fail;
- parse state-helper stdout only after exit 0;
- on any nonzero exit, invalid JSON, identity/commit mismatch, unsupported
  schema, conflict, or I/O error, claim no initialization, resume, or mutation;
- show only the operation and concise non-sensitive category, do not inspect or
  repair SQLite directly, and continue read-only tutoring when useful.

## Locks, hints, and edits

Manifest solution locks override diagnostic convenience. While locked, do not
read, search, diff, execute, import, compile, lint, or type-check solution paths.
After exact unit or matching-milestone validation, `unlock-solution` records
`deterministic_success`; unlock only that matching scope. Without a pass, call
`unlock-solution` only after at least the configured number of meaningful
`passed`, `failed`, or `error` attempts and an explicit learner request with
confirmed scope; the helper records `post_attempt_request`. `skipped` does not
satisfy the threshold. Repeated calls are idempotent as `already_unlocked`. A
helper conflict means the solution remains locked.

Use one Socratic hint level, wait for new learner evidence, and confirm the exact
file and edit before changing learner work. Never commit or push unless asked.
