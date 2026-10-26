---
id: FB-handoff-error-modes-documented-differently
title: Handoff error modes in the proposal code table differ from the emitted ones
scope: repo
kind: question
category: docs-mismatch
target: CAP-DLV-proposal-incubation (4.12 Codes), packages/devkit-spec/src/devkit_spec/base/errors.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-handoff-error-modes-documented-differently] Handoff error modes in the proposal code table differ from the emitted ones

## 1. Friction / Question (friction, question)

- **Context**: adding the `SPEC_HANDOFF_STALE` row to `CAP-DLV-proposal-incubation` §4.12 in
  `SPEC-living-spec-consistency-sweep`.
- **Expectation**: each row's level and mode match the advisory the class emits.
- **Actual**: `HandoffNotReadyError`, `HandoffReplyError` and `HandoffStaleError` inherit `SpecError` and emit mode
  `MAINTENANCE`, while the table documents `SPEC_HANDOFF_NOT_READY` as `BLOCKED` and `SPEC_HANDOFF_REPLY_INVALID` as
  `INPUT_ERROR`.
- **Workaround (or Interpretation Chosen)**: the new row documents the emitted `MAINTENANCE`; the two older rows were
  left as they are, because which side is intended is a code-versus-document decision.
- **Suggestion**: decide whether the classes should set `BLOCKED` and `INPUT_ERROR` (a code change) or the table should
  say `MAINTENANCE`.

## Diagnostic Details

- **Reproduction**: `HandoffNotReadyError("x").to_dict()["advisory"]["mode"]`, reported by the reconcile review.
- **Expected / Actual**: `BLOCKED` / `MAINTENANCE` (and `INPUT_ERROR` / `MAINTENANCE`).
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DLV-proposal-incubation`.

## Evidence

```text
base/errors.py:602-620 HandoffNotReadyError, HandoffReplyError, HandoffStaleError(SpecError) set only code
CAP-DLV-proposal-incubation 4.12: SPEC_HANDOFF_NOT_READY ERROR (BLOCKED); SPEC_HANDOFF_REPLY_INVALID ERROR (INPUT_ERROR)
```
