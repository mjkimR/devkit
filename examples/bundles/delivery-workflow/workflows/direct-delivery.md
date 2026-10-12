---
id: direct-delivery
title: "Direct delivery"
status: active
schema_version: 1
checks:
  - { name: ci-passed, class: runner, description: "repository CI is green for the integrated change" }
stages:
  - id: intent
    name: Intent
    human_gate: direction
    entry: []
    exit: [anchor-exists, not-skeleton(task.md)]
    artifacts: [task.md]
    skills: [devkit-workflow]
    role: developer
    isolation: none
    returns: []
  - id: build-verify
    name: Build and verify
    human_gate: false
    entry: [tasks-exists]
    exit: [tasks-all-checked, lint-clean]
    artifacts: [code, tests, tasks.md]
    skills: [devkit-workflow]
    role: developer
    isolation: none
    returns:
      - { to: intent, when: new requirements appear }
  - id: review
    name: Review loop
    human_gate: false
    entry: [tasks-all-checked]
    exit: [envelope-review-passed]
    artifacts: [envelopes/review-NN.yaml]
    skills: [devkit-workflow]
    role: reviewer
    isolation: preferred
    returns:
      - { to: build-verify, when: defects are found }
  - id: integrate
    name: Integrate
    human_gate: integration
    entry: [envelope-review-passed]
    exit: [anchor-status-completed, ci-passed]
    artifacts: []
    skills: [devkit-workflow]
    role: developer
    isolation: none
    returns: []
---

## Gate rules

- **direction**: the user states the intent and scope before work starts. Under `auto` the agent records its assumptions in `task.md` instead of asking.
- **integration**: the user approves the reviewed change before it is integrated. The agent presents the latest review envelope and the test results, then waits.

## Stage notes

- `build-verify` is done when every task in `tasks.md` is checked and `agent-rules check` passes on the unit's files.
- `review` is performed by a review skill when the consumer ships one (swap it into `skills`), preferably as a delegated reviewer; the result is written to `envelopes/review-NN.yaml` and a `reverify` envelope closes a round with findings.
- `integrate` requires the anchor status to be `completed` and CI to be green (`--given ci-passed` after the run).
