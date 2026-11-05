---
id: PLAN-deep-research-practical-orchestration
spec: SPEC-deep-research-practical-orchestration
---

# Technical Plan: `SPEC-deep-research-practical-orchestration`

## 1. Constitution & Invariant Review

`ADR-deliverable-driven-research` authorizes the lasting instruction refinement. The explicit-only entry,
local-role placement, source qualification, material ownership and no-commit boundaries in `CAP-DLV-deep-research`
remain intact. No architecture, dependency, policy or runtime changes are needed.

## 2. Architecture Overview & Impact

Update the existing entry, orchestration/synthesis references and four roles inside the deep-research bundle.
Use the existing brief and assignment rather than adding intake machinery. Keep the final usefulness check inline;
an optional critic receives the same task criteria. Distinguish technical retrieval failure from refused or
ambiguous authority in both coordinator and role instructions. Recovery consumes the existing bound.

The coordinator reviews source-specific returns and reopens only consequential gaps; the retained result contains
the requested artifact and a useful next action with optional investigations clearly conditional. A practical repo
request is an example, not a universal research output schema. No listed file needs a test change merely to prove
wording. Existing real sync/projection/removal and wheel-consumer tests retain the distribution contract.

Reflect the same behavior in `CAP-DLV-deep-research` and `UC-research-an-idea-and-shape-a-roadmap`; complete exact ADR
rule traces during reconciliation. Only actual tracked sync outputs may extend the declared file list.

## 6. Verification & Test Plan

- Review each AC-01 through AC-06 against the changed source and the target blueprint's semantic examples.
- Run `just test-affected --base 94cd340e166d0714788c185f514923268e6d0b2a`, preserving the selector's full fallback.
- Run the deep-research installed-consumer e2e when not selected already; its built wheel must preserve packaging and material ownership (AC-07).
- Run `just lint-check catalog`, `just check catalog`, bundle hygiene and CI rules against the retained base.
- Run `devkit sync`, inspect every generated tracked path, then `devkit sync --check` with exit 0.
- Use one nested code review at medium effort. Reconcile all identified contract deltas and independently verify them if interpretation remains uncertain.

The implementer commits each stage; the Host alone integrates and checks the final combined base HEAD.
