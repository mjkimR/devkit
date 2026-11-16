---
id: FB-attention-base-check-differs-from-verify
title: Adaptive assignments capability does not say list base-not-ancestor uses HEAD while verify base uses the return's final commit
scope: repo
kind: friction
category: docs-mismatch
target: CAP-DLV-adaptive-assignments
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-attention-base-check-differs-from-verify] Adaptive assignments capability does not say list base-not-ancestor uses HEAD while verify base uses the return's final commit

## 1. Friction / Question (friction, question)

- **Context**: Writing the assignment attention routing entry.
- **Expectation**: `CAP-DLV-adaptive-assignments` §4 tells a reader how `list` attention and `verify` checks relate.
- **Actual**: `list` reports `base-not-ancestor` when the current worktree HEAD does not descend from the base; `verify`'s `base` check compares the base with the return's `final` commit, so the two disagree once HEAD moves after a return. §4 also does not say a closed assignment renders `attention=-` in text, the same as the normal state.
- **Workaround (or Interpretation Chosen)**: The operations entry states both differences as evidence, citing source.
- **Suggestion**: State the compared commit for each, and how a reader separates closed from no attention in text.

## Diagnostic Details

- **Reproduction**: Read-only source reading.
- **Expected / Actual**: A stated compared commit per surface.
- **Versions**: repository head of the formal-document-coverage Development branch.
- **Conditions**: assignment with a return and a later worktree commit
- **Workarounds Attempted**: not attempted
- **Related Assets**: verification.py, CAP-DLV-adaptive-assignments §4

## Evidence

```text
packages/devkit-adaptive/src/devkit_adaptive/features/assignment/services/verification.py: list observation compares base with HEAD; verify base check uses final
cli/commands.py joins an empty attention list; field_value renders it as -
```
