---
name: spec-plan
description: Map spec requirements to the system architecture, check existing capabilities, ADRs and invariants, weigh technical tradeoffs, and write an implementation plan (plan.md) sized to the change.
---

# spec-plan: Technical Planning Workflow

Design the solution for an agreed `spec.md` and write `plan.md` beside it, at the `specify` stage of
`sdd-spec-feature` or the `plan-tasks` stage of `sdd-spec-bugfix`. A bugfix bundle has no `plan.md` yet: create it
with frontmatter `id: PLAN-<slug>` and `spec: SPEC-<slug>`.

## Procedure

1. **Invariants**: check the design against accepted ADRs (`devkit spec search "<topic>" --kind decision`),
   `docs/architecture/` and the capabilities it touches (`devkit spec refs <CAP-ID> --direction in`).
2. **Changed invariant**: if an architectural rule that must hold has to change, propose an ADR
   (`docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`, template `.devkit/managed/spec/templates/decision.md`).
3. **Choices**: inside the agreed intent, take the recommended option and record its reason. Outside it, raise a
   problem for the Host; a bugfix that needs a different defect scope returns to `characterize`.
4. **Design**: give every story and `[AC-NN]` scenario a handling component and keep every non-goal out. Name the
   components touched, their contracts (types, signatures, schemas; for a CLI or API its flags, codes and payloads),
   the failure modes and any migration.
5. **Verification**: name the tests and checks that prove each scenario; a bugfix keeps its reproduction test as the
   regression test.

## Plan output

Read the skeleton, then rewrite it, keeping its frontmatter. Cite documents by full ID, the unit's own spec included.
Always write sections 1, 2 and 6; add the others only when the change has that content:

1. `Constitution & Invariant Review`: conflicts with ADRs, architecture or capabilities and the ADR each needs, or
   "None".
2. `Architecture Overview & Impact`: impacted components with what changes, new dependencies with their reason.
3. `Component & Interface Design`: a diagram and the normative interface snippet.
4. `Storage & State Management`.
5. `Error Handling & Edge Cases`.
6. `Verification & Test Plan`: the commands under the repository's test policy, and which results can be
   reused.

## Completion

- [ ] Every story and scenario has an implementation path and no non-goal is planned.
- [ ] `devkit workflow next --unit <dir>` no longer reports `not-skeleton(plan.md)`.
