---
id: FB-compacted-other-dismissed
title: Other feedback, dismissed
summary: General operational feedback and development ergonomics.
target: other
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-affected-selector-helper-resolution-cost
  - FB-feature-branch-pushed-without-a-push-command
  - FB-host-smoke-stdin-isolation
  - FB-ruff-formats-plan-snippets
---

# [FB-compacted-other-dismissed] Other feedback, dismissed

## FB-affected-selector-helper-resolution-cost

- **Symptom**: Profile the remaining per-run helper resolution cost
- **Response**: Dismissed
- **Reason**: additional measurement on source revision `6b21869d9029e22886fc6d5511b82c67bc9297cc` found approximately 1.15–1.55 seconds of extra selector time across the nine cases. A helper inventory does not have enough demonstrated benefit to justify additional dependency-resolution complexity. Separate single pytest runs with eight workers, plus selector medians from three samples, retained net improvements for gate (14.58 to 10.78 seconds) and rules (61.34 to 54.80 seconds). Scope, documents and proposals retain the costly integration consumers; removed scope/proposal tests account for only 0.08/0.06 summed worker-seconds in the full run. Scope's single selected execution was slower, so no universal runtime improvement is claimed. Whole-workspace verification passed 3,993 tests with 12 skipped, and all six selected executions passed. Keep the existing selector and investigate repeated integration-test preparation separately; no selector optimization is required.

## FB-feature-branch-pushed-without-a-push-command

- **Symptom**: A devkit feature branch reached the remote although no push was run
- **Response**: Dismissed
- **Reason**: a separate manual push may have included the feature branch; the cause remains unverified, and no further investigation or repository policy change is required for this isolated observation.

## FB-host-smoke-stdin-isolation

- **Symptom**: Close stdin when launching one-shot host smoke clients
- **Response**: Dismissed outcome
- **Reason**: dismissed. The input leak came from an ad hoc launcher used once for live host evidence; the repository has no `codex exec` or `claude -p` launcher to change.

## FB-ruff-formats-plan-snippets

- **Symptom**: ruff format checks the Python snippets of spec plans
- **Response**: Dismissed outcome
- **Reason**: `just lint` formats the snippets automatically and keeps them valid Python; no exclusion needed
