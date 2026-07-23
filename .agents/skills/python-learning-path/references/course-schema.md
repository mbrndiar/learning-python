# Course manifest schema 1.0

`course.toml` is parsed with Python 3.11's `tomllib`; adapters must not require a
third-party TOML package. Paths are repository-root-relative, and commands run
from the repository root.

## Stability

- `manifest_version` versions the instance; `schema_version` versions this
  contract.
- Unit and concept IDs are semantic, opaque identifiers. They must not contain
  commit hashes or depend on display order or file names.
- Existing IDs are never reassigned. Renames change titles or paths, not IDs.
- Every prerequisite names another declared trackable ID. Concept prerequisites
  apply in addition to their parent module prerequisites. The graph must be
  acyclic.

## Records

- `[course]` contains course identity, supported runtime range, entry/setup
  documents, command working directory, and required final destinations.
- `[[modules]]` contains one ordered teaching module. Each module declares its
  prerequisites, required outcomes, README, review-question source, exercise
  pair, focused validation commands, and solution-lock group. Optional
  `solution_supplements` paths hold additional reference artifacts and must
  appear after the primary exercise solution in the same lock group.
- `[[modules.concepts]]` maps one stable concept ID to a runnable lesson file
  and its documented command. Concepts may be ordered with explicit
  prerequisites rather than by relying on array position.
- `[[projects]]` and `[[capstones]]` use the same prerequisite, outcome,
  validation, and solution-lock conventions. Their implementation selector
  records the environment variable and learner/reference values used by the
  shared tests.
- `[[projects.milestones]]` and `[[capstones.milestones]]` provide stable
  milestone IDs, prerequisites, required outcomes, and focused learner test
  commands.
- `[[solution_lock_groups]]` declares repository paths hidden until its policy
  permits comparison. `solution_unlock_after` is the minimum number of recorded
  attempts before an explicit post-attempt unlock request may succeed; a
  deterministic success may unlock earlier.

## Tutor state projection

The manifest's `[course].id` and `[course].version` identify adapter content.
The state helper deliberately uses the normalized Git remote (or explicit local
fallback) as course identity and the observed commit SHA as version identity.
Adapters must not invent unsupported course-ID or course-version CLI flags.

The adapter, not the state helper, parses this TOML. It projects trackable
concepts and milestones into the helper's flat `concepts` initialization JSON,
preserving IDs, assigning deterministic order, inheriting container
prerequisites, and copying `solution_unlock_after` from the referenced lock
group. Container completion may be derived from its required children rather
than creating a second unstable identifier.

All declared path fields must exist at manifest-validation time. A future
adapter may declare a command-created path only with a record shaped like
`{ path = "...", availability = "command-created", created_by = "..." }`;
plain strings always mean `availability = "repository"`.

Unknown keys may be ignored by schema-compatible readers. Missing required
records, duplicate IDs, invalid references, cycles, nonexistent repository
paths, or unsupported selector values are errors.
