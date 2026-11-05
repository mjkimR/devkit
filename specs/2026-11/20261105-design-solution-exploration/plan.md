---
id: PLAN-design-solution-exploration
spec: SPEC-design-solution-exploration
---

# Technical Plan: `SPEC-design-solution-exploration`

## 1. Constitution & Invariant Review

No conflict. Preserve content-only catalog layout under `ARCH-05-2-components` and the independent-entry decision
in `ADR-explicit-solution-exploration`. Current research/UIUX additions do not break the accepted premises.
The Host expressly authorizes adding only design_explore to catalog data_roots in `.devkit/architecture.toml`;
this is initial Tier A scope necessary to classify the new content module, with no new feature edge or policy.

## 2. Architecture Overview & Impact

Register design-explore in catalog metadata. Add an empty module initializer and one bundle manifest selecting
only a user-invoked skill. Keep three roles and two conditional references inside that skill; no global roles,
runtime module, dependency, automatic selection or companion-bundle import. Package version stays 0.1.5.
Reconcile into one capability, one use case, existing architecture, ADR clause traces and consumer guidance.

## 3. Component & Interface Design

The manifest interface is name = "design-explore", default_preset = "core", one skill asset with
invocation = "user", and presets.core.assets = ["design-explore"]. The metadata target is
`design-explore = "devkit_catalog.design_explore"`.

The coordinator recovers constraints, selects useful premise passes, compares real mechanisms and returns the
result. Keep small questions inline. For useful delegation, load only selected role bodies by absolute installed
path; send self-contained facts without parent conversation or peer conclusions where supported. Disclose inline
fallback. Research and one bounded critique/refinement pass serve a concrete unknown, with zero findings valid.
Only the coordinator writes a user-requested destination. Missing coverage and blocked writes remain explicit.

## 5. Error Handling & Edge Cases

Missing facts ask only when they change useful directions. Missing fresh contexts use disclosed inline passes;
missing or failed returns are not votes or evidence. A denied access/write stops that operation without rerouting.
An unavailable destination leaves a useful conversation result and names the blocked write.

## 6. Verification & Test Plan

- AC-01, AC-03, AC-06: real manifest/sync integration across supported projections, opt-in selection, no global
  roles, independent removal and re-addition; real dist/catalog wheel consumer without agt/docs/spec.
- AC-02 through AC-05: focused instruction-boundary regression checks and independent semantic code review.
- All ACs: `just test-affected --base 5401115e19a09cdbe3d1a9e1a1ae7b85569b753d` with its full fallback,
  `just lint-check catalog`, `just check catalog`, and `uv run devkit rules check --ci --base <handoff-head>`.
- Distribution baseline at handoff: design-explore entry points 0, source absent, local roles 0. Repeat at head;
  assert one entry and three roles and validate installed lifecycle. No creative-benefit experiment is planned.
- Use mandatory medium code-reviewer and separate reconcile-reviewer; implementer writes records and Living Spec.
