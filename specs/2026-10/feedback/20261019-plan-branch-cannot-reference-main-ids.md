---
id: FB-plan-branch-cannot-reference-main-ids
title: A Planning branch cannot cite documents integrated on main after it was cut
scope: repo
kind: friction
category: instruction-conflict
target: RULE-document-reference on a plan- branch worktree (Planning workers do not merge main; the Host merges at acceptance)
skill: spec-delegate
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-plan-branch-cannot-reference-main-ids] A Planning branch cannot cite documents integrated on main after it was cut

## 1. Friction / Question (friction, question)

- **Context**: A `high` Planning turn re-checked its PADRs against `main`, which had moved since the `plan-` branch
  was cut. The decisions now depend on an ADR and a draft proposal that exist only on `main` (the role effort presets
  decision, the worker range validation proposal, the bounded review loop ADR).
- **Expectation**: The PADR cites them by ID, so the promoted ADR keeps a checkable reference.
- **Actual**: The commit gate's `RULE-document-reference` refuses each ID ("no document has the ID ..."), because the
  branch does not contain them, and the worker may not merge `main` (the Host does so at acceptance).
- **Workaround (or Interpretation Chosen)**: Named those documents in plain words with "on `main`", which the rule does
  not check; after the Host's merge the references stay unlinked and unchecked.
- **Suggestion**: Either let the Host merge `main` into the `plan-` branch before a Planning turn that follows a base
  advance, or let the reference rule resolve IDs against the integration base for a `plan-` branch, so a PADR can cite
  what Planning actually reviewed.

## Diagnostic Details

- **Reproduction**: On `plan-worktree-host-compatibility` (cut at 298dd9e), write a code-span reference to the role
  effort presets ADR's ID in a PADR and run `devkit rules check docs/proposals/PROP-worktree-host-compatibility`.
- **Expected / Actual**: Expected the reference to resolve against what Planning read; observed an error-severity
  violation.
- **Versions**: devkit at the worktree's head; `main` at 1b954e6.
- **Conditions**: local-orchestrated Planning; write scope limited to the proposal directory; no merge allowed.
- **Workarounds Attempted**: plain-word references only.
- **Related Assets**: `planning-worker` Git boundary; `spec-delegate` payload (Host merges at acceptance);
  `RULE-document-reference`.

## Evidence

```text
[VIOLATION: RULE-document-reference severity=error file=.../PADR-codex-process-worker.md line=61
 message="no document has the ID ADR-role-effort-presets"]
[VIOLATION: RULE-document-reference ... message="no document has the ID PROP-worker-range-validation"]
```

Historical source: Git `1b8478093a44cf2d0b74c412bffc93f259459ef0:docs/proposals/PROP-worktree-host-compatibility/feedback/plan-branch-cannot-reference-main-ids.md`; relative evidence paths refer to that proposal bundle.
