---
id: PLAN-ux-design-exploration
spec: SPEC-ux-design-exploration
---

# Technical Plan: `SPEC-ux-design-exploration`

## 1. Constitution & Invariant Review

`ARCH-05-2-components` permits content-only catalog modules with empty initializers. No runtime dependency,
feature edge or existing invariant changes. `ADR-uiux-improvement-workflow-boundary` owns explicit invocation,
local roles, optional perspectives and consumer-workflow authority. Its final clause traces will point to the
new capability after reconciliation. The implementation creates no product UI.

## 2. Architecture Overview & Impact

Add `devkit_catalog/uiux_improve/bundle/` with one user-invoked skill and core preset. Register it through the
existing devkit.bundles entrypoint. Keep the initializer empty and the catalog version/dependencies unchanged.
The source contains the entry, four local roles and two conditional references. No sibling assets are imported.
The repository's currently selected bundle set remains unchanged. The Host authorized the exact
`.devkit/architecture.toml` catalog data_roots addition required by the existing architecture rule; no dependency
edge, policy or declaration schema changes.

The entry owns intake, authority, implementation/verification continuity and completion. The orchestration
reference owns payload construction, path resolution, independent first passes, fallback and return validation.
Design guidance provides flow, hierarchy, feedback, accessibility and visual-character lenses. Roles return bounded
suggestions or evidence; the coordinator owns product changes through the consumer workflow.

## 3. Component & Interface Design

```text
uiux-improve/SKILL.md
  → references/design-guidance.md when choosing design lenses
  → references/orchestration.md when delegating
      → roles/{designer,unconventional-designer,reference-researcher,critic}.md
```

The bundle declares `invocation = "user"`; existing projections supply native user-only metadata. Role Markdown
is behavioral guidance, not a permission mechanism. A missing tool or artifact yields qualified partial work and
its concrete blocker. A review-only request remains read-only. The skill neither chooses policy nor grants
commit, integration or publication authority.

## 6. Verification & Test Plan

- AC-01/AC-06: real sync selection, removal and reselection tests plus isolated built-wheel CLI consumer.
- AC-02/AC-03/AC-04: focused semantic contract assertions and mandatory independent code review of representative
  review-only, visual-refinement, flow-simplification and unavailable-tool scenarios.
- AC-05: installed role/reference links, self-containment scan and independent instruction review.
- Run `just test-affected --base 94cd340e166d0714788c185f514923268e6d0b2a` with full fallback retained;
  catalog lint/type checks and `uv run devkit rules check --ci --base main`.
- Build and run the isolated consumer test without docs, agt or spec. No live browser or model outcome is claimed.
- Reconcile the capability/use case, content layout, ADR traces and package/consumer guidance; verify separately.
