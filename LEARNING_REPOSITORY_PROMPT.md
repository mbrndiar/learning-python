# Prompt: Build a Hands-On Learning Repository

Use this prompt with a coding agent to create a repository like this one for a
different programming language, framework, tool, or platform. Replace every
value in angle brackets before starting.

## Inputs

- **Subject:** `<language, framework, tool, or platform>`
- **Learner level:** `<beginner, intermediate, or other>`
- **Prerequisites:** `<what the learner must already know, or "none">`
- **Supported versions:** `<minimum and/or tested versions>`
- **Primary environment:** `<operating systems, runtime, SDK, hardware, or cloud>`
- **Package/build tools:** `<tools expected in the subject's ecosystem>`
- **Quality tools:** `<formatter, linter, type checker, test runner, coverage tool>`
- **Course scope:** `<included topics and explicit boundaries>`
- **Capstone theme:** `<a practical application that joins the course concepts>`

## Agent assignment

Create and fill a self-contained, hands-on learning repository for **Subject**.
It must take a learner from the stated prerequisites to independent,
practical use of the core subject. Do not merely copy the topic list or file
names from another course: adapt the curriculum, terminology, tooling,
examples, and project architecture to the subject and its ecosystem.

Prefer official documentation and current ecosystem conventions. Confirm
version-sensitive facts against authoritative sources. Keep runtime
dependencies minimal, but use established development tools where they improve
feedback. Never include credentials, paid-service requirements, or resources
that a learner cannot reproduce locally unless the scope explicitly requires
them and a safe free alternative is documented.

## Learning design

1. Define concrete, observable learning outcomes.
2. Order modules so each one relies only on earlier material.
3. Start with the smallest runnable or observable result, then progress through
   core syntax/concepts, composition, data or state, error handling, testing,
   tooling, integration, and advanced or platform-specific concerns.
4. Teach one main idea at a time with concise explanations and small examples.
5. Use active learning: ask learners to predict, run, modify, explain, and
   recreate examples.
6. Include common mistakes, debugging guidance, review questions, and
   checkpoints throughout.
7. Pair every lesson module with exercises and verifiable feedback.
8. End with a capstone that combines the important course concepts without
   introducing a large unrelated framework.
9. State what the course intentionally does not cover and point to official
   next-step resources.

## Required repository structure

Adapt extensions and commands to the subject, while preserving these roles:

```text
/
├── README.md
├── CHEATSHEET.md
├── docs/
│   ├── README.md
│   └── SETUP.md
├── lessons/
│   ├── README.md
│   ├── 01_<first_module>/
│   │   ├── README.md
│   │   └── <small runnable examples>
│   └── ...
├── exercises/
│   ├── README.md
│   ├── 01_<first_module>/
│   │   ├── README.md
│   │   ├── <starter exercise files>
│   │   └── <reference solutions>
│   └── ...
├── project/
│   ├── README.md
│   └── <capstone and any smaller integration projects>
├── <ecosystem configuration and dependency files>
└── <continuous-integration workflow>
```

If the subject is not file- or code-oriented, replace runnable examples with
the smallest reproducible artifacts appropriate to it, such as manifests,
queries, notebooks, diagrams, commands, or configuration. Explain every
structural deviation in the root README.

## Content requirements

### Root guide

The root `README.md` is the learner's entry point. Include:

- purpose, audience, prerequisites, supported versions, and course boundaries;
- measurable outcomes and a linked course outline;
- exact setup and first-run instructions;
- a study loop that emphasizes prediction and experimentation;
- links to lessons, exercises, projects, setup, and cheat sheet;
- exact formatting, linting, building, type-checking, and testing commands;
- conventions used in samples; and
- troubleshooting and guidance on using reference solutions.

Keep all links and commands valid from a fresh checkout.

### Lessons

Create enough modules to cover the stated scope without padding the course.
Each module must contain:

- objectives and required prior knowledge;
- an explanation in plain language;
- focused, idiomatic examples that can be run or reproduced independently;
- expected behavior or output where useful;
- at least one experiment for the learner to modify;
- common mistakes and how to diagnose them;
- a summary and review questions; and
- links to the matching exercises and authoritative references.

