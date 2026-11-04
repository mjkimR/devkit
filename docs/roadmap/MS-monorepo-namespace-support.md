---
id: MS-monorepo-namespace-support
title: Namespace-complete monorepo support
summary: "Lets a monorepo keep each registered namespace's roadmap and steering under docs/packages/<name>/ and tune the UX rules per namespace, so the global Living Spec stays readable when packages evolve on their own cadence."
status: planned
created_at: 2026-11-04
depends_on: []
---

# [MS-monorepo-namespace-support] Namespace-complete monorepo support

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification) and §2 (Bounded
Context) by completing `CAP-DOCS-namespaces`: today a registered namespace mirrors `docs/` for capabilities, use cases,
UX and architecture documents, while milestones and steering documents are global only and the document rules apply
one contract to every namespace. A monorepo whose packages are independent products (several games sharing one
engine, each with its own world setting, art direction and release cadence) needs its roadmap and its background per
namespace, and needs the rules written for web and app screens to be tunable where a package's domain does not fit
them. This reopens the deferrals `ADR-roadmap-and-milestones-ledger` (per-namespace roadmaps) and
`ADR-steering-documents` (a namespace steering copy) record, on the terms those decisions name.

## Exit condition

- A registered namespace owns milestones under its docs root with the global milestone lifecycle (placement,
  archive, closure, membership through direct proposals), and milestone discovery selects namespaces as `devkit docs
  list` does for the other kinds.
- A registered namespace owns steering documents under its docs root: the steering rule checks them as it checks the
  root directory, and an agent context lists the background of the namespace it works in beside the global list,
  within the bounded-context caps.
- A project can tune the UX document rules for a namespace whose domain the screen contract does not fit, without
  weakening the identity, reference and traceability rules on the same documents, and the tuning is visible in `devkit
  rules explain`.
- Each outcome is covered by rule tests and by the `CAP-DOCS-namespaces` and `CAP-GOV-spec-rules` contracts, and
  `devkit rules check` on a monorepo using all three reports no namespace-layout finding.

## Non-goals

- **Scope Excluded**: namespaced IDs or per-package ID spaces (`CAP-DOCS-namespaces` keeps IDs repository-wide);
  per-namespace goals as ID-bearing documents (goals stay prose, in `ARCH-01-introduction-and-goals` or a namespace
  steering file); localized use case or UX headings (the document system writes documents in English); disabling the
  identity, reference or traceability rules for a namespace; external tracker or autohub synchronization of
  namespace roadmaps.

## Completion review

Decomposition: pending
Direct proposal work: pending
