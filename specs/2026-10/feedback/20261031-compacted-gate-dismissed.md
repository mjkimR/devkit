---
id: FB-compacted-gate-dismissed
title: Gate feedback, dismissed
summary: Git commit gates, hooks, and lifecycle checks.
target: docs/capabilities/gate/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-commit-rewrite-skews-committer-time
  - FB-plan-intent-overrides-accepted-adr
  - FB-reconcile-close-guidance-names-reverify
---

# [FB-compacted-gate-dismissed] Gate feedback, dismissed

## FB-commit-rewrite-skews-committer-time

- **Symptom**: Commit rewriting stamps times hours away from the wall clock, so committer time does not follow ancestry
- **Response**: Dismissed by the user
- **Reason**: the `[cgate]` commit rewrite is outside this repository, no devkit behavior relies on commit times, and the time-bounded design that exposed it was dropped.

## FB-plan-intent-overrides-accepted-adr

- **Symptom**: A plan-intent can reverse an accepted ADR outcome without ADR write authority
- **Response**: Dismissed outcome
- **Reason**: Dismissed as moot. The user decision recorded with the return to build-verify (`decisions/02-return-build-verify.yaml`) withdrew the plan-intent's refusal and kept the English fallback that `ADR-configuration-language-and-rendering` decides, only making it visible with a `PRESENTATION_LANGUAGE_UNSUPPORTED` warning. `SPEC-feedback-quick-fixes` now conforms to the accepted ADR, the capabilities agree with it again, and no superseding ADR is needed, so the conflict this item describes no longer exists.

## FB-reconcile-close-guidance-names-reverify

- **Symptom**: Effort and delegate guidance still offer reverify for reconcile findings
- **Response**: dismissed. Superseded by the agent asset pruning
- **Reason**: `references/effort.md` now states that each reconcile verification is a `reconcile-check` envelope, and `spec-delegate` no longer names `envelope reverify` for closing findings.
