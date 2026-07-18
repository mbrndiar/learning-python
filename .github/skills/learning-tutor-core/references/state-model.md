# Learner state and evidence model

## Purpose and privacy

The repository-bundled state helper stores durable learning progress in SQLite
outside the repository so generated state is not mixed with course or learner
work. Use the platform's XDG location selected by the helper; do not copy the
database into the repository.

Store only structured learning data needed to resume and review:

- normalized course identity and commit versions;
- concept IDs, titles, order, and prerequisites;
- attempt outcomes and scores, hint levels, and timestamps;
- mastery decisions and review schedules;
- commit-specific solution unlocks and command-session timestamps.

Do not store source code, command output dumps, full conversations, prompts,
secrets, credentials, tokens, private endpoints, or sensitive personal data.
The helper intentionally has no free-form note, source, transcript, or citation
field. Keep repository citations in the current tutoring response and store only
the corresponding structured result. Local storage does not make data anonymous;
tell the learner where it is. Do not invent a retention or deletion command that
the helper does not support.

## Course identity and versioning

The helper identifies a course by its normalized Git remote and identifies a
course version by the current Git commit SHA. Prefer `--remote`; use
`--local-fallback` only when the repository has no remote and surface its warning
that the state will not follow a future remote.

Initialize every newly observed commit with the adapter-produced concept set.
Attempts retain their original commit version. Mastery and review state follow a
stable concept ID across commits, while solution unlocks are intentionally
commit-specific. Therefore:

- concept IDs must come from the manifest, never titles or directory positions;
- a renamed or semantically incompatible concept needs a new ID and
  reassessment;
- old attempts and citations remain historical evidence;
- an unlock on one commit does not unlock a solution on another;
- the commit identifies the workspace's base snapshot, not uncommitted learner
  edits.

The manifest's own schema and course versions remain adapter concerns. Verify
them before exporting concepts; do not pass manifest version strings where the
helper requires a Git SHA.

## Startup and resume protocol

The active repository adapter owns manifest parsing and projection. Use its
`validate` and `state-projection` operations; for this repository their
implementation is the
[adapter-owned producer](../../learning-python-adapter/scripts/course_adapter.py).
Do not reproduce its ecosystem-specific invocation or parse its manifest in the
core skill.

Perform this sequence on every start or resume:

1. **Validate** — run the adapter's `validate` operation. Continue only when it
   exits successfully and reports a valid manifest.
2. **Identify** — obtain the repository's Git remote and current commit SHA.
   Prefer the remote as course identity. If no remote exists, deliberately pass
   the absolute repository root as `--local-fallback` and surface the helper's
   warning.
3. **Project** — run the adapter's `state-projection` operation. Require exit
   zero and compact JSON whose top level contains a `concepts` list. Use the
   producer's node count dynamically; never hard-code a repository's current
   count in core policy.
4. **Initialize** — pipe the exact projection to
   `init-course --concepts -` with the same identity and current commit. Check
   the producer and initializer statuses, parse the initializer JSON, and verify
   its concept total agrees with the projection.
5. **Inspect** — only after successful initialization, run `status`, then
   `due-reviews`, then `next-objective`. Use the due review first when one should
   take priority; otherwise use the returned objective.

Initialization is intentionally idempotent for an unchanged commit. A changed
commit must receive a fresh projection and successful `init-course` before any
current-version status, review, objective, attempt, mastery, or unlock command.
Stable concept IDs allow mastery and reviews to carry forward; attempts retain
their history, while solution unlocks remain commit-specific.

Fail closed at every boundary:

- If validation fails, do not project, initialize, or claim that course state is
  current.
- If identity or commit discovery is missing or ambiguous, do not invent a
  value. Resolve it or use the explicit local fallback.
- If projection exits nonzero, emits invalid JSON, has the wrong shape, or
  cannot be consumed completely, do not call `init-course` and do not reuse a
  cached projection as if it described the current manifest.
- If a pipeline is used, verify both producer and consumer results; consumer
  success alone cannot hide a producer failure.
- If initialization fails or its count disagrees with the projection, do not
  run current-version state commands. The transaction rolls back; preserve the
  prior database and report current state as unavailable.
- After a commit change, never substitute the previous commit's status while
  presenting it as current. Historical state may be described only as
  historical.

## Use the state helper

Use the repository's
[bundled helper](../scripts/learning_state.py); never open or mutate its SQLite
file with ad hoc SQL. Run it from the repository root. The examples use
`python3` only to launch tutor infrastructure; all course execution commands
remain the adapter's responsibility.

The database path comes from `--db` or `COPILOT_LEARNING_TUTOR_DB` when
explicitly set. Otherwise it is
`$XDG_DATA_HOME/copilot-learning-tutor/state.sqlite3`, falling back to
`~/.local/share/copilot-learning-tutor/state.sqlite3`. The default SQLite busy
timeout is 5000 ms and can be overridden with `--busy-timeout-ms` or
`COPILOT_LEARNING_TUTOR_BUSY_TIMEOUT_MS`.

Treat compact JSON on standard output and the process exit status as the API.
Warnings, including the local-fallback warning, and categorized errors are
written to standard error.

First inspect the interface:

```text
python3 .github/skills/learning-tutor-core/scripts/learning_state.py --help
python3 .github/skills/learning-tutor-core/scripts/learning_state.py <command> --help
```

Every command requires exactly one course identity option (`--remote URL` or
`--local-fallback PATH`) and `--commit SHA`; `--at` is an optional ISO 8601 test
or replay timestamp. Use these commands:

