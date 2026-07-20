# AI Learning Mentor

The repository includes a shared, evidence-based Learning Mentor with native
entrypoints for GitHub Copilot CLI, OpenAI Codex, and Claude Code. It guides
predictions, experiments, exercises, reviews, the required Task project, and
both capstones while preserving learner ownership.

The tutor supplements the normal [course navigation](../README.md#course-outline)
and deterministic lesson, exercise, project, and capstone checks. It does not
replace reading the course material, following prerequisites, or running tests.

## Prerequisites and setup

1. Complete the normal [course setup](SETUP.md): use Python 3.11 through 3.14,
   create a virtual environment, and install the development dependencies.
2. Initialize the pinned shared mentor after an ordinary clone:

   ```bash
   git submodule update --init --recursive
   ```

   Alternatively, clone the course with `git clone --recurse-submodules`.

   The initial mentor integration uses relative Git symlinks. Linux, macOS, and
   WSL checkouts support this layout. A native Windows checkout with
   `core.symlinks=false` materializes the discovery links as plain text and
   cannot use the optional mentor; use WSL until the planned wrapper fallback is
   validated. This limitation does not affect the course itself.
3. Install and authenticate at least one supported client:
   [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli),
   [OpenAI Codex](https://developers.openai.com/codex/cli), or
   [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview).
4. Open a terminal at the repository root. Repository-level agents and skills
   are discovered relative to the current project.
5. Confirm Python and your selected client, for example:

   ```bash
   python --version
   copilot --version
   copilot skill list
   ```

The repository pins one canonical source and exposes it through each client's
project locations:

- canonical shared agent and policy:
  [`.learning-mentor/`](../.learning-mentor/);
- shared learning skill:
  [`.agents/skills/guided-learning/SKILL.md`](../.agents/skills/guided-learning/SKILL.md);
- course-owned Python learning path:
  [`.agents/skills/python-learning-path/SKILL.md`](../.agents/skills/python-learning-path/SKILL.md);
- integration descriptor:
  [`.learning-mentor.toml`](../.learning-mentor.toml);
- native agent entrypoints:
  [Copilot](../.github/agents/learning-mentor.agent.md),
  [Claude](../.claude/agents/learning-mentor.md), and
  [Codex](../.codex/agents/learning-mentor.toml).

See GitHub's documentation for
[creating CLI custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
and [invoking custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents).

## Start a mentor client

### GitHub Copilot CLI

Start an interactive session from the repository root:

```bash
copilot
```

Then select the tutor:

```text
/agent learning-mentor
```

You can also start Copilot with the repository agent already selected:

```bash
copilot --agent=learning-mentor
```

After changing or updating a skill during an existing session, reload skill
discovery and reselect the agent:

```text
/skills reload
/agent learning-mentor
```

Agent profiles are loaded when Copilot starts. If the agent was just added or
changed and is not listed, restart the CLI. The profile intentionally omits a
`tools` field: operations use the normal Copilot CLI permission prompts rather
than preapproving unrestricted tools.

### Claude Code

Start Claude with the repository agent selected:

```bash
claude --agent learning-mentor
```

### OpenAI Codex

Codex project custom agents are subagents. Start Codex from the repository root
and ask the main thread to delegate the tutoring session:

```text
Delegate this tutoring session to the project custom agent learning-mentor.
```

The canonical agent, shared skill, Python learning path, state, and solution-lock
rules remain the same across clients.

## Start or resume course state

The tutor uses two production CLIs:

- [the course adapter](../.agents/skills/python-learning-path/scripts/course_adapter.py)
  validates the manifest and emits the state projection;
- [the state helper](../.agents/skills/guided-learning/scripts/learning_state.py)
  initializes and queries persistent learner state.

Run the complete flow from any directory inside this repository:

```bash
(
  set -euo pipefail

  ROOT="$(git rev-parse --show-toplevel)"
  cd "$ROOT"
  ADAPTER=".agents/skills/python-learning-path/scripts/course_adapter.py"
  STATE=".agents/skills/guided-learning/scripts/learning_state.py"
  COMMIT="$(git rev-parse HEAD)"

  REMOTE_NAME="$(git remote | sed -n '1p')"
  if [[ -n "$REMOTE_NAME" ]]; then
    REMOTE="$(git remote get-url "$REMOTE_NAME")"
    IDENTITY=(--remote "$REMOTE")
  else
    IDENTITY=(--local-fallback "$ROOT")
  fi

  python "$ADAPTER" validate
  python "$ADAPTER" state-projection |
    python "$STATE" init-course \
      "${IDENTITY[@]}" --commit "$COMMIT" --concepts -

  python "$STATE" status "${IDENTITY[@]}" --commit "$COMMIT"
  python "$STATE" due-reviews "${IDENTITY[@]}" --commit "$COMMIT"
  python "$STATE" next-objective "${IDENTITY[@]}" --commit "$COMMIT"
)
```

Because the block does not pass `--db`, it uses
`COPILOT_LEARNING_TUTOR_DB` when set, otherwise
`$XDG_DATA_HOME/copilot-learning-tutor/state.sqlite3`, falling back to
`~/.local/share/copilot-learning-tutor/state.sqlite3`.

The adapter's `validate` command checks the manifest contract and declared
paths, commands, selectors, prerequisites, and locks. `state-projection` emits
the validated concept graph as JSON. The helper's `init-course --concepts -`
reads that projection from standard input and creates or updates the current Git
commit transactionally.

The commands emit compact JSON on standard output and errors on standard error.
The subshell uses `set -euo pipefail`, so it stops if validation, projection,
initialization, or either side of the pipe fails. The tutor must parse JSON only
after exit status zero and must not claim initialization, status, reviews, or an
objective if either CLI fails or emits invalid JSON.

Use `status` to inspect current progress, `due-reviews` to select scheduled
retrieval practice, and `next-objective` to find the next prerequisite-valid
item. A due review takes priority over new material.

These are the supported runtime entry points. Do not substitute a test module,
test fixture, direct import of adapter internals, or hand-written projection.
You can inspect the live interfaces with:

```bash
python .agents/skills/python-learning-path/scripts/course_adapter.py --help
python .agents/skills/python-learning-path/scripts/course_adapter.py validate --help
python .agents/skills/python-learning-path/scripts/course_adapter.py state-projection --help
python .agents/skills/guided-learning/scripts/learning_state.py init-course --help
```

### After the Git commit changes

State is initialized per `git rev-parse HEAD`. After pulling, switching
branches, or otherwise changing `HEAD`, rerun the entire validation, projection,
and initialization flow before querying or recording state. Initialization is
safe to repeat for the same commit and validated projection.

Mastery and review data follow stable manifest IDs across commits. Attempts
remain historical evidence on their original commit, and solution unlocks are
commit-specific. Uncommitted learner edits are workspace evidence rather than a
new course version.

If the new manifest or projection is invalid, or initialization fails, the
tutor remains read-only and reports persistent state as unavailable. It must not
reuse a previous commit's objective as if it belonged to the current commit.

## Learning flow

### 1. Onboarding or resuming

The mentor verifies the descriptor, shared skill, and Python learning path, then
runs the production start/resume flow before selecting an objective. It explains
what state is stored and asks about your goal, prior experience, available time,
and whether you want to resume.

Self-reported confidence helps select questions but is not mastery evidence. If
a review is due, the tutor offers it before new material. Otherwise it resumes
the active objective or chooses the next objective whose prerequisites have
evidence.

### 2. One bounded concept

For each concept, the tutor:

1. states one problem and observable success criteria;
2. asks you to predict the result or propose an approach;
3. runs the smallest command declared in the
   [course manifest](../.agents/skills/python-learning-path/course.toml);
4. asks what you observed and why it happened;
5. changes one assumption or input and asks for another prediction;
6. asks you to state the general rule;
7. uses a closed-notes recall question and an analogous independent exercise;
8. runs the exact deterministic evaluator;
9. asks you to explain and reflect before recording evidence.

Repository checks and their observed exit statuses are the authority. The tutor
does not turn an unrun, unavailable, timed-out, skipped, or failing check into a
pass.

### 3. Hints and edits

Hints advance one level at a time: eliciting your hypothesis, orienting you to a
relevant source or error, contrasting expected and observed behavior, offering
structure, and only then giving a small code-shaped hint. The tutor waits for
new learner evidence before escalating.

The tutor starts read-only. Before changing learner code, it must inspect the
current file and diff, show the smallest proposed unified diff, identify its
purpose, and receive explicit confirmation. Confirmation applies only to that
diff. The tutor never discards, restores, stashes, cleans, or overwrites learner
work. It resets, commits, or pushes only when the exact Git action and scope are
explicitly requested and confirmed. It also preserves
the local `main.py` in the
[`exercises/00_playground/`](../exercises/00_playground/README.md) directory as
learner-owned scratch space.

### 4. Evaluation, mastery, and review

A focused command exiting successfully is necessary but not sufficient for
mastery. Guided success can be recorded as practiced; mastery additionally
requires an explanation and independent transfer or later recall. Reviews are
scheduled from observed evidence. A due review is a scheduling fact, not proof
that previous learning was lost.

## Example session

This abbreviated example is illustrative; the tutor uses current repository
lines and actual command output in a real session.

```text
Learner: Help me resume.

Tutor: Your next prerequisite-valid objective is temperature conversion in
Module 1. Before we run anything: what should 20 °C become under F = C × 9/5 + 32,
and why?

Learner: 68 °F, because 20 × 1.8 is 36, then add 32.

Tutor: Good prediction. The starter contract is in
exercises/01_basics/exercises.py:14-20. I ran:
python exercises/01_basics/exercises.py
Observed: exit 1 at celsius_to_fahrenheit because it raises
NotImplementedError. What is the smallest expression that follows the stated
formula?

Learner: celsius * 9 / 5 + 32.

Tutor: Proposed edit:
--- a/exercises/01_basics/exercises.py
+++ b/exercises/01_basics/exercises.py
@@ -16,5 +16,4 @@ def celsius_to_fahrenheit(celsius):
     Formula: F = C * 9/5 + 32
     """
-    # TODO: implement this function
-    raise NotImplementedError
+    return celsius * 9 / 5 + 32

Apply only this diff?

Learner: Yes.

Tutor: [applies the confirmed diff and reruns the same focused command]
The command still exits 1 at the next unfinished exercise, while the two
temperature assertions passed. That is progress, not a full module pass. Why
does division by 5 occur before adding 32?
```

The example deliberately does not reveal `solutions.py`, claim that the whole
exercise passed, or edit before confirmation.

## Learner state and privacy

The bundled
[`learning_state.py`](../.agents/skills/guided-learning/scripts/learning_state.py)
stores structured progress in SQLite outside the repository. The path is:

1. `--db PATH`, when explicitly supplied;
2. `COPILOT_LEARNING_TUTOR_DB`, when set;
3. `$XDG_DATA_HOME/copilot-learning-tutor/state.sqlite3`; or
4. `~/.local/share/copilot-learning-tutor/state.sqlite3`.

Stored data includes normalized course identity, Git commit versions, stable
concept IDs and prerequisites, attempts and scores, hint levels, mastery,
reviews, solution-unlock events, and helper command timestamps. It does not
store source code, command-output dumps, full conversations, prompts, secrets,
credentials, or free-form personal notes. Local storage is private to the
machine's account permissions, but it is not anonymous or encrypted by the
helper.

The tutor must use the helper's JSON output and exit status rather than opening
or changing SQLite directly. The adapter projection and state initialization
must also succeed before state is claimed. You can inspect the executable
interface at any time:

```bash
python .agents/skills/python-learning-path/scripts/course_adapter.py --help
python .agents/skills/guided-learning/scripts/learning_state.py --help
python .agents/skills/guided-learning/scripts/learning_state.py status --help
```

### Status export

The helper has no dedicated `export` or `import` subcommand. `status` produces a
JSON snapshot of the current course and commit, suitable for inspection or a
limited progress export:

```bash
REMOTE="$(git config --get remote.origin.url)"
COMMIT="$(git rev-parse HEAD)"
python .agents/skills/guided-learning/scripts/learning_state.py \
  status --remote "$REMOTE" --commit "$COMMIT" \
  > "$HOME/learning-python-progress.json"
```

If the repository has no remote, replace `--remote "$REMOTE"` with
`--local-fallback "$PWD"`; the helper warns that this identity will not follow a
future remote. The status JSON is not a full audit backup and there is no helper
command to import it.

### Resetting progress

The supported reset is concept-specific. Ask the tutor for the stable manifest
ID and confirm the reset, or run:

```bash
python .agents/skills/guided-learning/scripts/learning_state.py \
  record-mastery --remote "$REMOTE" --commit "$COMMIT" \
  --concept concept.basics.hello-world --reset
```

This sets that concept's mastery to `not_started` and removes its review
schedule. It does not erase attempts, hints, or solution-unlock history. Verify
the result with `status`.

There is no whole-course reset or database deletion command. To start with a
separate fresh state without destroying the existing database, point the helper
at a new path outside the repository, then start a new tutor session:

```bash
export COPILOT_LEARNING_TUTOR_DB="$HOME/.local/share/copilot-learning-tutor/state-fresh.sqlite3"
copilot --agent=learning-mentor
```

Unset the variable to return to the default database.

### Backing up state

Close active tutor sessions first, keep backups outside the repository, and use
Python's SQLite backup API so WAL state is copied consistently:

```bash
DB="${COPILOT_LEARNING_TUTOR_DB:-${XDG_DATA_HOME:-$HOME/.local/share}/copilot-learning-tutor/state.sqlite3}"
BACKUP="$HOME/learning-tutor-state-backup.sqlite3"
python - "$DB" "$BACKUP" <<'PY'
import sqlite3
import sys

with sqlite3.connect(sys.argv[1]) as source:
    with sqlite3.connect(sys.argv[2]) as destination:
        source.backup(destination)
PY
```

Protect the backup like the original because it contains course identity and
learning history. Restoring is a deliberate file-level operation, not a helper
command; do not replace an active database while a mentor client or the helper
is using it.

## Course and Git version behavior

The manifest declares course version `1.0.0`, but persistent helper versions are
identified by `git rev-parse HEAD`. Stable manifest IDs allow mastery and review
state to continue across commits. Attempts remain attached to their original
commit, while solution unlocks are commit-specific and do not carry to changed
course content. Uncommitted learner edits are workspace evidence, not part of
the commit identity.

When the repository moves to a new commit, the tutor validates the manifest and
generates a fresh production adapter projection, then initializes that commit's
concept graph before querying or recording new evidence. A renamed or
incompatible concept needs a new stable ID and reassessment. If either CLI
fails, no new-commit state is claimed.

## Solution locks

Solution locks are a teaching policy enforced by the tutor:

- module `solutions.py` files remain locked until the exact module exercise
  command passes, or until a genuine attempt is recorded and you explicitly
  request the specific post-attempt unlock;
- project and capstone solution trees unlock only for the matching milestone,
  never for future milestones;
- while locked, the tutor does not read, search, quote, summarize, diff, import,
  execute, compile, lint, or type-check the solution path;
- unlocking is an audit event, not proof of mastery, and comparison is optional.

The lock is not filesystem access control, encryption, or a security boundary.
You can still open repository files yourself. If you do, the tutor must not use
that accidental access as evidence or silently unlock other scopes.

## Project and capstone milestones

The required [Task project](../projects/tasks/README.md) follows Module 11 and
precedes Module 12. Always assess the learner tree explicitly with
`PROJECT_IMPLEMENTATION=starter`.

| Milestone | Focused check |
| --- | --- |
| Domain and contracts | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m1_domain.py -q` |
| Persistence | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m2_persistence.py -q` |
| Standard-library HTTP | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m3_stdlib.py -q` |
| Flask | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m4_flask.py -q` |
| FastAPI and parity | `PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests/test_m5_fastapi_and_parity.py -q` |

After Module 12 and the Task project, complete both required
[capstones](../capstones/README.md). Always select the starter tree explicitly
with `CAPSTONE_IMPLEMENTATION=starter`.

### Comparative configuration store

| Milestone | Focused check |
| --- | --- |
| Domain | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m1_*.py' -v` |
| CLI | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m2_*.py' -v` |
| SQLite | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m3_*.py' -v` |
| Mutations | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m4_*.py' -v` |
| Independent processes | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/comparative/tests -p 'test_m5_*.py' -v` |

Verify the frozen comparative specification checksum before conformance work as
described in the [comparative guide](../capstones/comparative/README.md).

### Idiomatic ingestion and reporting

| Milestone | Focused check |
| --- | --- |
| Domain | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m1_*.py' -v` |
| Sources and application boundary | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m2_*.py' -v` |
| SQLite | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m3_*.py' -v` |
| Reporting | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m4_*.py' -v` |
| HTTP and integration | `CAPSTONE_IMPLEMENTATION=starter python -m unittest discover -s capstones/idiomatic/tests -p 'test_m5_*.py' -v` |

For every project or capstone milestone, the tutor reads the contract, asks for
a plan, runs a narrow baseline, confirms each proposed edit, reruns the same
focused check, requests a demonstration and explanation, and only then advances.
Final completion also requires the manifest's cumulative learner-safe checks.

## Troubleshooting

### The agent is not listed

- Confirm the current directory is the repository root.
- Confirm `.github/agents/learning-mentor.agent.md` exists.
- Confirm the entrypoint is a symlink resolving into `.learning-mentor/`. On a
  native Windows checkout with `core.symlinks=false`, use WSL as described in
  the setup section.
- Restart Copilot, then run `/agent learning-mentor`.
- A user agent at `~/.copilot/agents/learning-mentor.agent.md` overrides the
  repository agent with the same filename.

### A required skill is not listed

Run `git submodule update --init --recursive`, then `copilot skill list`. In an
active Copilot session, run `/skills reload`. Confirm `guided-learning` and
`python-learning-path` are available under `.agents/skills/`. If the submodule,
either skill, or the descriptor is unavailable, the mentor should stop rather
than invent course rules.

### State is unavailable

Run both production CLIs' `--help`, confirm Python 3.11-3.14, rerun adapter
`validate`, and verify that exactly one of `--remote` or `--local-fallback` and
the current commit are supplied. Use `set -o pipefail` for the projection/init
pipe. On a nonzero exit, invalid JSON, invalid projection, corrupt state, or
SQLite conflict, the tutor must not claim initialization or a state update. It
may continue read-only while clearly labeling state as unavailable.

### A focused check cannot run

Confirm the virtual environment and dependencies from [setup](SETUP.md), run
from the repository root, and use the explicit learner selector for projects or
capstones. Missing tools, collection errors, timeouts, unexpected skips, and
harness failures are assessment errors, not passing learner attempts.

### Copilot asks for permission

That is expected. The agent does not preapprove unrestricted tools. Review each
requested command, path, or edit; reject anything broader than the current
learning step.
