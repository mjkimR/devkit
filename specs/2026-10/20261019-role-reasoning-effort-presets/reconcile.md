---
reconcile_id: REC-role-reasoning-effort-presets
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-role-effort-presets.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
    resolution: waived
    rationale: "Its role contract format already lists effort among the claude-code keys and model_reasoning_effort among the codex keys, and the allowlist code is unchanged; the presets are spec bundle content that this capability renders without interpreting."
---

# Reconcile: `SPEC-role-reasoning-effort-presets`

## Reflected

- `CAP-DLV-delivery-workflows`
  - Section 2: the model-selection non-goal keeps the model with the runtime and states that role contracts preset
    only a model-independent reasoning effort per role, independent of `activity-effort` (AC-06).
  - Section 4.6: a paragraph names the preset keys (`effort` under `claude-code`, `model_reasoning_effort` under a
    `codex` block that is not `unsupported`), the profile-to-value mapping of the four read-only roles, the unset
    workers and Antigravity, the values allowed (`low`, `medium`, `high`), the precedence on each host, that a role
    the main session runs itself uses the session's effort, and the drift test; the role table gains a "Reasoning
    effort" column (`high`, `medium`, or session for the workers) (AC-06).
- `ADR-role-effort-presets`: promoted from the proposal's PADR by the handoff commit on this branch; its decision is
  what the contracts, the test and the capability now state. No edit in this unit.

## No impact

- `CAP-DIST-agent-projections`: waived above; both keys were already allowlisted and documented.
- `docs/architecture/`: no module, layer or projection change.
- The `spec` skill's `references/effort.md` already states that model and reasoning settings are outside the
  `activity-effort` axis, which the presets keep.

## Deferred work

None retained. Values above `high` and an Antigravity key are non-goals with reconsider triggers in `spec.md`, not
retained work. The proposal's open feedback `FB-envelope-answer-help-item-keys` was carried into this bundle and
stays open for hygiene.
