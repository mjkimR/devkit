---
reconcile_id: REC-remove-integration-ui-action
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
---

# Reconcile: `SPEC-remove-integration-ui-action`

- `CAP-INT-mcp-services` now states that integration JSON carries `authority` (`none` from `prepare`, else `policy`
  or `host-conversation`). It never listed `ui_action`, so no removal text was needed there.
- No delivery capability, use case or `docs/development/reference/` page names `ui_action` or lists the fields of the
  `integration` object embedded in the `spec proposal accept` result; they need no change. `CAP-DLV-proposal-lifecycle`
  describes that result without listing the embedded object's keys.
- Entrypoint candidates from `derive` were test paths only and were rejected.
- Historical records under `docs/materials/` that quote `ui_action` stay unchanged (Non-Goal 2).
- Entrypoints: `CAP-INT-mcp-services` already lists `packages/devkit/src/devkit_agt/features/integration/`; nothing
  to add.
- Deferred work and source feedback: none. The source finding AO-05b is a materials report entry, not a feedback
  document, so nothing is retired.
