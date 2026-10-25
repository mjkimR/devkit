---
id: ADR-five-subagent-levels
title: Five neutral model presets with a compact scout and native capability fallback
summary: "For portable model selection, we use five neutral presets and a compact scout while unsupported Antigravity presets inherit, to separate model family from effort, accepting reduced host distinctions."
status: accepted
created_at: 2026-10-25
supersedes: ADR-subagent-level-projection
---

# [ADR-five-subagent-levels] Five neutral model presets with a compact scout and native capability fallback

## 1. Context & Problem Statement

`ADR-subagent-level-projection` defines deterministic distribution-time model policy, inherited defaults and a
three-preset registry. The desired five presets distinguish low effort and inherited effort on lightweight models,
and inherited effort and high effort on larger models. Only the SDD scout should select a level by default.
Antigravity's native role schema cannot select Argon or per-role effort.

## 2. Decision Drivers

- Keep neutral names distinct from native effort values.
- Keep project defaults inherited and select compact only on the source scout contract.
- Preserve offline deterministic distribution and existing configuration, transaction and variant boundaries.
- Honor native capability limits without replacing requested Argon with Pro or emitting fictional keys.

## 3. Considered Options

1. Retain the existing names and resource pairs. This does not express the chosen five-stage policy.
2. Use minimal, compact, standard, deep and maximal; inherit unavailable Antigravity combinations. This preserves
   native behavior and the user's fallback choice while expressing all five pairs on Claude Code and Codex.
3. Introduce a runtime launcher or prompt-driven effort emulation. This exceeds distribution scope.

## 4. Decision Outcome

Choose option 2 on the user's direction. `CAP-DIST-agent-projections` defines exact native pairs and
`CAP-DIST-sync-and-transactions` defines configuration validation and resets.

- Keep inherit as the implicit default, separate from the five opt-in presets.
- Use lightweight models at low effort for minimal and inherited effort for compact.
- Use general-purpose models with inherited effort for standard, and larger models with inherited effort for
  deep or high effort for maximal.
- On Antigravity, compact selects Flash and omits effort. Every other built-in preset omits both model and effort.
  No Pro-for-Argon substitution or warning is introduced. Explicit project mapping validation remains strict.
- Set only the source SDD scout contract to compact. Leave other role sources inherited and do not tie model
  presets to procedural activity-effort.
- Preserve distribution-time resolution, shared-only overrides, source/native conflict rules, verbatim native
  variants and runtime inheritance limitations from the superseded decision.
- Remove light in place, with no alias or migration; the repository has no external format consumers.

## 5. Consequences

Roles can choose a model family while retaining session effort. A compact scout uses lightweight families by
default, so difficult research can opt into a stronger preset through project overrides. Antigravity provides fewer
native distinctions; inherited settings do not force Argon or exact runtime effort. Provider/account availability
remains host-owned. The host mapping registry requires maintenance as native capabilities change.

## 6. Confirmation

Resolver and projection tests under `packages/devkit-dist/tests/` pin all five native mappings, omitted effort,
strict invalid configuration, override/reset behavior and sync lifecycle. Source role tests under
`packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` pin compact only for scout.
Independent code and reconcile reviews check agreement with `SPEC-five-subagent-levels`.
