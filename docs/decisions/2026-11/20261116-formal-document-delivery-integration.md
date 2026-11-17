---
id: ADR-formal-document-delivery-integration
title: Consume formal documentation policy at delivery boundaries
summary: "For formal document maintenance across delivery approaches, we consume shared document policy at existing delivery boundaries, to preserve complete impact coverage and ownership, accepting explicit per-change semantic review."
proposal: SPEC-design-document-lifecycle
status: accepted
created_at: 2026-11-16
---

# [ADR-formal-document-delivery-integration] Consume formal documentation policy at delivery boundaries

## 1. Context & Problem Statement

Formal design, domain and operations require complete downstream authoring and maintenance support. Existing SDD
and adaptive procedures omit these roles, while the docs core owns their shared identity and ownership semantics.
Copying role schemas into delivery guidance would create competing authorities; a runtime presence registry would
not establish semantic source agreement.

## 2. Decision Drivers

- Complete affected-document coverage for all three formal kinds.
- One shared identity, ownership and entrypoint policy.
- Existing delivery authority and records, including adaptive neutrality.
- Source-specific verification, useful detail and no forced unaffected-layer edits.

## 3. Considered Options

1. Extend existing delivery boundaries and consume core policy; explicit semantic review remains necessary.
2. Share a delivery-specific checklist across spec/adaptive; reduces repetition but couples private assets or
   imposes delivery process on neutral docs guidance.
3. Add a runtime impact manifest; mechanically checks presence but adds a second registry and cannot prove source
   agreement. All options retain mandatory first-class kinds.

## 4. Decision Outcome

Option 1 is selected for ownership consistency and existing authority with complete downstream coverage.

- Planning and review assess every formal responsibility for the actual change, recording affected IDs/actions
  and source evidence or a bounded unaffected reason. → `CAP-DLV-proposal-planning` formal impact rules (MUST).
- SDD reconciliation compares affected formal statements and identity/reference/detail/artifact maintenance with
  retained source through existing records. → `CAP-DLV-delivery-workflows` rule 9 reflection and rule 15 coverage (MUST).
- Delivery entrypoint derivation consumes the docs core's applicable-kind and path policy, with role-appropriate
  source review. → `CAP-TRACE-code-entrypoints` derivation and review rules (MUST).
- Adaptive authoring uses the same core formal ownership and maintenance contract without implicit SDD Units,
  envelopes, gates or immutable iteration history. → `CAP-DLV-adaptive-development` project documents rules (MUST).
- Baseline adoption treats required formal-document or source-evidence gaps as retained coverage gaps.
  → `CAP-DLV-sdd-baseline-adoption` retained coverage rules (MUST).

The core decision replaces ID-free standing. This decision does not duplicate its supersession or alter approval,
execution permissions, recovery ownership or neutral document formats.

## 5. Consequences

Existing runtime joins and targets can be reused when per-kind tests prove their behavior. Semantic impact and
source agreement remain explicit author/reviewer obligations; string-presence or path checks alone do not establish
them. The delivered core interface is consumed through its public policy; changed source invalidates affected comparisons.

## 6. Confirmation

`SPEC-design-document-lifecycle` names source and current-contract owners. `docs/materials/2026-11/20261116-design-document-lifecycle/integration-contract.md` §5 maps L1–L4 to
scaffold, entrypoint, bundle, installed-consumer and scripted lifecycle scenarios. Semantic owner/source agreement
is Review only with source-identified comparisons; actual document/reference checks supplement it.

The lifecycle verification executes actual per-kind global/registered-root procedures under SDD and adaptive,
including composed artifact rename/root moves, one-parent split/transfer and real source-deletion retirement.
SDD tests exercise generated formal impact and DESIGN derive/select/apply; adaptive retains its approach and prior
SDD history. Semantic owner/source comparison remains separate review evidence, not an inferred runtime guarantee.
