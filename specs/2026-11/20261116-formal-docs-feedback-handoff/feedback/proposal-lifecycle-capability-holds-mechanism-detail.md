---
id: FB-proposal-lifecycle-capability-holds-mechanism-detail
title: "CAP-DLV-proposal-lifecycle §4.1 and §4.3 hold implementation mechanism that DESIGN-proposal-handoff now explains"
scope: repo
kind: suggestion
category: other
target: CAP-DLV-proposal-lifecycle
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-proposal-lifecycle-capability-holds-mechanism-detail] CAP-DLV-proposal-lifecycle §4.1 and §4.3 hold implementation mechanism that DESIGN-proposal-handoff now explains

Nature: document ownership placement between a capability and a formal design.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `CAP-DLV-proposal-lifecycle` §4.1 step 5 and §4.3 state the handoff mechanism at source
  level: per-leaf `lstat` checks of a materials merge, the order of move-backs, which link resolves from which
  directory, how a dropped record citation is formed and which spans count as directory-only. Much of it reads as an
  explanation of how the code works rather than as an observable contract. While writing `DESIGN-proposal-handoff`,
  that design had to cite the capability for the contract and the source for the order, with the two overlapping.
- **Proposed Procedure**: In a separate, explicitly scoped change, review §4.1 and §4.3 against
  `CAP-DOCS-documentation-ownership` §3.1 and §3.3: keep each observable guarantee (what is refused before writing,
  what is rolled back, which codes and output lines appear, which references change) in the capability, and move
  pure mechanism explanation (evaluation order, internal plan structures, helper behavior) into
  `DESIGN-proposal-handoff`, citing it from the capability.
- **Expected Benefit**: A shorter capability that agents read before a handoff; one owner for the mechanism.
- **Cost & Risk**: Moving text can drop a guarantee that tests rely on; each moved sentence needs a check that no
  test or rule cites it as a contract. `SPEC-formal-docs-feedback-handoff` was scoped to move nothing.
- **Attempted**: Hypothesis; no text was moved.

## Diagnostic Details

- **Reproduction**: Read `CAP-DLV-proposal-lifecycle` §4.1 step 5 (materials merge bullets) and §4.3 (code-span paths,
  dropped workflow record citations) next to `DESIGN-proposal-handoff`.
- **Expected / Actual**: Expected the capability to state guarantees and the design to explain mechanism; actual
  overlap in the materials merge and rewrite passes.
- **Versions**: devkit at the Development head of `SPEC-formal-docs-feedback-handoff`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: The design cites the capability sections instead of restating them.
- **Related Assets**: `CAP-DLV-proposal-lifecycle`, `DESIGN-proposal-handoff`, `CAP-DOCS-documentation-ownership`.

## Evidence

```text
CAP-DLV-proposal-lifecycle §4.1 step 5: "The directory and every existing directory on the way to a planned path MUST
be a real directory by `lstat`; ..." and five further merge bullets.
CAP-DLV-proposal-lifecycle §4.3: "Code-span paths (`kind=path`) ... Directory-only spans, including `materials/` and
paths resolving to relocated directories without a trailing slash, remain unchanged ..."
```

- **Disposition**: `SPEC-formal-doc-padding-trim`: `CAP-DLV-proposal-lifecycle` §4.1 step 5, the rollback paragraph and §4.3 now state outcomes only; the preflight pass, the rollback walk, the pass order and the link library moved to `DESIGN-proposal-handoff`, which cites §4.2 for the body classification. The merge bullets stay as observable guarantees that `ADR-proposal-handoff` confirms. Verified by the code review against `handoff.py`, `specs.py` and `relocation.py` and by `rg` showing no moved phrase left in the capability and no test reading it.
