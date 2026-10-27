---
reconcile_id: REC-seeded-paths-in-boundaries
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconcile: `SPEC-seeded-paths-in-boundaries`

- `CAP-DLV-delivery-workflows`: the delegated bundle-source sentence now states the admitted class of sync outputs,
  the `sync_start` check, the `(sync output)` record and the Host's receipt check, citing
  `ADR-admit-change-sync-outputs` (AC-04). The ADR was written in Planning and is unchanged.
- No use case, architecture document or glossary term changes: the change is wording in the `spec` bundle's
  delegation text and introduces no domain term (`sync_start` and `(sync output)` are record labels the bundle text
  defines).
- Entrypoints: no candidate is applied; the bundle text files are not doorway files for `CAP-DLV-delivery-workflows`.
- Deferred work: none.
- Source feedback: `FB-new-seed-sync-output-outside-boundaries` is `promoted`, a terminal status; it needs no
  disposition and is left unchanged.
