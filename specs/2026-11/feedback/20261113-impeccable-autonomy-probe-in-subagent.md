---
id: FB-impeccable-autonomy-probe-in-subagent
title: Impeccable's AUTONOMY_DIRECTIVE_CHECK asks a subagent for a live probe it cannot run
scope: upstream
kind: friction
category: instruction-conflict
target: Impeccable skill (AUTONOMY_DIRECTIVE_CHECK)
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-11-13
---

# [FB-impeccable-autonomy-probe-in-subagent] Impeccable's AUTONOMY_DIRECTIVE_CHECK asks a subagent for a live probe it cannot run

## 1. Friction / Question (friction, question)

- **Context**: `app-uiux-improve` delegated refinement commands to a fresh Impeccable child under a brief with stop
  conditions.
- **Expectation**: Impeccable's autonomy check can be satisfied in a delegated, non-interactive child, or says how a
  delegating brief satisfies it.
- **Actual**: `AUTONOMY_DIRECTIVE_CHECK` asks for a live probe that a subagent cannot perform.
- **Workaround (or Interpretation Chosen)**: The child proceeded under the brief's stop conditions.
- **Suggestion**: Report upstream to Impeccable: accept an explicit delegation directive (for example a brief naming
  the stop conditions) in place of the live probe. In devkit, `SPEC-uiux-improve-impeccable-routing` decides whether
  the brief template should name this directive.

## Diagnostic Details

- **Reproduction**: Run an Impeccable refinement command in a fresh Claude Code subagent.
- **Expected / Actual**: Expected a satisfiable check; actual a probe the child cannot run.
- **Versions**: Impeccable version unknown (4.8.x plugin); `app-uiux-improve` 0.1.6.
- **Conditions**: Claude Code subagent; two consumer runs.
- **Workarounds Attempted**: proceed under the brief's stop conditions (worked).
- **Related Assets**: `MAT-uiux-improve-pilot` finding A2b, `CAP-DLV-uiux-improvement` rule 16.

## Evidence

```text
Pilot finding A2b: AUTONOMY_DIRECTIVE_CHECK asks for a live probe a subagent cannot perform; the child proceeded
under the brief's stop conditions.
```

## Disposition

Promoted to `SPEC-uiux-upstream-fallbacks` as completed local mitigation. The local skill briefs actual capabilities and stop conditions, reports an unavailable required probe, stops dependent Impeccable work and uses the user-operated session or authorized inline work without treating the brief as a passed or overridden check.

Verification: focused UI/UX bundle integration 16 passed; installed-consumer E2E 1 passed; catalog lint/format and type checks passed; `just test-affected --base 5cab6156a60de1a2a2845e38fc19bda92961c90e --tier all` passed 182 tests. These checks verify shipped instructions and distribution, not upstream runtime or model obedience.

The upstream runtime was not fixed. Native upstream trials were not required or performed. The user selected local compensation and no external submission or retained upstream follow-up; this disposition records no upstream resolution.
