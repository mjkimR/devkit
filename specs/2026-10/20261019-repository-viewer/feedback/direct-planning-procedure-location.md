---
id: FB-direct-planning-procedure-location
title: Direct-mode Planning steps are only in the planning-worker contract
scope: repo
kind: suggestion
category: other
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/SKILL.md
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-direct-planning-procedure-location] Direct-mode Planning steps are only in the planning-worker contract

Procedure discoverability: the Host running Planning in `direct` mode has no step list of its own.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the `spec` skill's routing table says Planning "runs on `plan-<slug>` to `plan-accept`" and
  `effort.md` gives the review depth per effort. The ordered steps (set `status: reviewing` and commit first, record
  decisions as PADRs with a summary, gather questions in one round, update `dev_effort`, sweep feedback, end with one
  `worker` envelope) are written only in the `planning-worker` role contract. `worker-records.md` says a direct-mode
  Host writes its own `worker` envelope, but not the other steps.
- **Proposed Procedure**: add a short Planning reference to the `spec` skill (or a pointer from the routing table)
  that lists those steps for any executor, and have the `planning-worker` contract cite it instead of owning it.
- **Expected Benefit**: a direct-mode Host finds the procedure without reading a subagent contract written for a
  different actor; one place to change the steps.
- **Cost & Risk**: one more reference file; the role contract and the reference must not diverge (moving the steps
  rather than copying them avoids that).
- **Attempted**: this run followed the `planning-worker` contract's steps in `direct` mode, minus delegation.

## Diagnostic Details

- **Reproduction**: start a proposal's Planning in `direct` mode from the `spec` skill and look for its steps.
- **Expected / Actual**: expected a Planning step list reachable from the `spec` skill; found it in
  `.devkit/managed/spec/subagents/planning-worker.md` only.
- **Versions**: devkit-spec at the repository revision of this proposal's Planning branch.
- **Conditions**: `direct` mode, `planning_effort: low`.
- **Workarounds Attempted**: read the role contract and applied it.
- **Related Assets**: `spec` skill `SKILL.md` routing table, `references/worker-records.md` §1, `references/effort.md`,
  the `planning-worker` role contract.

## Evidence

```text
spec SKILL.md, routing table row for proposal: "Planning (its own activity) runs on plan-<slug> to plan-accept
(updating dev_effort before acceptance)"
worker-records.md §1: "in direct mode you write it for your run whenever you stop for the user or end the activity"
planning-worker contract, Procedure 2: "On the first turn set status: reviewing in proposal.md and commit it."
```
