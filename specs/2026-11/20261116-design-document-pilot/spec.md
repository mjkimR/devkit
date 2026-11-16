---
id: SPEC-design-document-pilot
title: Early content pilot for domain, design and operations
summary: "Tests domain, design and operations ownership on distribution examples without changing contracts or tooling."
status: in-progress
created: 2026-11-16
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-design-document-pilot] Early content pilot for domain, design and operations

## Problem and user stories

Handed off from PROP-design-document-pilot. Preserved materials live under
`docs/materials/2026-11/20261116-design-document-pilot/`.
`PROP-design-document-pilot-target` bounds the retained evaluation artifacts.

- US-1: A reader needs a conceptual relationship view of bundle availability, selection, projected paths and receipt.
- US-2: An implementer needs to locate the journaled file/directory replacement mechanism and one readable detail.
- US-3: An operator needs to classify interrupted sync symptoms and find the existing recovery and readiness owners.
- US-4: Foundation Planning needs observed navigation, ownership and maintenance evidence before representation decisions.

Domain is conceptual input, not downstream of design. Each entry explains its overview and next step independently.
Concise summaries are non-normative; source contracts retain unique authority. No rigid authoring DAG, whole-layer
prerequisite, all-pairs links, manual reciprocal links or arbitrary hop cap is introduced.

## Non-goals

**Scope Excluded**: production code, new indexed kind/ID, final documentation homes, UI, templates, rules,
agent assets, new feature edges, normative transfer and executable recovery. No product screens change.
Existing capability, architecture, glossary and reference owners remain unchanged. No recovery command uses this
repository as a fixture. No Athena material is needed beyond the preserved Planning lessons.

## Acceptance Criteria

### [AC-01] Role contributions and unique ownership (carried AC-PILOT-01)

- **Given** existing distribution contracts, architecture, glossary and implementation at the recorded revision,
- **When** three role entries and one design detail are composed,
- **Then** each explains purpose, existing sources and added value, and a passage ledger compares before/after
  authority with zero selected transfers and zero repeated normative owners.

### [AC-02] Bounded independent navigation (carried AC-PILOT-02)

- **Given** the exact starting inputs in the preserved example-selection protocol,
- **When** an independent reader attempts domain concept-to-contract, contract-only design discovery,
  supplied-entry design-to-detail-to-source and four operations documented-state scenarios,
- **Then** evidence records reader, revision, every opened document with necessity, final authority/section,
  failures, unnecessary returns, prerequisite reading and entry overview/next-step clarity.
  Contract-only discovery and supplied-entry success have separate outcomes. Operations identifies pending,
  later-edited and legacy-journal stop conditions plus the readiness owner: sync --check exit 0 is ready,
  exits 1 and 2 are not ready; no journal with desired-state drift remains not ready.
  Lexical search, resolve/refs and relative-link checks separately measure existing facilities without claiming
  unindexed draft discovery, package-context validation or viewer validation.

### [AC-03] Change-specific maintenance (carried AC-PILOT-03)

- **Given** unchanged runtime safety guarantees,
- **When** deletion ordering and a recovery stop condition are changed counterfactually,
- **Then** evidence identifies each affected owner and source symbol, and explains which layers stay unchanged
  when their facts remain true; neither hypothetical change is executed.

### [AC-04] Evidence and representation decisions (carried AC-PILOT-04)

- **Given** the retained drafts, source ledger and actual reader observations,
- **When** recommendations are delivered to `PROP-design-document-foundation`,
- **Then** each role has separate content-location, indexed kind/ID and tooling/UI recommendations with supporting
  evidence, minimal missing behavior, limits and existing support that works. Facts, hypotheses and unverified
  claims are distinguished; existing later proposal owners retain deferred scope.

## Assumptions and baseline

The accepted selection still matches the current transaction source and capability; no normative transfer is needed.
`ARCH-06-runtime-view` supplies system interaction context, not file/directory algorithm detail.
Its diagram places journal recording inside a write loop; this pilot treats that ordering as a coarse-view ambiguity
and uses the explicit write-ahead owner in `CAP-DIST-sync-and-transactions` §3 and source for mechanism claims.
The pilot records this limitation without modifying architecture.

Baseline: 3d21622a44ccb9fdf1388a33b360bf39c71a79a1 with the pilot drafts absent. Development measures existing
facilities and subsequent supplied-entry paths separately. No elapsed-time or corpus-size improvement is claimed.
