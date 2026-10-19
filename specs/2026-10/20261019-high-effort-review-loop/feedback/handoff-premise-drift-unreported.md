---
id: FB-handoff-premise-drift-unreported
title: Proposal premises changed between plan-accept and Development are found only by reading history
scope: repo
kind: suggestion
category: missing-capability
target: devkit spec proposal handoff
skill: spec-specify
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-handoff-premise-drift-unreported] Proposal premises changed between plan-accept and Development are found only by reading history

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the `development-worker` contract asks a handed-off spec to check the proposal's premises
  (target paths, interfaces, boundaries) against the current base. Nothing points at what changed: the worker
  finds drift only by reading the target files and their `git log`.
- **Proposed Procedure**: `devkit spec proposal handoff` (or `spec-specify` for a handed-off bundle) lists the commits
  since the proposal's `plan-accept` record that touched the proposal's declared boundaries or target documents, as a
  notice, so the premise check starts from a list.
- **Expected Benefit**: drift between acceptance and Development is visible at the first step instead of depending on
  the worker noticing it while reading.
- **Cost & Risk**: one Git query per handoff; boundaries are directory-level, so the list may be long for broad
  proposals (a count with the first few commits keeps output small).
- **Attempted**: in `SPEC-high-effort-review-loop`, commit `a37add2` (same day, after Planning) rewrote the `high`
  proposal triggers in `effort.md`, which the proposal's problem statement and §3.5 relied on. It was found only by
  running `git log` on `effort.md` while reading it; the spec records the adaptation as an assumption.

## Evidence

- `effort.md` before `a37add2`: "Propose `high` when the work reverses an upstream or accepted decision ..., creates
  a contract or a document kind, or affects more than one package"; after: "Propose `high` only when (a) the work has
  an effect that cannot be undone locally ... or (b) an earlier activity or review of the same work left P1 findings
  unresolved".
- Handoff output and `devkit workflow next` for the unit name no change since `plan-accept`.

- **Disposition**: Deferred as open feedback. `PROP-worker-range-validation` covers existing worker-result checks
  only; handoff premise drift is outside its scope.