Examples must explain why an operation is useful, not narrate obvious syntax.
Avoid unexplained abstractions and avoid relying on concepts not yet taught.

### Exercises

Give each lesson module a matching, consistently named exercise directory.
Include:

- clear tasks with inputs, outputs, constraints, and edge cases;
- starter artifacts containing only the scaffolding learners need;
- deterministic checks or tests that provide actionable failures;
- reference solutions kept separate from starter files; and
- instructions that encourage an attempt before viewing the solution.

Exercise checks are learning feedback, not a substitute for explaining the
contract. Solutions should be readable and idiomatic; mention when multiple
approaches are valid.

### Projects

Provide a capstone that is useful, locally reproducible, and large enough to
integrate the main outcomes. Include:

- a problem statement and staged milestones;
- architecture and data-flow documentation;
- exact run and test commands;
- representative automated tests, including failure and boundary cases;
- safe handling of files, network calls, state, and user input where relevant;
- extension ideas ordered from small to ambitious; and
- explanations of any techniques beyond the lesson material.

Smaller projects may be added when they bridge lessons to the capstone. If
multiple projects interact, document their ownership and data flow.

### Setup and reference material

`docs/SETUP.md` must cover installation, version verification, workspace
creation, dependency installation, editor-agnostic execution, and common setup
failures. Clearly distinguish required tools from optional conveniences.

`CHEATSHEET.md` must be a compact recall aid, not a duplicate textbook. Include
the most useful syntax, commands, terminology, and links to official references.

## Engineering and safety requirements

- Use idiomatic conventions for **Subject** and the selected supported versions.
- Pin or constrain tools and dependencies where reproducibility requires it.
- Prefer deterministic, offline-capable examples and tests.
- Keep generated files, build output, local databases, secrets, and editor
  state out of version control with an appropriate ignore file.
- Never embed tokens, passwords, private endpoints, or realistic credentials.
- Validate external input and avoid teaching insecure defaults.
- Make examples portable across the declared environments, or clearly label
  platform-specific material.
- Add automated checks using the ecosystem's established formatter, linter,
  compiler/build tool, type checker, test runner, and coverage tool as
  applicable. Do not add meaningless tools merely to fill this list.
- Configure continuous integration to run the same checks documented for local
  use.
- Test commands and links exactly as written from a clean repository checkout.

## Execution process

Work in these stages and keep the repository usable after each stage:

1. **Research:** inspect the existing repository, official subject
   documentation, current supported versions, and ecosystem conventions.
2. **Design:** write the outcomes, boundaries, module dependency sequence,
   exercise strategy, capstone architecture, and quality gates.
3. **Scaffold:** create navigation, setup instructions, configuration, and the
   complete directory structure.
4. **Build modules:** finish each lesson and its matching exercises together;
   run every example and check before moving on.
5. **Build projects:** implement and document the capstone in milestones, with
   tests for normal, boundary, and failure behavior.
6. **Integrate:** complete the cheat sheet, cross-links, local quality commands,
   and continuous integration.
7. **Audit:** verify educational progression, technical correctness,
   consistency, portability, accessibility, links, commands, tests, security,
   and absence of secrets.

Do not leave placeholders, fake output, disabled checks, unfinished exercises,
or TODO-only sections in the completed repository. If an input is ambiguous,
make a reasonable documented assumption; ask only when the decision would
substantially change the course audience or scope.

## Completion report

Before declaring the work complete, verify and report:

- the final module sequence and how prerequisites progress;
- the lesson-to-exercise mapping;
- the capstone concepts and architecture;
- setup, run, format, lint, build, check, test, and coverage commands;
- the result of every automated validation;
- any intentionally unsupported environment or omitted topic; and
- confirmation that links were checked and changed files were scanned for
  secrets.

The repository is complete only when a learner can follow the root README from
a fresh checkout, reproduce every lesson, receive useful exercise feedback,
run the capstone, and pass the documented quality checks without undocumented
steps.