| Command | Use |
| --- | --- |
| `init-course --concepts FILE` | Create or update the current commit from adapter-produced JSON. `--concepts-json` and `--concepts -` are alternatives. |
| `status` | Read concepts, mastery, attempts, reviews, and lock state. |
| `due-reviews [--limit N]` | Select reviews due before new work. |
| `next-objective` | Select the next prerequisite-valid concept. |
| `record-attempt --concept ID --outcome RESULT [--score 0..1]` | Record an observed evaluator result. `RESULT` is `passed`, `failed`, `error`, or `skipped`. |
| `record-hint --concept ID --hint-level 0..4` | Record the one Socratic hint level just given. Solution unlock is not a hint event. |
| `record-mastery --concept ID --level LEVEL` | Set `not_started`, `in_progress`, `practiced`, or `mastered` after applying the evidence rules. |
| `record-mastery ... --review-in-days N` | Schedule an initial or explicit review interval for practiced/mastered work. |
| `record-mastery ... --review-result RESULT` | Update spaced review with `again`, `hard`, `good`, or `easy`. |
| `unlock-solution --concept ID` | Record an allowed deterministic-success or explicit post-attempt unlock. |

The adapter must transform its manifest into the helper's concept JSON shape;
do not pass TOML directly. Consume JSON fields rather than prose or SQLite
internals. Do not infer schema columns, row IDs, or unsupported flags. Report a
concise result to the learner without exposing unrelated local state.

## Evidence taxonomy

### Observed evidence

Observed evidence has a reproducible source:

- a command the tutor ran, its exit status, and concise relevant result;
- a learner answer or prediction captured in the current interaction;
- a repository diff or behavior inspected at the current commit;
- a deterministic exercise, test, build, lint, or milestone result;
- an explanation, recall response, or independent transfer demonstrated by the
  learner.

For repository-based claims, include a current repository-relative citation
such as `lessons/topic/README.md:20-34` or `src/module.ext:8-19`. For command
evidence, report the exact adapter-selected command and exit result; cite the
relevant test or contract path when available. Do not claim a citation was
observed if the file or line range was not inspected. The helper stores only the
structured attempt result, not the citation or output.

### LLM inference

Inference includes estimated confidence, suspected misconceptions, likely
causes, readiness, code-quality judgment, or predicted transfer. Label it
explicitly as inference. Inference may choose the next question or hint, but it
must not:

- turn an unrun check into a pass;
- replace a learner explanation or recall response;
- unlock a solution as if success occurred;
- promote mastery without sufficient observed evidence.

If a learner reports a result the tutor did not run, store it as
learner-reported evidence, not tutor-observed deterministic evidence.

## Attempts and mastery

Record every meaningful attempt without overwriting earlier attempts. A failed
attempt is useful learning evidence and must not reduce the history to a single
latest score.

Use the helper's supported mastery values. Apply these semantic rules regardless
of their storage spelling:

- **Not started** — no meaningful attempt.
- **In progress** — attempted, but the deterministic contract is not yet met.
- **Practiced** — the immediate deterministic check passed with some guided
  support or explanation evidence is incomplete.
- **Mastered** — the deterministic contract passed, the learner explained the
  mechanism, and an independent exercise or later recall showed transfer.
- **Review due** — previously practiced or mastered evidence is old enough for
  retrieval; this schedules work and does not erase historical mastery.

Do not promote mastery from code appearance, confidence, a reference-solution
comparison, or one inferred judgment. If no deterministic evaluator exists,
use the manifest's declared observable rubric and record the limitation; never
represent the result as an automated pass.

## Spaced review

After successful practice, ask the helper to schedule the next review according
to its deterministic interval policy. On resume:

1. run `due-reviews` before `next-objective`;
2. use short closed-notes retrieval or a small transfer task;
3. record the observed response and evaluator result;
4. use `record-mastery --review-result` to advance or shorten the interval.

An overdue review is a scheduling fact, not proof that learning was lost.
Failed recall changes the next learning action and review interval; it does not
delete prior evidence.

## Solution unlock state

Record the manifest concept ID, timestamp, reason, and whether unlock followed
deterministic success or an explicit post-attempt learner request. The adapter
maps that concept to any repository-level solution lock group.
Call `unlock-solution` only after the core policy permits it; the helper verifies
success or the manifest-derived minimum attempt count, but only the tutor can
verify that the learner explicitly requested a post-attempt unlock. An unlock is
an audit event, not mastery evidence. Never create one merely because the tutor
accidentally saw a solution.

## Failure behavior

State commands must fail closed. Parse JSON only after exit status zero. On
nonzero exit, invalid JSON, invalid course identity or commit, unknown concept,
unsupported schema version, corrupt database, or exhausted SQLite lock:

1. do not claim the requested state change occurred;
2. show a concise, non-sensitive error and the failed operation;
3. retry only a clearly transient `error[conflict]` using helper-supported busy
   timeout behavior;
4. do not delete, recreate, migrate, repair, or edit the database without the
   learner's explicit permission;
5. continue tutoring read-only if useful, clearly labeling state as unavailable
   and keeping no fictional persistent updates.

Never convert a helper failure, missing evaluator, timeout, or interrupted
command into a passing attempt. Transactional helper behavior protects the
database, but the tutor must still verify the returned status before reporting
success.

Expected failure categories and exit codes are: `usage` 2, `not-found` 3,
`conflict` 4, `state` 5, and `io` 6. Errors use
`error[category]: message` on standard error. Mutations use an immediate
transaction and roll back on failure; never infer a partial successful write.
