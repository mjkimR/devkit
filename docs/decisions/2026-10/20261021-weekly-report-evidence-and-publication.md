---
id: ADR-weekly-report-evidence-and-publication
title: Revision-bound reports and independent publication
summary: Weekly reports preserve revision-bound evidence in immutable local artifacts, with publication authority and outcome recorded independently.
proposal: SPEC-weekly-report
status: accepted
created_at: 2026-10-21
---

# [ADR-weekly-report-evidence-and-publication] Revision-bound reports and independent publication

- **Status**: Accepted
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`MS-reporting-and-actionable-insights` needs a manually useful report before a scheduler or durable history
backend exists. Commits, accepted proposals and current check results alone cannot prove weekly delivery or
resolution. An external publication can fail independently from successful evidence collection.

## 2. Decision Drivers

- Preserve source revision, observation interval and limitations behind each claim.
- Keep generation useful without maintenance sweeps, external accounts or publication authority.
- Make retries and same-period reruns distinguishable without a new runtime or database.
- Fit the independently invocable maintenance playbooks in `SPEC-periodic-drift-reconciliation`.

## 3. Considered Options

1. Replace one report per calendar week and embed its mutable publication result. This is simple to locate but
   destroys earlier evidence and changes the report after publication, making ambiguous retries harder to verify.
2. Generate immutable run-specific local reports and keep publication outcomes in a companion record. This keeps
   the evidence stable, supports same-period reruns and requires only ordinary files and existing connectors.
3. Deliver a history backend and automatic maintenance sweeps with reporting. This creates dependencies and
   external mutations beyond the manual reporting milestone; `MS-maintenance-history` already owns storage.

## 4. Decision Outcome

Select option 2. A logical report key consists of repository, scope and exact interval/timezone; each generation
gets a unique run ID and inspected revision. New content means a new run. Default to the previous complete local
Monday-to-Monday week, allowing explicit endpoints and requiring a timezone if none is configured.

Committed evidence is the default. Working-tree observations, optional dirty-state evidence, and events whose
integration date cannot be proved stay explicitly qualified. A completed-work claim requires verification and
integration evidence in addition to a status or commit. Missing maintenance evidence is not a clean result.

Generate first and verify the local artifact. Publish only to an explicitly selected and authorized destination
using an existing tool. Record destination, authority, artifact digest and verified receipt separately. Unknown
publication outcomes require checking the destination before retrying; an unverifiable outcome remains unknown.

The selected direction is preliminary until the proposal direction gate. It creates no standing publication
permission. Artifact location and any external destination are invocation inputs, not fixed organization policy.

## 5. Consequences

Reports can be inspected without external setup and retain prior evidence across reruns. Several reports may
cover one interval, so each names its identity and supersession relationship. Publication records can change
without changing the report digest. Readers must check scope, revision and limitations before comparing runs.

The playbook remains content-only; manual scenario evidence supplements package and governance tests. The
maintenance bundle can be initialized with reporting alone when absent; existing companion assets are preserved
when present. The Host serializes overlapping catalog writes. The future history backend remains independent.
