---
id: PLAN-five-subagent-levels
spec: SPEC-five-subagent-levels
---

# Technical Plan: `SPEC-five-subagent-levels`

## 1. Constitution & Invariant Review

The user explicitly replaces the preset cardinality/default pairs and all-role inheritance rule from
`ADR-subagent-level-projection`. A scoped successor decision records the five names and compact scout exception.
Inherited neutral defaults, shared-only configuration, native variant bytes and layer boundaries remain unchanged.
Antigravity's pending behavior is not inferred from session-only model/effort flags.

## 2. Architecture Overview & Impact

Extend the existing LEVELS enum and DEFAULTS registry. No runtime launcher or new dependency.
Use absent ModelSettings.effort for compact, standard and deep on Claude/Codex. Keep the parser's strict effort
registry independent of the neutral preset names. Update comments and source role selection; renderer, receipts,
status and dry-run reuse the existing policy path. No migration reader for light.

## 3. Component & Interface Design

`LEVELS = (inherit, minimal, compact, standard, deep, maximal)` defines configuration and source validation.
`resolve_settings` retains its interface and native escape-hatch behavior. Mapping fields remain partial overrides;
field inherit resets to omission. Source scout gains level compact; other role sources are untouched.
The Antigravity resolution behavior is finalized after the Host supplies the user's pending decision.

## 6. Verification & Test Plan

Parametrized unit tests assert exact presets and reset/override behavior. Integration tests parse native files to
verify omitted effort for inherited presets, explicit low/high bounds, source scout defaults, project resets and
stable sync lifecycle. Existing strict configuration and native variant regressions remain.
Run focused tests while only settled mappings change; run just test-affected --base main after the final host
contract is settled. Run dist/spec lint-check and Pyright, independent code review and separate reconcile review.
Host owns final sync, tracked deployment artifacts and integration.
