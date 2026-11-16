---
id: PADR-linked-symptom-led-operations
title: Linked symptom-led operations entries
summary: "For operational symptom classification, we keep linked ID-free operations entries with existing action owners, to preserve useful diagnosis routing without new identity, accepting owner-linked discovery."
proposal: PROP-operations-documents
status: draft
created_at: 2026-11-16
---

# [PADR-linked-symptom-led-operations] Linked symptom-led operations entries

## 1. Context & Problem Statement

`CAP-DOCS-documentation-ownership` retains operations as a distinct role but defers its home. The pilot's supplied
entry helps classify four sync states. Unsupplied operational discovery is unverified. Clean separation from
existing recovery guarantees, actions, syntax, procedures and architecture is the primary constraint.

## 2. Decision Drivers

- Preserve unique authority and existing execution permissions.
- Give symptom-specific overview, evidence selection and a next useful owner.
- Choose home, indexed identity and tooling independently from demonstrated needs.
- Verify global/package entry paths before claiming discovery support.

## 3. Considered Options

- A: ID-free `docs/operations/` entries with selected owner links. Separate responsibility with small maintained
  scope; needs ordinary-link review and withheld-entry trials. Recommended.
- B: Embed the classification map in the existing distribution reference. Viable for one small scenario and no
  runtime; mixes operational composition with syntax/error reference ownership and weakens a distinct maintained home.
- C: New indexed operations Kind. Supports direct indexed identity but adds model/placement and consumer surface;
  no required result has demonstrated that selected owner links cannot satisfy it.

## 4. Decision Outcome

Choose A, conditional on successful O1–O5 Development evidence. This decision meets PADR admission because it
compares viable alternatives and adds a lasting representation convention across document responsibilities.

- Operations compositions use ID-free `docs/operations/<slug>.md`, or analogous `operations/` in a registered
  package docs root, with question, overview, authority boundary and next useful action.
  → `CAP-DOCS-documentation-ownership` Operations entries (planned SHOULD).
- Selected existing owners link to entries for their operational question; entries cite indexed owners by full ID
  and ordinary paths for ID-free content without borrowing indexed identity.
  → `CAP-DOCS-documentation-ownership` Operations entries (planned SHOULD/MUST).
- Recovery guarantees, compatibility, stop/readiness criteria, actual advisory actions and executable steps retain
  their existing owners; no statement transfer is selected.
  → `CAP-DOCS-documentation-ownership` §3.1 Operational authority (MUST).
- No new Kind, runtime, executor, registry, permission or viewer support is selected. Failed required discovery is
  corrected within selected content/link scope or returned to the Host for scope review.

`ADR-documentation-ownership-and-linked-design-entries` remains in force: this decision settles its deferred
operations home without replacing its design representation or shared ownership clauses. No accepted ADR is
superseded, wholly or partially.

## 5. Consequences

One maintained operations entry has selected capability/reference ingress links. Existing action owners need no
procedure migration. ID-free entries are not returned by document search/resolve/refs; semantic and ordinary-link
integrity need review. Package convention is checked in a disposable fixture; no unneeded maintained example is
seeded. Required direct indexed discovery that cannot be met by selected owner links triggers a later scope decision.

## 6. Confirmation

Review only for semantic ownership and navigation. Execute proposal O1–O5 with withheld-entry global/package
readers, four documented classifications, journal-compatibility paper review and generic source distribution.
Scoped document/source asset rules cover applicable contracts, not ID-free ordinary links or semantic completeness.
