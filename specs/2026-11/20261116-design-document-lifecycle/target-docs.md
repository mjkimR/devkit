---
id: PROP-design-document-lifecycle-target
title: Formal document lifecycle target blueprint
summary: "Plans complete formal-kind impact, maintenance, reconciliation and adoption through existing SDD and adaptive delivery boundaries."
status: draft
proposal: SPEC-design-document-lifecycle
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
  - file: docs/usecases/governance/UC-keep-the-living-spec-consistent.md
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
  - file: docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md
  - file: docs/usecases/harness/UC-adopt-in-an-existing-repository.md
---

# [PROP-design-document-lifecycle-target] Formal document lifecycle target blueprint

This is future-state Planning for `SPEC-design-document-lifecycle`. Current contracts continue to describe current
behavior until implementation reconciles them. Core identity/schema and neutral docs assets belong to
`SPEC-formal-document-kinds`; presentation belongs to `PROP-design-document-viewer`.

## 1. System capabilities plan

| Owner | Exact planned change |
| --- | --- |
| `CAP-DLV-delivery-workflows` | Rule 9 reflection and rule 15 review/reconcile coverage explicitly include affected formal responsibilities and source/detail/artifact maintenance; stages, checks and gates stay the same |
| `CAP-DLV-proposal-planning` | Target-docs and Planning include affected formal roles, IDs, source evidence, migration and applicability, preserving existing approval/handoff boundaries |
| `CAP-DLV-adaptive-development` | Project documents and documenter include core formal roles, all maintenance operations and source-bound semantic comparison; adaptive context maps retain IDs or explicit missing coverage |
| `CAP-DLV-sdd-baseline-adoption` | Retained coverage includes warranted formal roles and their source/detail/artifact agreement; required missing evidence remains a gap, without retrospective Units |
| `CAP-TRACE-code-entrypoints` | Derive/review/apply supports every core-eligible kind; eligibility/path semantics are referenced from core policy, and ineligible kinds are explicitly skipped |

`CAP-DOCS-documentation-ownership`, `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`,
`CAP-DOCS-document-search` and `CAP-DOCS-namespaces` are core inputs. Core also owns `CAP-TRACE-code-entrypoints` §1 and §§3.1–3.3 neutral declaration, liveness and reverse-lookup clauses;
lifecycle owns §§3.4–3.7 derivation, selection, apply and review plus applicable interface descriptions.
Lifecycle does not rewrite their identity,
relation or applicability policy. If their delivered contract cannot support L1–L4, return the concrete conflict to
the core owner before dependent implementation, with no silent local substitute.

## 2. Use cases plan

- `UC-plan-and-hand-off-a-proposal`: add a multi-role change and mechanism-only change selecting appropriate formal
  targets in the blueprint and plan. Preserve acceptance and handoff semantics.
- `UC-keep-the-living-spec-consistent`: extend structural reference and source-entrypoint regression scenarios for
  core-eligible formal documents and ineligible controls. Semantic source comparison remains in existing
  `CAP-DLV-delivery-workflows` review/reconcile boundaries rather than becoming a deterministic-rule claim.
- `UC-adopt-in-an-existing-repository`: route canonical design/domain/operations content and useful legacy detail
  to delivered formal destinations; repair identity/reference ingress without inventing history.
- `UC-adopt-sdd-from-adaptive-development`: demonstrate retained formal documents, missing-role gaps, evidence
  freshness and unchanged approach until existing activation authority is satisfied.

No additional use case or screen is needed: the actor goals and command/output surfaces already exist.

## 3. Architecture and decision impact

`ADR-formal-document-delivery-integration` selects consumer integration at existing boundaries with one core policy.
Its future ADR restates delivery impact obligations in the capability targets above. The core decision owns replacement
of the ID-free clauses of `ADR-documentation-ownership-and-linked-design-entries` and
`ADR-linked-domain-relationship-views`; this PADR does not separately supersede those clauses.

No package, feature, test tier or feature edge is added. The entrypoints feature already depends on
`devkit_docs.features.documents` and `devkit_docs.features.governance` in `.devkit/architecture.toml`.
The proposal scaffold is static guidance, so its existing docs.documents dependency is sufficient. Adaptive assets
consume public docs guidance and commands, with no Python dependency on `devkit_spec` or its private assets.

## 4. Source and runtime delivery plan

All following paths are under `packages/`; the matrix in materials expands scenarios and test ownership.

