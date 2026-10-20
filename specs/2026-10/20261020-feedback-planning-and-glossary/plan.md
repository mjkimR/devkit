---
id: PLAN-feedback-planning-and-glossary
spec: SPEC-feedback-planning-and-glossary
---

# Technical Plan: `SPEC-feedback-planning-and-glossary`

## Constitution and invariant review

No conflicting invariants or ADR changes. Preserve the draft/no-Planning-branch guard in
`CAP-DLV-proposal-incubation` and ID-free glossary exclusion in `CAP-DOCS-document-model`.
Extend `CAP-GOV-spec-rules` narrowly; new reference validation is an agreed capability extension.

## Architecture and impact

- Decomposition passes operation context to the existing Backlog guard; only its recovery advice changes.
- DocumentReferenceRule reads the root glossary through the existing workspace cache, scans visible Markdown lines
  for the five-column header/separator and Owner cells, and resolves references with the existing index.
- Existing indexed-document parsing, reference graph and autofix stay unchanged. No dependencies or schema changes.
- Planning and Backlog instructions own the two halves of return recovery. The Host owns branch integration and
  removal under existing approval policy; worker guidance does not grant those Git actions.

## Edge cases and verification

Test local/fetched branches, non-draft parents, no mutation, normal editable drafts and unchanged generic guard advice.
Test missing/duplicate/valid/multiple Owner IDs, escaped pipes, prose and other columns, code/comment exclusions,
legacy tables, repeated tables, targeting, snapshot cache behavior and no glossary autofix/index inclusion.
Run spec lint/type checks, affected tests, staged/cumulative rules and independent medium code and reconcile reviews.
Host performs final sync; emulated worker boundaries are enforced by explicit absolute cwd, scoped writes and
Host validation of the committed range, not by native per-worker confinement.
