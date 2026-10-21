---
id: PLAN-unit-dependencies-and-milestone-scope
spec: SPEC-unit-dependencies-and-milestone-scope
---

# Technical Plan: `SPEC-unit-dependencies-and-milestone-scope`

## Constitution & Invariant Review
`ADR-separate-unit-prerequisites-from-milestone-themes` authorizes the change to `ADR-milestone-documents`. Preserve package layering and existing advisory families. No new runtime dependency, CLI or readiness service.

## Architecture & Components
Extend documents/parse.py and shared dependency validation for typed anchor targets and deterministic cycles. Use the full document index for resolution, with completed SPEC anchors terminal. Reuse that validation in proposals/handoff.py on an in-memory projected index before writes. Existing direct reference relocation preserves live incoming edges.
Remove milestone from direct spec creation and carried metadata, and restrict query/hygiene membership to PROP anchors. Update source templates and procedural Backlog/spec-next guidance for base-snapshot scheduling and lifecycle disposition. Reconcile affected document, governance, delivery and harness contracts.

## Choices and Premise Check
Current parser restricts depends_on to milestones; handoff uses indexed references and creates files only after target validation. These premises match the accepted direction. Share structural validation between rules and handoff to prevent drift; readiness remains a procedural recommendation. Existing completed-history indexing supplies target resolution. Cloud rendering renames overlapping guidance templates; the Host incorporates that base before guidance edits.

## Failure Modes
Refuse invalid projected graphs through ProposalInvalidError before any write. Keep existing rollback for later I/O failures. Reject collisions instead of treating them as projected replacements. No historical rewrites, migration layer or new completion claims.

## Verification
Parser/reference tests cover shapes, exact anchors, namespaces, history and filtered cycles. Isolated Git handoff tests cover carry/rewrite, invalid graph zero-write refusal and collisions. Membership/API/CLI and guidance tests cover AC-03 through AC-05, including base-versus-branch status evidence. Run module lint/types, just test-affected with its full fallback, cumulative rules, medium independent code review and reconcile verification.
