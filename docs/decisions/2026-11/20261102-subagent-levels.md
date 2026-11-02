---
id: ADR-subagent-levels
title: Neutral subagent model levels resolved at distribution time
summary: "For portable subagent model selection, we resolve opt-in neutral presets (minimal to maximal plus lean) at distribution, inherit by default and give the scout compact, to separate model family from effort, accepting maintained host mappings and fewer Antigravity distinctions."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-subagent-level-projection
  - ADR-five-subagent-levels
  - ADR-lean-subagent-level
---

# [ADR-subagent-levels] Neutral subagent model levels resolved at distribution time

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `CAP-DIST-agent-projections`, `CAP-DIST-sync-and-transactions`

---

## 1. Context & Problem Statement

`CAP-DIST-agent-projections` renders native model and effort fields. Projects need portable opt-in levels and
overrides without replacing role prompts, and host defaults and field capabilities differ. The desired presets
distinguish low effort and inherited effort on lightweight models, and inherited effort and high effort on larger
models. Bounded operational roles also need an opt-in setting between compact and standard that selects Terra on
Codex and fixes medium effort where the native role schema permits it; changing standard would change existing
consumers. Antigravity's native role schema cannot select Argon or per-role effort.

---

## 2. Decision Drivers

- Inherit by default and avoid synchronizing runtime session values into generated files.
  (ADR-subagent-level-projection)
- Resolve both model and supported effort deterministically across all three hosts. (ADR-subagent-level-projection)
- Keep role prompts, permissions and delivery activity depth independent of model policy.
  (ADR-subagent-level-projection)
- Keep sync offline and preserve native-variant and transaction boundaries. (ADR-subagent-level-projection)
- Keep neutral names distinct from native effort values. (ADR-five-subagent-levels)
- Keep project defaults inherited and select compact only on the source scout contract. (ADR-five-subagent-levels)
- Preserve offline deterministic distribution and existing configuration, transaction and variant boundaries.
  (ADR-five-subagent-levels)
- Honor native capability limits without replacing requested Argon with Pro or emitting fictional keys.
  (ADR-five-subagent-levels)
- Preserve every existing level and the implicit inherited default. (ADR-lean-subagent-level)
- Specify model and effort together for bounded work on Claude Code and Codex. (ADR-lean-subagent-level)
- Keep native capability limits and existing project overrides. (ADR-lean-subagent-level)

---

## 3. Considered Options

- **Keep host blocks and uninterpreted profiles** (rejected in `ADR-subagent-level-projection`): preserves current
  rendering but requires prompt overrides for project-wide tuning and does not implement neutral levels.
- **Resolve neutral levels during distribution with shared project overrides** (selected in
  `ADR-subagent-level-projection`): fits existing inventory and receipt hashing but requires maintained native mappings
  and a documented precedence policy.
- **Select models dynamically at spawn time** (rejected in `ADR-subagent-level-projection`): can observe the session
  but needs a runtime launcher or host prompt enforcement and exceeds distribution scope.
- **Retain the existing names and resource pairs** (rejected in `ADR-five-subagent-levels`): does not express the
  chosen five-stage policy.
- **Use minimal, compact, standard, deep and maximal; inherit unavailable Antigravity combinations** (selected in
  `ADR-five-subagent-levels`): preserves native behavior and the user's fallback choice while expressing all five
  pairs on Claude Code and Codex.
- **Introduce a runtime launcher or prompt-driven effort emulation** (rejected in `ADR-five-subagent-levels`): exceeds
  distribution scope.
- **Add lean** (selected in `ADR-lean-subagent-level`): selects the requested resource pairs without changing
  existing levels.
- **Change standard** (rejected in `ADR-lean-subagent-level`): replaces an existing model/effort contract for all
  consumers choosing it.
- **Use only project mappings** (rejected in `ADR-lean-subagent-level`): requires each consumer to redefine an
  existing level for the same setting.

---

## 4. Decision Outcome

### Distribution-time resolution

- Resolve neutral levels during distribution with shared project overrides. `CAP-DIST-agent-projections` and
  `CAP-DIST-sync-and-transactions` define the schema, resolution, diagnostics and built-in mappings. Retained host
  evidence documents native limitations. (ADR-subagent-level-projection)
- The default, `inherit`, emits no devkit model or effort override. (ADR-subagent-level-projection)
- Keep overrides in shared `.devkit/config.toml`; no checkout-local policy or host-global mutations.
  (ADR-subagent-level-projection)
- Resolve level selection before deterministic rendering. Preserve explicit native fields when no neutral policy
  selects a level; a project selection replaces model/effort fields intentionally. Mixed source mechanisms fail.
  (ADR-subagent-level-projection)
