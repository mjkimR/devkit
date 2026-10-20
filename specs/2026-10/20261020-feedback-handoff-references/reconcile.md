---
reconcile_id: REC-feedback-handoff-references
feature: SPEC-feedback-handoff-references
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/decisions/2026-10/20261020-reverify-closes-challenger-rounds.md
    resolution: modified
  - file: docs/decisions/2026-10/20261020-proposal-boundaries-name-existing-paths.md
    resolution: modified
---

# Reconciliation: `SPEC-feedback-handoff-references`

`CAP-DLV-proposal-incubation` describes directory span preservation, verified Git-pinned record citations,
unchanged record deletion and the unresolved fallback. No new public commands, document kinds or domain terms
are introduced. Existing capability entrypoints already cover the proposal package.

The two accepted ADRs receive only the explicitly authorized historical answer citations. Their decisions and
status do not change; the pinned record contains both question IDs. No policy exception is generalized.

## Source feedback dispositions

- `FB-handoff-rewrites-generic-materials-span`: resolved by preserving directory-only spans while concrete material
  references keep relocating; reproduced and verified by the handoff regression.
- `FB-promoted-adr-cites-deleted-proposal-envelope`: resolved by byte-verified historical pins, unavailable-history
  reporting, and the two citation corrections; the committed source and both question IDs were verified.

Independent code review passed. Both explicit sources were addressed directly, without promotion; no terminal
feedback was changed. There is no deferred work within the authorized scope.
