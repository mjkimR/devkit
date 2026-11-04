---
id: MS-monorepo-namespace-support
title: Namespace roadmap, steering and cross-domain UX guidance
summary: "Supports registered namespaces' roadmap and steering directories and domain-neutral UX writing under shared document rules, with UX rule changes reconsidered only on concrete mismatch evidence."
status: done
created_at: 2026-11-04
depends_on: []
---

# [MS-monorepo-namespace-support] Namespace roadmap, steering and cross-domain UX guidance

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification) and §2 (Bounded
Context) through `CAP-DOCS-namespaces`: registered namespaces own their roadmap and steering context while retaining
repository-wide document identity, references and traceability. `ADR-namespace-milestone-roots` and
`ADR-namespace-steering-directories` define those boundaries. Interfaces beyond pages and forms use domain-neutral
writing guidance under the shared UX rules rather than a namespace opt-out, following
`ADR-reject-ux-rules-path-exclusion`. A concrete document mismatch is the evidence for reconsidering UX rule changes.

## Exit condition

- A registered namespace owns milestones under its docs root with the global milestone lifecycle (placement,
  archive, closure, membership through direct proposals), and milestone discovery selects namespaces as `devkit docs
  list` does for the other kinds.
- A registered namespace owns steering documents under its docs root: the steering rule checks them as it checks the
  root directory, and an agent context lists the background of the namespace it works in beside the global list,
  within the bounded-context caps.
- Domain-neutral UX writing guidance covers surfaces beyond pages and forms while keeping both UX rules and the
  identity, reference and traceability rules enabled. A mismatch the guidance cannot resolve is recorded with the
  real document before a rule change is considered.
- Namespace outcomes are covered by rule and command tests and by `CAP-DOCS-namespaces` and `CAP-GOV-spec-rules`;
  `devkit rules check` accepts a monorepo fixture using both namespace roots. Guidance tests cover the surface
  criteria catalogued in `CAP-HARN-agent-guidance`.

## Non-goals

- **Scope Excluded**: namespaced IDs or per-package ID spaces (`CAP-DOCS-namespaces` keeps IDs repository-wide);
  per-namespace goals as ID-bearing documents (goals stay prose, in `ARCH-01-introduction-and-goals` or a namespace
  steering file); localized use case or UX headings (the document system writes documents in English); disabling the
  identity, reference or traceability rules for a namespace; external tracker or autohub synchronization of
  namespace roadmaps.
- **Scope Excluded**: Per-namespace UX rule opt-outs or relaxed UX contracts without a demonstrated document
  mismatch; `ADR-reject-ux-rules-path-exclusion` keeps reconsideration evidence-driven.
- **Scope Excluded**: Namespace UX object registers (`FB-namespace-ux-objects-copy`), package glossary relocation
  and namespace synonyms (`FB-package-glossary-asymmetry`), and viewer roadmap support
  (`FB-viewer-namespace-roadmap-roots`). These remain separately tracked follow-ups beyond this completed phase.

## Completion review

Decomposition: confirmed
Direct proposal work: confirmed
