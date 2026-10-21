---
id: sdd-session-bugfix
title: "Session bugfix (planning-depth session, task-kind bugfix: reproduce first, no Unit)"
status: active
schema_version: 1
# dev-integration is asked after the change is final: its approval is passed as `--given dev-integration`, never
# recorded (ADR-integration-approval-asserted).
gates:
  plan-intent: { policies: [ask] }  # always a person (01 §3); configuration cannot pass it
  dev-integration: { answer: given, policies: [ask, auto] }  # off would skip integration
# Shared stages must match across workflows (`devkit workflow validate`); returns are this workflow's own.
# No layout: a session creates no work unit, envelope, gate record file or reconcile document.
checks:
  - { name: lint-ci-clean, class: runner, description: "devkit rules check --ci --base <ref> passes on the committed head: the Developer runs it after the commit and CI re-runs it as the final gate" }
  - { name: merged, class: runner, description: "the integration unit is merged into the base branch" }
  - { name: exception-raised, class: human, description: "a retry cap, tool failure or unresolved semantic conflict was raised" }
  - { name: exception-handled, class: human, description: "the cause of the exception was handled by the user" }
stages:
  - id: intent-session
    name: Plan intent
    human_gate: plan-intent
    entry: []
    exit: []
    artifacts: [agreed intent in the conversation or the Work Plan Item]
    skills: [spec]
    role: developer
    isolation: none
    returns: []
  - id: reproduce-session
    name: Reproduce (Red)
    human_gate: false
    entry: []
    exit: []
    artifacts: [failing reproduction test]
    skills: []
    role: developer
    isolation: none
    returns:
      - { to: intent-session, when: the defect is not what was agreed }
  - id: execute-verify
    name: Execute and verify
    human_gate: false
    entry: []
    exit: []
    artifacts: [code, tests]
    skills: []
    role: developer
    isolation: none
    returns: []
  - id: report-session
    name: Review and report
    human_gate: false
    entry: []
    exit: []
    artifacts: [session report in the final response or the PR body]
    skills: [spec-review, spec-feedback]
    role: developer
    isolation: none
    returns:
      - { to: execute-verify, when: defects }
  - id: commit-session
    name: Commit
    human_gate: false
    entry: []
    exit: [lint-ci-clean]
    artifacts: [commit]
    skills: []
    role: developer
    isolation: none
    returns:
      - { to: execute-verify, when: defects found by CI }
      - { to: exception, when: retry caps }
  - id: approval-session
    name: Dev integration approval
    human_gate: dev-integration
    entry: []
    exit: []
    artifacts: [session OK or PR ready state (no file)]
    skills: [spec]
    role: developer
    isolation: none
    returns:
      - { to: report-session, when: the objection is about the change }
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
      - { to: commit-session, when: "head, base or approval changed" }
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
      - { to: commit-session, when: "the stage that raised it, after the cause is handled" }
---

# Session bugfix (`planning-depth` session, `task-kind` bugfix)

A defect against an agreed contract that the session can reproduce and fix without written documents. The expected behavior is agreed at `plan-intent`. All other rules of the `sdd-session-feature` body apply, its review included (the `spec` skill's `references/effort.md`, at `high` its `references/review-loop.md`).

- **Red before Green.** Before the fix, write a test that reproduces the defect and confirm it fails (Red, `reproduce-session`); then fix it so the test passes (Green, `execute-verify`). The test stays as a regression test. A compile, environment or test-setup failure unrelated to the defect is not reproduction; a build failure that is the defect is.
- **Report the evidence.** The final response or the PR body includes the Red then Green evidence: the reproduction command, its failure before and its pass after the fix.
- When the defect is hard to reproduce, or the current, expected and preserved behavior must be written down, raise the depth to `spec` (`sdd-spec-bugfix`). When the agreed expected behavior cannot be kept, report it as a problem.
