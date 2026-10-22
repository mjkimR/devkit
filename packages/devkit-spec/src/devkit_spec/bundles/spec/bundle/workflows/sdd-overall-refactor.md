---
id: sdd-overall-refactor
title: "Overall refactor (task-kind overall-refactor: no Unit, direct with the user)"
status: active
schema_version: 1
# dev-integration is asked after the change is final: its approval is passed as `--given dev-integration`, never
# recorded.
gates:
  plan-intent: { policies: [ask, auto] }  # task intent; explicit user instructions need no repeated prompt
  dev-integration: { answer: given, policies: [ask, auto] }  # off would skip integration
# Shared stages must match across workflows (`devkit workflow validate`); returns are this workflow's own.
# No layout: an overall refactor creates no work unit, envelope, gate record file or reconcile document.
checks:
  - { name: lint-ci-clean, class: runner, description: "devkit rules check --ci --base <ref> passes on the committed head: the Developer runs it after the commit and CI re-runs it as the final gate" }
  - { name: merged, class: runner, description: "the integration unit is merged into the base branch" }
  - { name: exception-raised, class: human, description: "a retry cap, tool failure or unresolved semantic conflict was raised" }
  - { name: exception-handled, class: human, description: "the cause of the exception was handled by the user" }
stages:
  - id: intent-refactor
    name: Plan intent
    human_gate: plan-intent
    entry: []
    exit: []
    artifacts: [agreed goal, scope and non-goals in the conversation]
    skills: [spec]
    role: developer
    isolation: none
    returns: []
  - id: restructure
    name: Restructure and verify
    human_gate: false
    entry: []
    exit: []
    artifacts: [code, tests, Living Spec, checkpoint commits]
    skills: []
    role: developer
    isolation: none
    returns: []
  - id: report-refactor
    name: Review and report
    human_gate: false
    entry: []
    exit: []
    artifacts: [refactor report in the final response and the commit body]
    skills: [spec-review, spec-feedback]
    role: developer
    isolation: none
    returns:
      - { to: restructure, when: defects }
  - id: commit-refactor
    name: Commit
    human_gate: false
    entry: []
    exit: [lint-ci-clean]
    artifacts: [commit]
    skills: []
    role: developer
    isolation: none
    returns:
      - { to: restructure, when: defects found by CI }
      - { to: exception, when: retry caps }
  - id: approval-refactor
    name: Dev integration approval
    human_gate: dev-integration
    entry: []
    exit: []
    artifacts: [session OK or PR ready state (no file)]
    skills: [spec]
    role: developer
    isolation: none
    returns:
      - { to: report-refactor, when: the objection is about the change }
  - id: merge
    name: Merge
    human_gate: false
    entry: [lint-ci-clean]
    exit: [merged]
    artifacts: [merge]
    skills: []
    role: "-"
    isolation: none
    returns:
      - { to: commit-refactor, when: "head, base or approval changed" }
  - id: exception
    name: Exception
    exception: true
    human_gate: false
    entry: [exception-raised]
    exit: [exception-handled]
    artifacts: [exception report]
    skills: [spec]
    role: developer
    isolation: none
    returns:
      - { to: commit-refactor, when: "the stage that raised it, after the cause is handled" }
---

# Overall refactor (`task-kind` overall-refactor)

A structural change across the project that adds no behavior: package boundaries, conventions, document systems or
ledgers that span several areas, whose direction settles while the work proceeds. A refactor inside one feature or
module is not this workflow: it follows the `feature` workflows.

It has no unit: no `spec.md`, `plan.md`, `tasks.md`, `reconcile.md` or envelope. Read the stages with
`devkit workflow show sdd-overall-refactor`; `devkit workflow next` is not used.

- **Mode**: `direct` only. The Host works with the user in the conversation. Do not delegate to `planning-worker` or
  `development-worker`. Use general subagents for parallel drafting, edits across many files and research; the Host
  splits the work, checks each result, talks with the user and commits.
- **Intent**: agree the goal, the scope and what stays out in the conversation; record nothing.
- **Restructure**: change code, tests and the Living Spec together; commit at checkpoints. Work on the base checkout
  or on `dev-<slug>`, as the `GIT_POLICY` levels allow. A lasting policy the refactor settles is an ADR.
- **Verify**: the full test suite (`just test`), lint and type checks, and `devkit rules check`; the Living Spec states
  the result.
- **Review**: at the activity's `activity-effort` as the `spec` skill's `references/effort.md` defines it for
  `session`, at `high` in the bounded rounds of its `references/review-loop.md`; the Host starts the `code-reviewer`
  subagent itself and receives its result as a message, without an envelope.
- **Report**: in the final response and the commit body: what changed and why, every breaking change, the
  verification results and anything left for follow-up.
- **Integration**: on `dev-<slug>`, the session integration path with `task_kind` `overall-refactor` in its claims.
