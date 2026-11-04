---
id: PROP-worker-scope-extension-target
title: Worker extension contract targets
summary: "Contract targets for recorded adjacent-path extensions, typed worker evidence and compatible optional inspection."
status: draft
created_at: 2026-11-04
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-orchestration-workers.md
    resolution: modified
---

# [PROP-worker-scope-extension-target] Worker extension contract targets

- `CAP-DLV-delivery-workflows`: tiered admission, pre-final annotation review, final record verification,
  additive inspection evidence and explicit-scope compatibility.
- `CAP-DLV-workflow-envelopes`: optional typed worker list and its authoring flag, validation and compatibility.
- `ADR-orchestration-workers`: only the partial-supersession annotation introduced by promoting
  `PADR-recorded-adjacent-path-extensions-for-development-workers` at handoff; do not rewrite its remaining decisions.

The promoted ADR restates its new clauses through the two capability IDs. No UI or Screens draft is needed.
