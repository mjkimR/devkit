---
id: FB-code-reviewer-probe-deletion
title: The code-reviewer contract still asks to delete its ignored probes
scope: repo
kind: change-request
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md (rule 4)
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-code-reviewer-probe-deletion] The code-reviewer contract still asks to delete its ignored probes

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the code-reviewer contract lets the reviewer write throwaway probe tests under the ignored
  probe path the payload names and says "Delete every probe before you return, so `git status --short` stays
  unchanged"; `CAP-DLV-delivery-workflows` describes the probes as "deleted before it returns".
  `SPEC-feedback-guidance-and-scope` now has workers leave ignored scratch files to worktree removal, because a host
  can deny the recursive removal (`FB-fixture-removal-denied`).
- **Proposed Procedure**: decide whether the reviewer keeps deleting its probes (a reviewer probe is usually one file,
  removable without a recursive delete) or follows the workers: leave probes in the ignored path, which keeps
  `git status --short` unchanged anyway, for removing the worktree to clean.
- **Expected Benefit**: one rule for ignored scratch files across the roles the Host delegates to.
- **Cost & Risk**: one sentence in the contract, its mirror in `CAP-DLV-delivery-workflows` and the pinned phrase in
  `test_delegation_sandbox_guidance.py`; a probe left behind might be read by a later reviewer round in the same
  worktree.
- **Attempted**: not changed: decision 1 of `SPEC-feedback-guidance-and-scope` targets the worker contracts and the
  payload reference, not the reviewer.

## Diagnostic Details

- **Reproduction**: `rg -n "Delete every probe" packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md`.
- **Expected / Actual**: one scratch-file rule / workers leave probes, the reviewer deletes them.
- **Versions**: worktree head of `dev-feedback-guidance-and-scope`.
- **Conditions**: a review run with a probe path.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DLV-delivery-workflows`, `SPEC-delegation-sandbox-guidance`.

## Evidence

```text
code-reviewer.md rule 4: "... Delete every probe before you return, so `git status --short` stays unchanged."
CAP-DLV-delivery-workflows: code-reviewer writes "nothing but throwaway probe tests under the ignored probe path the payload names, deleted before it returns"
```

## Disposition

Resolved by `SPEC-handoff-modes-and-template-report` (decision 2: unify with the workers): the code-reviewer contract writes each round's probes in its own subdirectory of the ignored probe path (for example `<probe path>/review-NN/`), never reads another round's probes and never deletes them, leaving them for worktree removal; the `spec-delegate` payload reference names the per-round subdirectory and `CAP-DLV-delivery-workflows` mirrors the role row. Verified by `test_delegation_sandbox_guidance.py`.
