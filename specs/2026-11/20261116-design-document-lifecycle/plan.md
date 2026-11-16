---
id: PLAN-design-document-lifecycle
spec: SPEC-design-document-lifecycle
---

# Technical Plan: `SPEC-design-document-lifecycle`

## 1. Constitution & Invariant Review

`ADR-formal-document-delivery-integration` and `SPEC-formal-document-kinds` supply direction and core policy.
No architectural invariant changes. `ARCH-05-2-components` permits existing spec entrypoints → docs documents/governance
edges. Adaptive assets consume public docs guidance without a devkit_spec import. No new feature or test tier.

## 2. Architecture Overview & Impact

Extend proposal scaffolding and shipped SDD/adaptive guidance at existing Planning, review, reconcile, adoption
and source-identified documenter boundaries. Runtime derivation already calls core applicability; retain its generic
logic and update CAP/UC-only descriptions. Formal responsibility assessment is body guidance, not another registry.

## 3. Component & Interface Design

The proposal target-docs scaffold retains metadata and existing sections, adding a formal responsibility table
and maintenance evidence prompts. Spec-plan/planning/review/completion/sync consume the same role instructions.
Entrypoint skills distinguish CAP/UC doorways from useful DESIGN mechanism paths and explicitly skip core-ineligible
kinds. CLI flags, codes and JSON remain unchanged. Adaptive documents/documenter/current-context and adoption assets
route to canonical roles, preserve source identity and identify missing evidence without implicit SDD records.

## 5. Error Handling & Edge Cases

Exercise alias/root changes with ordinary artifact links, one-parent split/transfer, source-deletion retirement,
negative orphan/invalid alias/stale-anchor controls and unrelated-role byte preservation. Reference rules do not
prove arbitrary ordinary links: tests resolve destinations and compare bytes. Native staged snapshots are needed
for deleted-path liveness. Retired documents remain rule-checked. Use no completed-spec fixture exemption.

## 6. Verification & Test Plan

Use focused scaffold/entrypoint/guidance tests and new existing-tier composed E2E files in both packages, actual
CLI read/fix/derive/apply operations and source/ordinary-link comparison. Run installed spec/adaptive E2E, lint and
Pyright for both packages, affected unit-integration selection from 5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4 with
full fallback, native sync and CI rules. HIGH separate code and reconcile reviews use frozen source snapshots.
Core and Viewer are separately owned; required Viewer completion cannot be claimed here.
