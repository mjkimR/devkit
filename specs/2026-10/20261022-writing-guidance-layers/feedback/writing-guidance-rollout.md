---
id: FB-writing-guidance-rollout
title: Rewrite the remaining bundle skills, playbooks and instructions under agent-asset-writing
scope: repo
kind: change-request
category: other
target: packages/*/src/**/bundle/{skills,playbooks,instructions}/
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-writing-guidance-rollout] Rewrite the remaining bundle skills, playbooks and instructions under agent-asset-writing

Deferred work retained by `SPEC-writing-guidance-layers` (Non-Goal 1).

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: Only `spec-plan` and the `skill-authoring` playbook follow `agent-asset-writing`; the
  other bundle skills, playbooks and instructions keep sentences that stack a condition, an action, an exception and
  a cross-reference.
- **Proposed Procedure**: A rollout spec that rewrites them in batches, each skill with a constraint mapping table
  (no dropped constraint) and a behavior comparison of several dry runs per scenario per version, graded blind
  against expected-behavior lists fixed before the runs.
- **Expected Benefit**: Directive text an agent acts on without unpacking; fewer misses on conditional branches.
- **Cost & Risk**: Many files; a rewrite can drop a constraint, which the mapping table guards against. One run per
  version and scenario did not separate small differences in the pilot.
- **Attempted**: Pilot on `spec-plan`: no regression and no measurable improvement (final text vs old: S1 11/11 vs
  10/11, S2 9/9 vs 9/9, S3 7/8 vs 6/8).

## Diagnostic Details

- **Reproduction**: not applicable.
- **Expected / Actual**: not applicable.
- **Versions**: devkit-spec at the `SPEC-writing-guidance-layers` integration.
- **Conditions**: Restart once `SPEC-writing-guidance-layers` is integrated.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `ADR-layered-writing-guidance`, `specs/2026-10/20261022-writing-guidance-layers/pilot.md`.

## Evidence

```text
Acceptance checks for the rollout: every rewritten file has a mapping table with zero dropped entries; for each
scenario, the new text meets at least as many expected behaviors as the old text over several runs.
```
