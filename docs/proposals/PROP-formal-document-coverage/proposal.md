---
id: PROP-formal-document-coverage
title: Formal document coverage across capability areas
summary: Adds DESIGN, DOMAIN and OPS documents written from the current code and Living Spec for each capability area whose readers have a question no existing owner answers, using the delivered formal templates.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/designs/
    - docs/domain/
    - docs/operations/
    - docs/proposals/PROP-formal-document-coverage/
  excludes:
    - packages/
    - docs/capabilities/
    - docs/architecture/
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-formal-document-coverage] Formal document coverage across capability areas

## 1. Background & Hypothesis

The formal kinds (DESIGN, DOMAIN, OPS), their area-scoped paths (`ADR-area-scoped-design-bundles`) and their
templates and writing instructions (`ADR-problem-first-formal-document-openings`) are delivered. Five formal
documents exist, all in the distribution and delivery areas: `DESIGN-distribution-file-directory-replacement`,
`DESIGN-distribution-transactions`, `DOMAIN-bundle-selection-and-installation`, `DOMAIN-delivery-relationships` and
`OPS-distribution-sync`. The Living Spec has 18 capability areas under `docs/capabilities/`; the other areas have no
implementation explanation, conceptual model or operations routing beyond capabilities, architecture and reference.

`CAP-DOCS-documentation-ownership` §3.3 asks for one reader question per formal document and to drop a document that
has none, so coverage is not one document per kind per area.

Hypothesis: an inventory of reader questions per area, answered from the current code and Living Spec, yields a
bounded set of formal documents that agents and maintainers use instead of reading source to recover mechanisms,
concept distinctions and symptom routing.

## 2. Technical Spike Questions

- **Q1**: Which areas have a reader question that only a DESIGN (local mechanism), DOMAIN (concepts readers
  confuse) or OPS (symptom → owner routing) document answers, and which existing owner already answers the rest?
- **Q2**: How should the work split into Development units (by area group, disjoint `docs/` paths) so workers run in
  parallel, and is any unit XL?

## 3. Proposed Design & Impact

Documentation only. Each new document follows its kind's delivered template and writing instruction, states its
authority boundary by full ID and moves no normative statement out of its current owner (§3.1). No code, capability,
architecture or ADR changes; a gap found in those is recorded as feedback.

## 4. Lifecycle & Retirement Criteria

Retired when the accepted inventory's documents are delivered by the handed-off spec units.
