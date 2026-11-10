---
id: FB-planning-evidence-not-retaken-after-base-refresh
title: A Planning turn after a base refresh has no step that retakes head-pinned evidence
scope: repo
kind: suggestion
category: missing-capability
target: the spec skill's references/planning.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-planning-evidence-not-retaken-after-base-refresh] A Planning turn after a base refresh has no step that retakes head-pinned evidence

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `planning.md` sends a missing document ID or CLI feature to the Host as a problem and lets
  the Host refresh the branch. No step tells the turn that runs after a refresh to retake what the bundle pinned to
  the earlier head. The caller listed each stale item in its payload by hand.
- **Proposed Procedure**: add to step 2 (or as a step before it): when the branch head moved since the last turn's
  `--head` by a merge of the base, retake the bundle's head-pinned facts before folding: counts and inventories in
  `materials/`, every ID the bundle cites (`devkit docs resolve`), and each sentence that says what exists or does
  not exist on the base. Add that a turn records such facts only for its own worktree head, never for a base commit
  it has not got.
- **Expected Benefit**: stale counts, dead IDs and false "none exists" statements do not reach the `plan-accept`
  request, and the caller's payload shrinks to the answers.
- **Cost & Risk**: a later turn repeats inventory work; limiting the step to facts the bundle pins to a commit keeps
  it small.
- **Attempted**: done in this run on the caller's instruction; the proposed wording was not tried.

## Diagnostic Details

- **Reproduction**: a Planning turn records an inventory at head A and sentences about base commit B it did not hold;
  the base is merged into the branch; the next turn folds answers.
- **Expected / Actual**: expected the bundle to describe the refreshed head; three kinds of stale content remained
  and `devkit rules check docs/proposals/` reported none of them.
- **Versions**: the repository at `c84a5485`.
- **Conditions**: `local-orchestrated`, a base that gains decisions and proposals between two Planning turns.
- **Workarounds Attempted**: recounted with a read-only probe and resolved each cited ID; succeeded.
- **Related Assets**: the `spec` skill's `references/planning.md`, the `planning-worker` contract,
  `RULE-document-reference` (materials are outside it).

## Evidence

```text
Bundle at the refreshed head, before this turn:
- proposal.md and materials: "65 ADRs", "26 pairs", pinned to the earlier head; the refreshed head holds 66 and 27.
- materials cited two IDs of a proposal handed off on the base; devkit docs resolve: DOCS_ID_UNRESOLVED for both.
- proposal.md: "None exists on the base at <base commit>" for open PADRs naming `supersedes`; two PADRs of an
  accepted proposal on that commit name it.
devkit rules check docs/proposals/ on that head: errors=0 (materials are excluded from RULE-document-reference).
```
