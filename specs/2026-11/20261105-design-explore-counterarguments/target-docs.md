---
id: PROP-design-explore-counterarguments-target
title: Target contracts for optional design critique responses
summary: "Drafts the optional author-response and coordinator-disposition refinement and its exact delivery paths without adding a role or runtime."
status: draft
proposal: SPEC-design-explore-counterarguments
created_at: 2026-11-05
targets:
  - file: docs/capabilities/delivery/CAP-DLV-design-exploration.md
  - file: docs/usecases/delivery/UC-explore-a-design-problem.md
---

# [Blueprint] Optional design critique responses

These are intended contract edits for Development. The proposal and `ADR-optional-design-critique-response`
contain the reasons; this blueprint does not change current contracts.

## 1. Capability draft

Refine `CAP-DLV-design-exploration` rule 14 and its interface text with these intended rules:

- WHEN a supported criticism can change feasibility, a consequential tradeoff or the recommendation, the
  coordinator SHOULD use one bounded critique/response exchange within the existing optional refinement pass.
- WHEN selecting an objection for response, the coordinator SHOULD pass the actual candidate, objection,
  evidence, failure condition, affected choice and preserved constraints to its explorer after initial passes.
- WHEN responding, the explorer SHOULD accept and revise, rebut with evidence/inference identified, or name a
  bounded unknown. The coordinator SHOULD report the actual response and its own disposition per selected objection.
- IF an author response is unavailable, THEN the coordinator MUST disclose missing coverage and label any inline
  analysis without inventing an author's return or agreement.
- WHEN another pass is useful, the coordinator SHOULD first name a decision-changing unresolved question and a
  finite pass/time bound. It SHOULD otherwise stop after the normal exchange and return remaining uncertainty.

Keep zero findings valid, roles optional and local, independent first-pass payloads, no fixed result schema,
conversation-first output and no implementation authority. This refinement adds no automatic research or companion
bundle invocation. Source inspection and semantic review check the SHOULD rules; instruction tests check the
missing-response prohibition. Tests establish instruction consistency, not model obedience or team benefit.

## 2. Use case draft

Refine `UC-explore-a-design-problem` extension 4a: one supported decision-changing objection can lead to the
candidate author's response, then coordinator disposition, within the existing pass. Add examples for accepting a
stale-cache objection with a concrete invalidation mechanism; rebutting an objection with inspected evidence;
retaining a bounded unknown; zero findings; a missing author return; and a response relying on an unverified claim.
An unresolved disagreement ends with its assumption visible unless a concrete further question and finite bound
are selected. Preserve the existing extensions for shared-context passes and missing role coverage.

## 3. Exact source and verification paths

| Path | Planned change |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/SKILL.md` | Conditional pointer to response procedure within the existing critique/refinement step. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/references/orchestration.md` | Response packet, actual return validation, per-objection disposition, failure fallback and bounded stop, with one example. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/solution-explorer.md` | Conditional response assignment after the independent first pass; accept/revise, rebut or bounded unknown. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/design-critic.md` | Bounded supported objections and surviving benefits; no automatic further debate. |
| `packages/devkit-catalog/tests/integration/bundles/test_design_explore.py` | Assert the response/evidence/fallback/stop instructions while retaining zero findings and optional-role checks. |
| `packages/devkit-catalog/tests/e2e/bundles/design_explore/test_installed_consumer.py` | Verify built-wheel deployment includes the response instructions in existing local role/reference assets. |

No manifest, package initializer, README, architecture, dependency or global-role change is planned. The ADR promoted
from `ADR-optional-design-critique-response` is the sole new decision file; existing ADRs are unchanged. No product
screen changes, so UX drafts/review are inapplicable. Development must load authoring context before asset edits.

Development runs focused catalog integration and installed-consumer checks, required lint/types/rules and the
repository affected-test selector with its full fallback. Semantic review walks all five proposal ACs against the
instructions and examples; deterministic checks do not claim that a language model will obey them. These paths
are independent of deep-research implementation files; the Host still sequences any shared generated outputs.
