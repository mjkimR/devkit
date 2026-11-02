---
reconcile_id: REC-retire-stale-integration-clauses
status: pending
targets:
  - file: docs/decisions/2026-10/20261022-configuration-language-and-rendering.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-local-and-pull-request-integration.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-retire-stale-integration-approval-clauses.md
    resolution: modified
---

# Reconcile: `SPEC-retire-stale-integration-clauses`

- `ADR-retire-stale-integration-approval-clauses` retires the following clauses:
  - the pre-confirmation `--auto`/`--admin` refusal of `ADR-local-and-pull-request-integration`;
  - the confirmation-form text rules and "native approval routes" of `ADR-configuration-language-and-rendering`.

  Both earlier ADRs stay `accepted`, with "Superseded in part by" lines under their headings and at the affected items.
- Capabilities are unchanged:
  - `CAP-INT-mcp-services` already states the current refusal points and the ban on enqueue, auto-merge and admin-merge.
  - `CAP-DIST-sync-and-transactions` already states the domain-owned English and Korean copy.
  - No capability stated the retired form rules.
- Agent-facing text now matches the retirement:
  - the local render of the spec skill's routing row and of the completion reference say "integration approval";
  - the help of `devkit-mcp` drops "native approval".

## Source feedback

- `FB-pr-auto-admin-refusal-point`: `resolved` (Disposition names this spec).
- `FB-stale-approval-form-clause`: `resolved`.
- `FB-bundle-text-bare-devkit-commands`: `dismissed` by user decision.

## Entrypoints

No capability or use case entrypoint changes; the code edit is a help docstring.