| Package / exact source suffix | Planned consumer integration |
| --- | --- |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-plan/SKILL.md | Include affected formal statements, IDs/source evidence, owner transfer and maintenance in invariants/impact/verification |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md | Review target-docs formal impact and source agreement in existing Planning procedure |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/SKILL.md | Review affected and unaffected formal responsibility assessment and complete maintenance against source |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja | Extend impact routing and reconciliation comparison to shared formal role ownership |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md | Reconcile affected formal docs, removed destinations, detail/support references and source agreement; no required mismatch waiver |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-entrypoints/SKILL.md and references/backfill.md | Consume core eligibility; review role-appropriate source anchors, preserve explicit selection and exclusion evidence |
| devkit-spec/src/devkit_spec/features/entrypoints/services/derive.py; usecases/apply.py; cli/commands.py; __init__.py | Audit existing generic behavior, update CAP/UC-only descriptions/help, make any required policy-consumption correction; preserve codes, outputs, atomicity and idempotence |
| devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py `_target_docs` | Add formal impact/applicability and maintenance sections to generated root target-docs, retaining targets metadata and existing sections |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja | Route current formal roles through shared docs instructions; keep full-ID and approach rules |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/brownfield-adoption/SKILL.md and references/migration.md | Include formal role inventory, destination selection and canonical maintenance |
| devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/SKILL.md and references/report-template.md | Include retained-role coverage, source evidence and required gap accounting |
| devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/documents.md and roles/documenter.md | Read, author and maintain shared formal roles; return source-specific evidence and conflicts, never introduce implicit SDD records |
| devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md; references/current-context.md; templates/current-context.md; AGENTS.md | Keep consumer pointers and retained-item map consistent; no forced document tree or approach switch |

Core owns docs bundle `instructions/living-spec-writing.md` responsibility/representation/reference sections,
`instructions/architecture-writing.md` boundary section, per-kind instructions/templates, `AGENTS.md` template
pointers, `seed/docs/README.md` hierarchy and bundle registration/distribution inventories. Lifecycle references these
assets; it introduces no second role/identity matrix. Installed projections are generated by ordinary sync during
Development; Planning edits no source or managed file.

Before source guidance changes, Development runs `uv run devkit get-context authoring` and applies
`agent-asset-writing`, as well as docs context and applicable writing instructions.

## 5. Before and after

| Surface | Current evidence at bde0a923192aaea7f6a467bb6a575db4ca447f9e | Required outcome |
| --- | --- | --- |
| Planning/scaffold | CAP/UC/architecture prompts | Affected formal IDs/actions/source evidence plus bounded unaffected reasons |
| Entrypoints | Runtime consults docs eligibility; help/skill assume CAP/UC | Core-eligible formal kinds derive/apply with role-appropriate anchors; unsupported kinds skipped |
| Reconcile/review | Generic targets with CAP/UC-centered author guidance | Required affected formal statements and maintenance compared with source |
| Adaptive | Behavior/structure/choice map | Complete warranted formal role map and maintenance, without SDD artifacts |
| Adoption | Formal role destinations omitted | Core destinations, canonical identity repairs and evidence gaps explicitly covered |

L1–L4 require the complete verification matrix in [integration contract](../../../docs/materials/2026-11/20261116-design-document-lifecycle/integration-contract.md).
Core/viewer completion is separate required milestone evidence; these comparisons claim no implementation pass.


## 6. Selected core interface dependency

[Core consumption record](../../../docs/materials/2026-11/20261116-design-document-lifecycle/core-interface-pin.md) pins source 504e2e12006ab3e2aad2b8ce470607646ad4c4ac and
verified content hash. Use flat canonical role IDs and peer independent details; parent-owned artifacts live under
PARENT-ID/artifacts. Same-kind rename/root moves carry that subtree and repair ordinary links; aliases do not
legalize old orphan folders. Split/cross-kind transfer assigns every retained artifact exactly one canonical
parent without stale duplicates. Retired nodes remain rule-checked; DESIGN retirement with source deletion
removes/replaces obsolete entrypoints in the same change and retains historical coordinates only as prose plus
commit. The composed global/package × SDD/adaptive scenarios in materials are mandatory. DESIGN has optional entrypoints; DOMAIN/OPS are explicitly ineligible. All three support
complete lifecycle operations, same-kind aliases, typed optional relations and retired identity without ADR
supersession fields. Consumer guidance points to the core definitions rather than copying an applicability matrix.
This is a reviewed future contract; delivered core runtime/assets are a prerequisite to Development handoff.
