---
id: FB-compacted-integration-promoted
title: Integration feedback, promoted
summary: Worktree preparation and branch integration procedures.
target: docs/capabilities/integration/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-auto-integration-dispatch
  - FB-integrate-assumes-a-remote-base
  - FB-integrate-merge-message-fails-commit-msg-gate
---

# [FB-compacted-integration-promoted] Integration feedback, promoted

## FB-auto-integration-dispatch

- **Symptom**: Add automatic integration dispatch under dev-integration=auto once ask-mode integration is validated
- **Response**: Promoted outcome
- **Reason**: promoted to `SPEC-policy-authorized-integration`. The proposal owns the decision about policy-granted merge and deletion authority; `ADR-delivery-decision-boundaries` remains the current contract until a successor decision is accepted.

## FB-integrate-assumes-a-remote-base

- **Symptom**: spec-integrate merges origin/main even when the base is ahead of it
- **Response**: src/devkit_spec/bundle/skills/spec-integrate/SKILL.md
- **Reason**: S-Lane; Step 1 pulls the base and merges the base checkout's branch

## FB-integrate-merge-message-fails-commit-msg-gate

- **Symptom**: spec-integrate's base merge uses Git's default message, which a Conventional Commits gate refuses
- **Response**: `src/devkit_spec/bundle/skills/spec-integrate/SKILL.md` (S-Lane)
- **Reason**: Step 1 merges with `-m "<subject the commit-msg gate accepts>"`.
