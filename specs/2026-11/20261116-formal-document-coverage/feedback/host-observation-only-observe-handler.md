---
id: FB-host-observation-only-observe-handler
title: Host lifecycle capability does not say non-observe hooks never produce an observation
scope: repo
kind: question
category: spec-ambiguity
target: CAP-HOST-lifecycle-observation
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-host-observation-only-observe-handler] Host lifecycle capability does not say non-observe hooks never produce an observation

## 1. Friction / Question (friction, question)

- **Context**: Writing the host hook dispatch routing entry.
- **Expectation**: `CAP-HOST-lifecycle-observation` §5 tells a reader whether a missing observation means a hook did not run.
- **Actual**: Only the built-in `observe` handler writes the observation record, so `host status` `last_received` stays null for any other handler even after successful dispatches; a handler failure during a call leaves no persistent evidence, only hook stderr the host may hide. §5 implies this without stating it.
- **Workaround (or Interpretation Chosen)**: The operations entry states that a missing observation proves nothing for a non-observe handler (interpretation chosen from source).
- **Suggestion**: State the observe-only scope of the observation record in §5, and decide whether a last dispatch failure needs a record.

## Diagnostic Details

- **Reproduction**: Read-only source reading.
- **Expected / Actual**: A stated scope for the observation record.
- **Versions**: repository head of the formal-document-coverage Development branch.
- **Conditions**: a hook bound to a handler other than observe
- **Workarounds Attempted**: not attempted
- **Related Assets**: observation.py, status.py, CAP-HOST-lifecycle-observation §5

## Evidence

```text
packages/devkit-dist/src/devkit_dist/features/host/services/observation.py: written by the observe handler only
packages/devkit-dist/src/devkit_dist/features/host/usecases/status.py loads handlers but never calls them
```
