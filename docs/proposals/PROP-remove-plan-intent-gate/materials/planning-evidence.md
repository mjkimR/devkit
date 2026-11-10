# Remove plan-intent: Planning evidence

Source baseline: `4a6223361b6a60171be665db598b4a81b277d38f`.

## Scope inventory

All six files under `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/` declare the gate,
including `sdd-overall-refactor.md:9,21`. The original draft's exception was incorrect.
The same source bundle's `AGENTS.md.jinja` is its constitution and guidance source.
Four English handbook pages describe the gate and need reconciliation: `handbook/en/concepts.md`,
`handbook/en/areas/delivery.md`, `handbook/en/journeys/route-development-intent.md` and
`handbook/en/journeys/plan-and-hand-off-a-proposal.md`.

## Compatibility evidence

- `packages/devkit/src/devkit_agt/features/workflow/repositories/unit/decisions.py:103-112,150-168` validates
  generic request shape and loads numbered decisions without requiring membership in the current workflow's gates.
- `packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py:87-90,410-417` scopes decisions to the
  segment and reports malformed records. Static inspection supports retaining valid old records; a runtime
  regression remains required in Development.
- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py:900-969` selects named carried gates
  and creates an audit-only decision for gates absent from the spec. Keep acceptance carry; stop intent selection.
- `packages/devkit-spec/src/devkit_spec/features/policy/usecases/inspect.py:28-42` reports arbitrary configured
  gates, so deleting `INTENT_GATE` alone would still report a configured retired key as active. Explicitly treat the
  retired key as ignored using the existing warning, while preserving custom gate behavior.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/depth-and-close.md:10-15` stores
  escalation rationale in the gate note. Move that rationale into `spec.md` without a replacement record.

## Alternatives and retained direction

| Option | Cost | Risk | Recommendation |
| --- | --- | --- | --- |
| Keep gate | Records and special cases remain | No simplification | Reject |
| Default auto | Declarations, config and carry remain | Policy delegation confused with task authorization | Reject |
| Remove gate, retain stage IDs | Update adapters, tests, guidance and contracts | Agent instruction still enforces authorization | Retain |

Stage IDs preserve historical envelope attribution and return targets. Gate removal is complete across all six
workflows; generic workflow-engine changes, historical record migration and new feature edges remain excluded.
No performance or timing improvement is claimed. The acceptance checks compare observable behavior, not counts.
