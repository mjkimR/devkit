---
id: FB-merge-conflict-guardrail-action
title: Merge conflict refusal pairs a guardrail action with a reconcile fix
scope: repo
kind: question
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/base/errors.py (ProposalTargetExistsError)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-merge-conflict-guardrail-action] Merge conflict refusal pairs a guardrail action with a reconcile fix

## 1. Friction / Question (friction, question)

- **Context**: SPEC-merge-proposal-materials-at-handoff gives a materials merge conflict its own fix under the kept
  code `SPEC_PROPOSAL_TARGET_EXISTS`, as `ADR-merge-proposal-materials-per-leaf-at-handoff` decides.
- **Expectation**: An agent reading the refusal gets one consistent directive.
- **Actual**: `ProposalTargetExistsError` sets `guardrail = True`, so the rendered `[ACTION]` says the refusal is a
  deliberate guardrail and forbids proposing or applying a way around it, while the merge fix tells the agent to
  reconcile one path (rename, move or make identical) and rerun.
- **Workaround (or Interpretation Chosen)**: Kept the code and the guardrail flag, since the ADR keeps the code and
  the error class; the fix text carries the reconciliation.
- **Suggestion**: Decide whether a merge conflict should be an agent-fixable refusal (no guardrail action) or whether
  the fix should tell the agent to report the conflict to the user before reconciling it.

## Diagnostic Details

- **Reproduction**: `devkit spec proposal handoff <slug> --format json` with differing bytes at the same path in the
  dated materials directory and the proposal's `materials/`.
- **Expected / Actual**: one directive / an `action` of `BLOCKED` beside a `fix` that starts with `Reconcile`.
- **Versions**: worktree head of the spec bundle.
- **Conditions**: any merge conflict.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `ProposalTargetExistsError`, `_refuse_merge` in the handoff use case, `CAP-DLV-proposal-incubation`.

## Evidence

```text
"action": "BLOCKED — A deliberate guardrail refused this. Report it and stop. Do not propose or apply a way around it; ..."
"fix": "Reconcile docs/proposals/PROP-x/materials/a.md with the existing docs/materials/.../a.md (different-content): ..."
```
