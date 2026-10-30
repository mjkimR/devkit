---
id: FB-handbook-journey-misses-handoff-commit
title: Handbook proposal journey misses the composed handoff commit
scope: repo
kind: change-request
category: docs-mismatch
target: handbook/en/journeys/incubate-and-hand-off-a-proposal.md
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-30
---

# [FB-handbook-journey-misses-handoff-commit] Handbook proposal journey misses the composed handoff commit

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The release handbook journey (`handbook/en/` and `handbook/ko/`
  `journeys/incubate-and-hand-off-a-proposal.md`) describes the composed handoff as write-only: it does not say the
  composed handoff commits its transaction or that its output carries `commit=`, its error table has no
  `SPEC_HANDOFF_COMMIT_REFUSED` row and no landed-but-unclean case under `SPEC_HANDOFF_STALE`, it still says the
  agent fixes unresolved links "in the same change", and it does not name the sibling-draft conflict resolution.
- **Proposed Procedure**: Update both journeys to `CAP-DLV-proposal-planning` as `SPEC-git-operator-result-readiness`
  changed it: the composed handoff's one commit and `commit=`, the refused-commit stop and its in-place fix, the
  link fixes as a later Host commit after the composed handoff, and the take-base-then-`devkit rules fix` resolution
  of a sibling conflict.
- **Expected Benefit**: A handbook reader no longer commits the handoff transaction by hand or reruns a stopped
  handoff.
- **Cost & Risk**: Two localized pages; `ADR-localized-handbook-language-exception` keeps the Korean page.
- **Attempted**: Not attempted: `handbook/` is outside the write scope of this Development unit; the nested
  reconcile review reported the gap.

## Diagnostic Details

- **Reproduction**: Compare the handbook journey's handoff section and error table with `CAP-DLV-proposal-planning`
  (Host-authorized proposal lifecycle CLI) on `dev-git-operator-result-readiness`.
- **Expected / Actual**: Expected the journey to match the capability; it describes the earlier write-only composed
  handoff.
- **Versions**: `dev-git-operator-result-readiness` at the reconcile commit.
- **Conditions**: Development worker write scope excludes `handbook/`.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-DLV-proposal-planning`, `UC-plan-and-hand-off-a-proposal`,
  `ADR-composed-handoff-commits-its-own-transaction`.

## Evidence

```text
handbook/en/journeys/incubate-and-hand-off-a-proposal.md: "fixes any unresolved link in the same change"
error table: no SPEC_HANDOFF_COMMIT_REFUSED row (the same in handbook/ko/)
```

## Disposition

Dismissed by the user: the release handbook is refreshed only when a release requests it, and that refresh finds
stale pages itself (`just handbook status`, `HANDBOOK_STALE`). Development does not track handbook drift.
