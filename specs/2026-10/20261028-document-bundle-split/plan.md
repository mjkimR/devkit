---
id: PLAN-document-bundle-split
spec: SPEC-document-bundle-split
---

# Technical Plan: Document bundle split

## 1. Constitution & Invariant Review

`ADR-document-package` and `ADR-document-and-sdd-bundles` authorize independent implementation and distribution.
`ARCH-05-2-components` places docs assets under devkit_docs/bundles/docs/bundle. Rule judgments remain unchanged.
No conflicting invariant requires another ADR.

## 2. Architecture Overview & Impact

Move shared authoring assets from spec into devkit-docs. Register docs through devkit.bundles and auto-select core.
Keep lifecycle assets in spec and use docs context for shared authoring constraints. Both wheels retain existing
runtime dependencies. This is asset distribution, not a runtime policy setting.

## 3. Component & Interface Design

- docs:core owns eight instructions, nine document rules, five shared templates, docs-pointer and steering context.
- spec:core owns five lifecycle rules, proposal template, SDD pointer/constitution and all lifecycle skills/roles/workflows/playbooks.
- docs:docs-skeleton seeds absent document scaffolds; sync preserves existing seeded bytes.
- Repair rule related IDs, all active asset citations, package tests and published installation guidance.
- Move immutable ADR history and completed-spec preservation from shared writing instructions into the SDD constitution.
- Keep installed extension behavior explicit when assets are deselected; clean isolation omits devkit-spec.

## 5. Error Handling & Edge Cases

Use existing manifest validation and sync transaction behavior. Explicit docs opt-out requires re-adding docs for
supported SDD selection. No resolver or compatibility alias is introduced. Existing seeded files stay project-owned.

## 6. Verification & Test Plan

- AC-01/AC-06: build wheels and install docs without spec in a fresh environment; sync, contexts, nine rules and docs CLI.
- AC-02/AC-03: bundle inventory/reference and semantic guidance tests; existing SDD proposal/workflow tests.
- AC-04/AC-05: real sync selection tests for opt-in seeds, byte preservation and spec removal/re-add.
- AC-06: just lint-check docs/spec, just check docs/spec, just test-affected with full fallback, sync --check and CI governance.
- All checks use this worktree. Review uses isolated code-reviewer and reconcile-reviewer at medium effort.
