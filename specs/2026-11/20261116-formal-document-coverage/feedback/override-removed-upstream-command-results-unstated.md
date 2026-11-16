---
id: FB-override-removed-upstream-command-results-unstated
title: Workspace ownership does not state override list, diff and accept results for a record whose asset was removed upstream
scope: repo
kind: friction
category: docs-mismatch
target: CAP-DIST-workspace-ownership
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-override-removed-upstream-command-results-unstated] Workspace ownership does not state override list, diff and accept results for a record whose asset was removed upstream

## 1. Friction / Question (friction, question)

- **Context**: Writing the override lifecycle domain entry from the capability and source.
- **Expectation**: `CAP-DIST-workspace-ownership` §3 states what each override command reports for every record state it keeps.
- **Actual**: For a record kept after its asset was removed or renamed upstream, `override list` shows `drift_detected: false` because no current digest exists, and `override diff` and `override accept` refuse with `SELECTION_INVALID` (asset not found); §3 states a refusal only for no tracked override.
- **Workaround (or Interpretation Chosen)**: The domain entry states the `list` result from source and leaves diff and accept to the capability.
- **Suggestion**: State the `list`, `diff` and `accept` results for a kept record whose asset no longer exists upstream.

## Diagnostic Details

- **Reproduction**: Read-only source reading.
- **Expected / Actual**: A stated result for each command; the source returns false drift and a selection refusal.
- **Versions**: repository head of the formal-document-coverage Development branch.
- **Conditions**: asset removed upstream with override files left
- **Workarounds Attempted**: not attempted
- **Related Assets**: override_commands.py, results.py, CAP-DIST-workspace-ownership §3

## Evidence

```text
packages/devkit-dist/src/devkit_dist/features/distribution/models/results.py: drift_detected false when the current digest is None
packages/devkit-dist/src/devkit_dist/features/distribution/usecases/override_commands.py: diff and accept call _find, which raises SELECTION_INVALID asset not found
```