- Keep native variants verbatim and explicitly outside global level selection. Reject role-specific level overrides
  on native variants in selected bundles. (ADR-subagent-level-projection)
- Remove fixed effort and uninterpreted profile metadata from the shipped spec roles.
  (ADR-subagent-level-projection)
- Delivery `activity-effort` continues selecting procedural depth independently of model policy.
  (ADR-subagent-level-projection)
- **Replaced effort presets**: this decision replaced, in `ADR-orchestration-workers`, its "Role reasoning effort
  presets" decision and its model-selection exclusion; that ADR's other worker and
  orchestration decisions remain in force. (ADR-subagent-level-projection)

### Presets

- Keep `inherit` as the implicit default, separate from the opt-in presets. (ADR-five-subagent-levels)
- Use lightweight models at low effort for `minimal` and inherited effort for `compact`. (ADR-five-subagent-levels)
- Use general-purpose models with inherited effort for `standard`, and larger models with inherited effort for `deep`
  or high effort for `maximal`. (ADR-five-subagent-levels)
- On Antigravity, `compact` selects Flash and omits effort; `minimal`, `standard`, `deep` and `maximal` omit both model
  and effort. No Pro-for-Argon substitution or warning is introduced. Explicit project mapping validation remains
  strict. (ADR-five-subagent-levels)
- Set the source SDD scout contract to `compact`, and do not tie model presets to procedural activity-effort.
  (ADR-five-subagent-levels)
- Remove `light` in place, with no alias or migration; the repository has no external format consumers.
  (ADR-five-subagent-levels)
- Add the opt-in `lean` level with Claude Code `sonnet` / `medium`, Codex `gpt-6.1-terra` / `medium`, and Antigravity
  `flash` with effort omitted. The desired Flash high setting cannot be encoded in the supported per-subagent schema;
  lean makes no high-effort guarantee there and introduces no prompt-based emulation. (ADR-lean-subagent-level)
- Resource-manager selection and naming remain separate decisions. (ADR-lean-subagent-level)
- The user requested session delivery; the additive `lean` preset uses no proposal or spec Unit. Capability
  documentation and this decision record retain the public contract without adding session workflow records.
  (ADR-lean-subagent-level)

---

## 5. Consequences

- **Positive**:
  - Projects can tune resource policy without duplicating role prompts. Projection and receipt hashes remain
    reproducible without provider calls. (ADR-subagent-level-projection)
  - Roles can choose a model family while retaining session effort. (ADR-five-subagent-levels)
  - Consumers can select lean through source level, project default or role override. Model-only overrides retain
    medium effort on Claude Code/Codex; an explicit inherit reset removes it. (ADR-lean-subagent-level)
- **Negative / Risks**:
  - Host-global and invocation overrides can still determine actual execution. Aliases can resolve differently across
    providers; defaults require maintenance when documented host support changes. (ADR-subagent-level-projection)
  - Antigravity cannot express all levels distinctly or guarantee inherited effort from this documentation.
    (ADR-subagent-level-projection)
  - Removing reviewer effort pins means expensive parent settings can propagate until a project opts into a level.
    (ADR-subagent-level-projection)
  - A compact scout uses lightweight families by default, so difficult research can opt into a stronger preset
    through project overrides. Antigravity provides fewer native distinctions; inherited settings do not force Argon
    or exact runtime effort. Provider/account availability remains host-owned. The host mapping registry requires
    maintenance as native capabilities change. (ADR-five-subagent-levels)
  - Availability and actual runtime behavior remain host-owned. Lean is not a claim of equal cross-provider quality or
    measured operational reliability. (ADR-lean-subagent-level)

---

## 6. Confirmation

- Resolver and sync tests live in `packages/devkit-dist/tests/` covering every AC in the proposal.
  (ADR-subagent-level-projection)
- Resolver and projection tests under `packages/devkit-dist/tests/` pin all five native mappings, omitted effort,
  strict invalid configuration, override/reset behavior and sync lifecycle. (ADR-five-subagent-levels)
- Source role tests under `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` pin the
  shipped roles' source levels, with compact for scout. (ADR-subagent-level-projection; ADR-five-subagent-levels)
- `packages/devkit-dist/tests/unit/features/distribution/test_subagent_levels.py` checks native pairs, selection
  precedence, partial overrides and reset. `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`
  checks native projection and installed configuration behavior. Existing level behavior remains covered by their
  parameterized cases. (ADR-lean-subagent-level)
- Review compares generated native keys with the recorded host sources and checks limited ADR supersession.
  (ADR-subagent-level-projection)
- Independent code and reconcile reviews check agreement with `SPEC-five-subagent-levels`. (ADR-five-subagent-levels)
- No live model availability guarantee is made by offline tests. (ADR-subagent-level-projection)
