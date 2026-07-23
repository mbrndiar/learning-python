# 🤖 AI Learning Mentor

The repository includes a shared, evidence-based Learning Mentor with native
entrypoints for GitHub Copilot CLI, OpenAI Codex, and Claude Code. It guides
predictions, experiments, exercises, reviews, the required Task project, and
both capstones while preserving learner ownership.

The tutor supplements the normal [course navigation](../README.md#course-outline)
and deterministic lesson, exercise, project, and capstone checks. It does not
replace reading the course material, following prerequisites, or running tests.

## ✅ Prerequisites and setup

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

## 🚀 Start a mentor client

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

## 🤝 Who runs what

Normal tutoring does not require you to invoke the course adapter, state helper,
lesson scripts, or evaluators manually.

| You | The mentor |
| --- | --- |
| initialize the submodule and install a supported client | validate the descriptor, course manifest, and pinned integration |
| start the client and select `learning-mentor` | initialize and query persistent course state |
| read the suggested material and answer predictions or explanations | choose due reviews and prerequisite-valid objectives |
| make hands-on changes in learner-owned files | inspect your diff and run the focused lesson or evaluator command |
| approve narrowly scoped tool operations | classify observed results and record learning evidence |
| explicitly request any exceptional edit, reset, commit, or push | remain read-only unless that exact operation is requested and confirmed |

The internal commands remain documented in the agent and skill contracts for
maintainers and automated tests. They are not learner setup steps.

## 💾 Start or resume course state

After you select `learning-mentor`, the mentor automatically:

1. verifies the submodule, discovery links, descriptor, and Python learning path;
2. validates the course manifest and its stable prerequisite graph;
3. initializes state for the configured Git remote and current commit;
4. reads progress, due reviews, and the next prerequisite-valid objective;
5. prefers the first due review over new material; and
6. explains the effective state location and privacy boundary.

If any startup boundary fails, the mentor reports the failing operation and
continues read-only when useful. It must not invent state or reuse an objective
from another commit. You only need to review the client's normal permission
request for each narrowly scoped operation.

### After the Git commit changes

State is initialized per Git commit. After pulling, switching branches, or
otherwise changing `HEAD`, the mentor reruns validation and initialization
before querying or recording state. You do not need to invoke the internal state
commands.

Mastery and review data follow stable manifest IDs across commits. Attempts
remain historical evidence on their original commit, and solution unlocks are
commit-specific. Uncommitted learner edits are workspace evidence rather than a
new course version.

If the new manifest or projection is invalid, or initialization fails, the
tutor remains read-only and reports persistent state as unavailable. It must not
reuse a previous commit's objective as if it belonged to the current commit.

## 🧭 Learning flow

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

Hands-on changes belong to you. The mentor gives a bounded outcome and exact
check, then asks you to edit the learner-owned file. Afterward it inspects your
diff and runs the focused command. Only when you explicitly request help may it
propose a minimal diff; applying that diff still requires your confirmation.

The mentor never discards, restores, stashes, cleans, or overwrites learner
work. It resets, commits, or pushes only when the exact Git action and scope are
explicitly requested and confirmed. It also preserves the local `main.py` in the
[`exercises/00_playground/`](../exercises/00_playground/README.md) directory as
learner-owned scratch space.

### 4. Evaluation, mastery, and review

A focused command exiting successfully is necessary but not sufficient for
mastery. Guided success can be recorded as practiced; mastery additionally
requires an explanation and independent transfer or later recall. Reviews are
scheduled from observed evidence. A due review is a scheduling fact, not proof
that previous learning was lost.

## 💬 Example session

This abbreviated example is illustrative; the tutor uses current repository
lines and actual command output in a real session.

```text
Learner: Help me resume.

Tutor: Your next prerequisite-valid objective is temperature conversion in
Module 2. Before we run anything: what should 20 °C become under F = C × 9/5 + 32,
and why?

Learner: 68 °F, because 20 × 1.8 is 36, then add 32.

Tutor: Good prediction. The starter contract is in
exercises/02_text_and_numbers/exercises.py:17-33. I ran:
python exercises/02_text_and_numbers/exercises.py
Observed: exit 1 at Task 1 (Celsius to Fahrenheit) because it raises
AssertionError with the focused message `Task 1: convert morning_celsius`.
What is the smallest expression that follows the stated formula?

Learner: celsius * 9 / 5 + 32.

Tutor: Implement only morning_fahrenheit and afternoon_fahrenheit in the
starter file according to the documented formula. Tell me when the change is
ready; I will inspect the diff and rerun the same focused command.

Learner: Done.

Tutor: [inspects the learner's diff and reruns the focused command]
The command still exits 1 at the next unfinished exercise, while the two
temperature assertions passed. That is progress, not a full module pass. Why
does division by 5 occur before adding 32?
```


The example deliberately does not reveal `solutions.py`, claim that the whole
exercise passed, or edit learner-owned code.

## 🔒 Learner state and privacy

The mentor stores structured progress in SQLite outside the repository. The
path is:

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

The mentor uses the state helper's structured interface rather than opening or
changing SQLite directly. Adapter validation and state initialization must
succeed before it claims progress, reviews, or an objective.

### Status export

Ask the mentor to show current progress or export a status snapshot. The helper
has no matching import operation, so that snapshot is for inspection rather
than a full audit backup.

### Resetting progress

Ask the mentor to reset a specific stable concept ID and confirm the exact
scope. A concept reset returns mastery to `not_started` and removes its review
schedule, but retains attempts, hints, and solution-unlock history. There is no
whole-course reset operation.

### Backing up state

Backup and restore are advanced maintenance rather than normal tutoring steps.
Ask the mentor for the effective database path and a safe backup procedure.
Close active mentor sessions first and protect the backup like the original
because it contains course identity and learning history. The state helper has
no backup or restore command.

## 🔀 Course and Git version behavior

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

## 🔐 Solution locks

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

## 🏁 Project and capstone milestones

The required [Task project](../projects/tasks/README.md) follows Module 16 and
precedes Module 17. The mentor always assesses the learner tree explicitly with
`PROJECT_IMPLEMENTATION=starter`.

The milestones are domain and contracts, persistence, standard-library HTTP,
Flask, and FastAPI with parity. The mentor selects and runs each exact focused
check from the Python learning path; you do not need to invoke the project test
harness manually.

After Module 17 and the Task project, complete both required
[capstones](../capstones/README.md). The mentor always selects the starter tree
explicitly with `CAPSTONE_IMPLEMENTATION=starter`.

### Comparative configuration store

The milestones are domain, CLI, SQLite, mutations, and independent processes.
The mentor selects the exact starter-scoped evaluator for each milestone.

The mentor verifies the frozen comparative specification checksum before
conformance work as described in the
[comparative guide](../capstones/comparative/README.md).

### Idiomatic ingestion and reporting

The milestones are domain, sources and application boundary, SQLite, reporting,
and HTTP with integration. The mentor again selects the exact starter-scoped
evaluator.

For every project or capstone milestone, the tutor reads the contract, asks for
a plan, runs a narrow baseline, confirms each proposed edit, reruns the same
focused check, requests a demonstration and explanation, and only then advances.
Final completion also requires the manifest's cumulative learner-safe checks.

## 🩺 Troubleshooting

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

Confirm Python 3.11-3.14, the initialized submodule, and the normal course
setup, then ask the mentor to retry startup and report the failing boundary. You
should not need to invoke the adapter or state helper directly. On a startup
failure, the mentor must not claim initialization or a state update; it may
continue read-only while clearly labeling state as unavailable.

### A focused check cannot run

Confirm the virtual environment and dependencies from [setup](SETUP.md), run
from the repository root, and use the explicit learner selector for projects or
capstones. Missing tools, collection errors, timeouts, unexpected skips, and
harness failures are assessment errors, not passing learner attempts.

### Copilot asks for permission

That is expected. The agent does not preapprove unrestricted tools. Review each
requested command, path, or edit; reject anything broader than the current
learning step.
