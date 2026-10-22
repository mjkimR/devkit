---
id: FB-plan-intent-overrides-accepted-adr
title: A plan-intent can reverse an accepted ADR outcome without ADR write authority
scope: repo
kind: friction
category: instruction-conflict
target: spec-delegate payload (allowed_boundaries) and the constitution's ADR requirement for lasting policy changes
skill: spec-specify
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-plan-intent-overrides-accepted-adr] A plan-intent can reverse an accepted ADR outcome without ADR write authority

## 1. Friction / Question

- **Context**: A Development worker implemented a recorded plan-intent that refuses unsupported `[presentation] language` values.
- **Expectation**: The constitution says a lasting policy change needs an ADR; ADRs are append-only and replaced through `supersedes`.
- **Actual**: `ADR-shared-language-preference-with-bounded-approval-content` (accepted) decides an English fallback for unsupported strings. The worker payload denied `docs/decisions/`, so no superseding ADR could be written; the capabilities were rewritten citing the spec while the accepted ADR still states the opposite outcome.
- **Workaround (or Interpretation Chosen)**: Treated the explicit user plan-intent as taking precedence, recorded the conflict as a spec assumption and in `reconcile.md`, and left a superseding ADR to the Host.
- **Suggestion**: When a Host writes a plan-intent or payload that reverses an accepted ADR's outcome, either include an exact superseding-ADR path in the write boundary or record the superseding ADR itself before delegation. Assessment: without one, `devkit spec search` keeps surfacing an accepted ADR that contradicts the current capability.

## Diagnostic Details

- **Reproduction**: Search `presentation language fallback` against the base; the accepted ADR's Decision Outcome names the fallback that this unit removed.
- **Expected / Actual**: Expected an ADR path in scope or a pre-recorded supersession; actual is a denied `docs/decisions/` path.
- **Versions**: Unit base 490b0b28.
- **Conditions**: Local-orchestrated Development worker, activity-effort low.
- **Workarounds Attempted**: Assumption and reconcile note; no ADR edit.
- **Related Assets**: `ADR-shared-language-preference-with-bounded-approval-content`, `SPEC-feedback-quick-fixes`, `spec-delegate/references/payload.md`.

## Evidence

```text
ADR Decision Outcome: "unsupported string fallback `en`"
Payload: denied ... docs/decisions/
spec.md Assumption 3 records the replacement; reconcile.md leaves the superseding ADR to the Host.
```
