---
id: ADR-subagent-level-projection
title: Resolve subagent levels at distribution time with inherited defaults
summary: "For reusable roles across three hosts, we resolve opt-in model levels during distribution and inherit by default, to keep role prompts portable, accepting maintained host mappings and native inheritance limits."
spec: SPEC-subagent-model-levels
supersedes: ADR-role-effort-presets
status: accepted
created_at: 2026-10-25
---

# [ADR-subagent-level-projection] Resolve subagent levels at distribution time with inherited defaults

## 1. Context & Problem Statement

`CAP-DIST-agent-projections` already renders native model and effort fields. The spec roles have no model
family selection and pin some effort values. `ADR-orchestration-workers` records that effort policy while
leaving model selection outside delivery scope. Projects need portable opt-in levels and overrides without
replacing prompts. Host defaults and field capabilities differ.

## 2. Decision Drivers

- Inherit by default and avoid synchronizing runtime session values into generated files.
- Resolve both model and supported effort deterministically across all three hosts.
- Keep role prompts, permissions and delivery activity depth independent of model policy.
- Keep sync offline and preserve native-variant and transaction boundaries.

## 3. Considered Options

1. Keep host blocks and uninterpreted profiles. This preserves current rendering but requires prompt overrides
   for project-wide tuning and does not implement neutral levels.
2. Resolve neutral levels during distribution with shared project overrides. This fits existing inventory and
   receipt hashing but requires maintained native mappings and a documented precedence policy.
3. Select models dynamically at spawn time. This can observe the session but needs a runtime launcher or host
   prompt enforcement and exceeds distribution scope.

## 4. Decision Outcome

Choose option 2. `CAP-DIST-agent-projections` and `CAP-DIST-sync-and-transactions` define the
schema, resolution, diagnostics and built-in mappings. Retained host evidence documents native limitations.

- Use `inherit`, `light`, `standard`, `deep`; the default emits no devkit model or effort override.
- Keep overrides in shared `.devkit/config.toml`; no checkout-local policy or host-global mutations.
- Resolve level selection before deterministic rendering. Preserve explicit native fields when no neutral policy
  selects a level; a project selection replaces model/effort fields intentionally. Mixed source mechanisms fail.
- Keep native variants verbatim and explicitly outside global level selection. Reject role-specific level
  overrides on native variants in selected bundles.
- All shipped spec roles inherit model and effort. Remove fixed effort and uninterpreted profile metadata.
- Replace only the role reasoning effort preset and model-selection exclusion portions of
  `ADR-orchestration-workers`; its other worker and orchestration decisions remain in force. The supersedes
  field names its effort-preset alias and applies only to that decision.
- Delivery `activity-effort` continues selecting procedural depth independently of model policy.

## 5. Consequences

Projects can tune resource policy without duplicating role prompts. Projection and receipt hashes remain
reproducible without provider calls. Host-global and invocation overrides can still determine actual execution.
Aliases can resolve differently across providers; defaults require maintenance when documented host support changes.
Antigravity cannot express all four levels distinctly or guarantee inherited effort from this documentation.
Removing reviewer effort pins means expensive parent settings can propagate until a project opts into a level.

## 6. Confirmation

Resolver and sync tests live in `packages/devkit-dist/tests/` covering every AC in the proposal.
`packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` verifies inherited shipped roles.
Review compares generated native keys with the recorded host sources and checks limited ADR supersession.
No live model availability guarantee is made by offline tests.
