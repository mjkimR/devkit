---
id: FB-direct-host-support-role-wait-rule
title: Direct-mode Planning has no rule to wait for a started support role
scope: repo
kind: suggestion
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/planning.md
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: resolved
resolved_at: 2026-10-19
disposition: Added explicit instruction to planning.md step 3 to wait for every started support role to return before relying on its result and never end the turn while one is still running, matching planning-worker.md.
created_at: 2026-10-19
---

# [FB-direct-host-support-role-wait-rule] Direct-mode Planning has no rule to wait for a started support role

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ADR-orchestration-workers` keeps "wait for every role you
  start, never end the turn while one is still running, a failed role is a problem" in the `planning-worker`
  contract. `spec/references/planning.md` and `spec-delegate/SKILL.md` carry no such rule, so a Host running
  Planning in `direct` mode that starts a background `challenger` has no written instruction to wait for it before
  writing its single `worker` envelope. Found by the `code-reviewer` in Development of
  `SPEC-direct-planning-procedure` (`review-01.yaml` finding 1).
- **Proposed Procedure**: move the generic wait and failed-role sentences into `planning.md` step 3 and keep only the
  nested spawn (Host -> worker -> role) in the contract.
- **Expected Benefit**: a `direct` Host and a worker follow the same wait rule from one place.
- **Cost & Risk**: changes the accepted ADR split, so it needs a new decision, not an edit inside this spec.
- **Attempted**: hypothesis; not changed in this spec.

## Evidence

- `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/planning.md` step 3 (no wait rule).
- `packages/devkit-spec/src/devkit_spec/bundle/subagents/planning-worker.md` step 3 (the rule, worker only).
