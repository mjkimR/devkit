---
id: FB-base-measurement-outside-worker-git
title: Acceptance outcomes timed on the integration base exceed a worker's Git rights
scope: repo
kind: friction
category: instruction-conflict
target: spec skill references/planning.md (acceptance outcomes), development-worker role contract
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-base-measurement-outside-worker-git] Acceptance outcomes timed on the integration base exceed a worker's Git rights

## 1. Friction / Question (friction, question)

- **Context**: Development of a unit whose performance outcome (AC-10) compares a command "on the integration base
  without the change" with the head, as cold runs on one machine.
- **Expectation**: A development worker can produce every acceptance outcome's evidence inside its worktree.
- **Actual**: The worker may only commit (no checkout, worktree or reset), and its scratch files must stay in its
  worktree. Running the base commit needs a second checkout or a nested repository. The worker measured the head
  with the new behavior disabled by a patch instead, and the code review raised that as a P3 deviation.
- **Workaround (or Interpretation Chosen)**: Recorded the patched-head baseline and the method deviation in the unit's
  evidence and waived the finding. Planning's own cold base measurement on the same machine corroborated the
  baseline.
- **Suggestion**: When Planning writes a before/after outcome, have it name a baseline a worker can produce (the head
  with the change disabled, or a Planning measurement on the same machine), or have the Host take the base
  measurement.

## Diagnostic Details

- **Reproduction**: SPEC-lint-clean-target-scoped-rules AC-10 and review-01.yaml finding 3.
- **Expected / Actual**: expected a base-commit timing; actual a patched-head timing (3.71 s, vs Planning's 3.65 s cold base).
- **Versions**: not applicable.
- **Conditions**: development-worker contract, Git commit-only.
- **Workarounds Attempted**: method deviation recorded in evidence.md section 2.
- **Related Assets**: `.devkit/managed/spec/subagents/development-worker.md` (Write boundaries, Git), the unit's
  `evidence.md`.

## Evidence

```text
development-worker.md: "Git: commit only; never push, merge, rebase, reset, amend, stash or check out."
review-01.yaml finding 3: "AC-10's baseline was measured on the head with scope_rules patched, not on the integration base 3015be11."
```

## Disposition

Resolved by `SPEC-delegation-sandbox-guidance`: the `spec` skill's `references/planning.md` step 5 has Planning name a
baseline a development worker can produce for a before/after outcome (the head with the change disabled, or a
Planning measurement on the same machine recorded in `materials/`), or state that the Host takes the base
measurement. The `development-worker` contract measures against the named baseline, never checks out the base, and
reports a missing base measurement for the Host in its `worker` envelope. Verified by
`packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`.
