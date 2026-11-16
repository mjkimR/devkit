---
id: FB-runtime-journal-ordering
title: Runtime synchronization diagram obscures write-ahead journal ordering
scope: repo
kind: friction
category: docs-mismatch
target: docs/architecture/ARCH-06-runtime-view.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-runtime-journal-ordering] Runtime synchronization diagram obscures write-ahead journal ordering

## 1. Friction / Question

- **Context**: The documentation pilot traced file/directory replacement from safety contract to implementation.
- **Expectation**: The runtime overview should preserve the safety-significant order while summarizing interactions.
- **Actual**: `ARCH-06-runtime-view` §1 puts “Write/update managed files & projections” before “Record written paths
  & previous state” inside a loop. `CAP-DIST-sync-and-transactions` §3 item 3 and transaction.py `apply_changes`
  instead write the complete journal before changed files.
- **Workaround**: The pilot explicitly uses the detailed capability and source as mechanism evidence. It treats
  architecture as system interaction context rather than algorithm ordering authority.
- **Suggestion**: In separate authorized architecture work, clarify the journal-before-write sequence without
  expanding the system view into the full implementation algorithm.

## Diagnostic Details

- **Reproduction**: Read the three named sections/symbols at a448f4ef5726039e7ddf61b72cef3bdc722dce19.
- **Expected / Actual**: Explicit write-ahead order versus a diagram visually recording after each changed path.
- **Versions**: Source HEAD above; no runtime recovery was executed.
- **Conditions**: Read-only architecture comparison during the bounded distribution pilot.
- **Workarounds Attempted**: Linked the unique safety owner and explained source ordering in the pilot detail.
- **Related Assets**: `ARCH-06-runtime-view`, `CAP-DIST-sync-and-transactions`, distribution installation transaction.py.

## Evidence

The runtime diagram orders Dist→Target Write/update before Dist→Journal Record within the loop.
The capability says journal contents are flushed before disk changes.
`apply_changes` calls atomic_write for JOURNAL before entering its ordered file-application loop.
No architecture edit is included in this pilot; the Host owns authorization for that separate correction.

- **Disposition**: `SPEC-open-feedback-fixes`: `ARCH-06-runtime-view` §1 writes the journal of pending changes and previous state before the file-write loop, matching `CAP-DIST-sync-and-transactions` §3 item 3; the capability keeps the algorithm.
