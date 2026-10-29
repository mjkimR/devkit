---
id: ADR-lean-subagent-level
title: Add a lean model preset with explicit medium effort
summary: "For bounded subagent operations, we add lean with Sonnet medium and Terra medium while preserving existing presets, to avoid parent effort inheritance, accepting Flash without per-role effort on Antigravity."
status: accepted
created_at: 2026-10-29
supersedes: ADR-five-subagent-levels
---

# [ADR-lean-subagent-level] Add a lean model preset with explicit medium effort

## 1. Context & Problem Statement

Standard selects Sonnet or Sol without specifying effort, and inherits both fields on Antigravity.
Bounded operational roles need an opt-in setting between compact and standard that selects Terra on Codex and
fixes medium effort where the native role schema permits it. Changing standard would change existing consumers.

## 2. Decision Drivers

- Preserve every existing level and the implicit inherited default.
- Specify model and effort together for bounded work on Claude Code and Codex.
- Keep native capability limits and existing project overrides.

## 3. Considered Options

- Add lean: selects the requested resource pairs without changing existing levels.
- Change standard: replaces an existing model/effort contract for all consumers choosing it.
- Use only project mappings: requires each consumer to redefine an existing level for the same setting.

## 4. Decision Outcome

Add the opt-in `lean` level with Claude Code `sonnet` / `medium`, Codex `gpt-6.1-terra` / `medium`,
and Antigravity `flash` with effort omitted. The desired Flash high setting cannot be encoded in the supported
per-subagent schema; lean makes no high-effort guarantee there and introduces no prompt-based emulation.

This supersedes only the closed five-preset registry and compact-only Flash mapping in `ADR-five-subagent-levels`.
Preserve its other level mappings, scout-only source selection, inheritance, strict explicit mapping validation
and native capability fallback policy. Resource-manager selection and naming remain separate decisions.

The user requested session delivery; this additive preset uses no proposal or spec Unit. Capability documentation
and this decision record retain the public contract without adding session workflow records.

## 5. Consequences

Consumers can select lean through source level, project default or role override. Model-only overrides retain
medium effort on Claude Code/Codex; an explicit inherit reset removes it. Availability and actual runtime behavior
remain host-owned. Lean is not a claim of equal cross-provider quality or measured operational reliability.

## 6. Confirmation

`packages/devkit-dist/tests/unit/features/distribution/test_subagent_levels.py` checks native pairs, selection
precedence, partial overrides and reset. `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`
checks native projection and installed configuration behavior. Existing level behavior remains covered by their
parameterized cases.
