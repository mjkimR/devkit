---
reconcile_id: REC-milestone-archive
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-archive-terminal-milestones-in-roadmap.md
    resolution: modified
  - file: docs/roadmap/_archive/MS-backlog-subagent-roles.md
    resolution: modified
  - file: docs/roadmap/_archive/MS-idea-incubation.md
    resolution: modified
  - file: docs/roadmap/_archive/MS-maintenance-operations.md
    resolution: modified
  - file: docs/roadmap/_archive/MS-ux-documentation.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: waived
    rationale: "Existing identity, alias, reference and status-derived history procedures are path-independent; archived integration fixtures verify the same contract without new flags or steps."
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: waived
    rationale: "Existing identity, alias, reference and status-derived history procedures are path-independent; archived integration fixtures verify the same contract without new flags or steps."
  - file: docs/usecases/documents/UC-find-the-right-documents.md
    resolution: waived
    rationale: "Existing identity, alias, reference and status-derived history procedures are path-independent; archived integration fixtures verify the same contract without new flags or steps."
  - file: docs/usecases/governance/UC-keep-the-living-spec-consistent.md
    resolution: waived
    rationale: "Existing identity, alias, reference and status-derived history procedures are path-independent; archived integration fixtures verify the same contract without new flags or steps."
---

# Reconciliation: `SPEC-milestone-archive`

The document model and validation own the two canonical status/location pairs without moving files automatically.
Proposal membership reuses the public document predicate, preserves canonical aliases and the inactive notice.
Viewer selective readers include the reserved archive in optimized and generic sources, post-load counts and roadmap
readiness; detail/deep links retain paths. Guidance combines existing close/drop/reopen authority with movement and
preserves historical merge aliases. The four approved history files changed paths only; manifest bytes match.

No new package, architectural layer, user screen or registered domain concept was introduced. No further required
work or linked source feedback remains. The consumer smoke expected-catalog repair is the Host-approved exact
`tests/e2e/smoke.sh` scope extension, preserving default opt-in absence and every smoke stage.

## Entrypoints

Keep the existing document/governance/viewer package doorways and proposal/guidance entrypoints. Reject helper
models, tests, templates, README files, generated assets and relocation paths as new entrypoints.

## Verification

Reader baseline/outcomes, exact relocation and labelled semantic Git exercises are retained in
`docs/materials/2026-10/20261028-milestone-archive/delivery-evidence.md`.
Independent code review and reconciliation verification run against the committed final content.
