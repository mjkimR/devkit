---
id: PADR-retain-research-as-cited-materials
title: Retain research as indexed materials cited by ID
summary: For research that may inform several proposals or an adaptive product, we retain each investigation as an indexed material under docs/materials/ owned by no proposal and cited by its MAT ID, accepting that consumers follow a citation instead of a copy.
proposal: PROP-deep-research-bundle
status: draft
created_at: 2026-10-30
---

# [PADR-retain-research-as-cited-materials] Retain research as indexed materials cited by ID

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

One broad investigation can inform several proposals at once, or an adaptive product and a later SDD proposal.
A proposal's own `materials/` moves into `docs/materials/` at its handoff, so research placed there belongs to
one proposal. The research entry also records resume facts in `.devkit/incubation.md`, which an SDD project does
not keep.

An indexed material needs only a frontmatter `id` (`CAP-DOCS-document-model`); a backticked `MAT-<slug>` in
prose is a reference edge that `RULE-document-reference` resolves, and handoff rewrites only IDs it wrote, so a
cited MAT ID survives handoff unchanged.

## 2. Decision Drivers

- One retained investigation serves several consumers without a copy.
- Consumers under either approach cite it the same way.
- An interrupted investigation can resume without an approach-specific file.
- No new document kind, relation field or check.

## 3. Considered Options

- **Copy into each proposal's `materials/`**: self-contained proposals; duplicated evidence that drifts.
- **One indexed material per investigation, cited by ID**: one source; a consumer follows a citation.
- **A new research document kind with a relation field**: checked links; a document-model change no failure
  requires.

## 4. Decision Outcome

Chosen: one indexed material per investigation, cited by ID.

- A retained investigation is the directory `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` with an index document
  `<YYYYMMDD>-<slug>.md` carrying `id: MAT-<slug>`, `created_at` and H1 `# [MAT-<slug>] <title>`. The index links
  the run's other notes by relative path; a note carries its own `MAT-` ID only when a consumer cites it alone.
- The index holds the logical contents (brief, alternatives, direction, conditional roadmap) or links them, plus a
  `Status` line (`complete` or `partial`), open questions and the next investigation.
- An SDD proposal, spec or ADR cites the index ID in a code span and never copies or moves the material into its
  own `materials/`. Adaptive current context links the same ID.
- A later investigation that builds on a complete material creates a new material citing it. Only a resumed run of
  the same investigation updates a `partial` index in place.
- The transient run brief holds in-flight state until a result is retained; nothing else replaces
  `.devkit/incubation.md` for research.
- The entry writes these files and reports their paths; committing them follows the project's ordinary Git flow.

## 5. Consequences

- Positive: one investigation is cited by several proposals; handoff leaves it in place.
- Negative: a reviewer of a proposal reads the cited material separately; the proposal report does not include it.
- Risk: a material cited only in bare text is not a reference edge; the spec guidance line asks for a code span.

## 6. Confirmation

`RULE-document-reference` resolves backticked MAT citations in proposals, specs and ADRs. The spec skill's
proposal reference states the citation rule. The layout and index fields are review only, as for every material
(`RULE-spec-format` skips `materials/`).
