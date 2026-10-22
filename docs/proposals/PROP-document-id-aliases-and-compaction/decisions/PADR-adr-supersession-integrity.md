---
id: PADR-adr-supersession-integrity
title: ADR supersession integrity
summary: "An ADR's supersedes (a list of ADR IDs) and superseded_by (one ADR ID) become checked provenance: a superseded ADR that still exists must say status superseded and name its successor in superseded_by, and devkit rules fix writes those reverse fields deterministically."
proposal: PROP-document-id-aliases-and-compaction
status: draft
created_at: 2026-10-22
---

# [PADR-adr-supersession-integrity] ADR supersession integrity

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

The ADR ledger records replacement through `supersedes` on the new ADR and `status: superseded` plus
`superseded_by` on the old one. Nothing checks these fields: `parse_document` skips `supersedes` on every document
that is not a Unit anchor, and `superseded_by` is not read at all. The ledger has drifted: five ADRs that a later ADR
supersedes still say `status: accepted`, and one `superseded_by` names an ADR that declares no `supersedes`
(`materials/ledger-evidence.md`, `envelopes/challenger-01.yaml` finding 1). An agent that filters ADRs by status
therefore reads replaced decisions as current, which is the context cost this proposal set out to reduce.

## 2. Decision Drivers

- The supersession fields are the ledger's only machine-readable statement of which decision is current.
- The existing rule infrastructure (`RULE-document-reference`, `services/rewrite.py`) already validates and rewrites
  frontmatter references deterministically.
- The check must hold whether or not old ADR files are later removed by compaction.

## 3. Considered Options

1. **Leave supersession unchecked** and rely on authors: the present state, which has already drifted.
2. **Check supersession as kind-aware provenance (chosen)**: on an ADR, `supersedes` is a list of `ADR-` IDs (a
   scalar is accepted as a one-element list) and `superseded_by` is one `ADR-` ID. Both stay provenance, outside the
   current reference graph.
3. **Derive status from `supersedes` alone** and drop `superseded_by`: fewer fields, but a reader of the old ADR
   would need an index query to learn it was replaced.

## 4. Decision Outcome

Option 2. `RULE-document-reference` (or a sibling spec rule chosen in Development) checks, for every targeted ADR:

- `supersedes` and `superseded_by` contain only full `ADR-` IDs and never the ADR's own ID.
- Each `supersedes` target that is still declared says `status: superseded` and names the superseding ADR in
  `superseded_by` (fixable: `devkit rules fix` writes both fields on the old ADR).
- A `superseded_by` target is declared and lists the ADR in its `supersedes` (not fixable: the successor's intent is
  not inferred).
- An undeclared `supersedes` target is allowed only as the compaction decision of this proposal defines it (an alias
  of the superseding ADR when deletion is chosen); otherwise it is an unresolved reference.

The Unit-anchor provenance (`supersedes` and `decomposed_from` as one `PROP-` ID) is unchanged.

## 5. Consequences

- The drifted records in `docs/decisions/` are corrected in the same Development, by the fix where it applies.
- `devkit spec list decision --status accepted` becomes a reliable view of current decisions.
- A partial replacement cannot be expressed with `supersedes`; it is written as a prose reference in the new ADR.
- Writing `status` and `superseded_by` on a replaced ADR is a metadata correction, consistent with the ledger's
  existing practice of setting `superseded_by` on replaced records; the decision text is not edited.
