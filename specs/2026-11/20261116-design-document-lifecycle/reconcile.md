---
reconcile_id: REC-design-document-lifecycle
status: pending
targets:
- file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md
  resolution: modified
- file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
  resolution: modified
- file: docs/decisions/2026-11/20261116-formal-document-delivery-integration.md
  resolution: modified
- file: docs/materials/2026-11/20261116-design-document-lifecycle/development-evidence.md
  resolution: modified
- file: docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md
  resolution: modified
- file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
  resolution: modified
- file: docs/usecases/governance/UC-keep-the-living-spec-consistent.md
  resolution: modified
- file: docs/usecases/harness/UC-adopt-in-an-existing-repository.md
  resolution: modified
- file: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/AGENTS.md
  resolution: modified
- file: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md
  resolution: modified
- file: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/current-context.md
  resolution: modified
- file: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/documents.md
  resolution: modified
- file: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/roles/documenter.md
  resolution: modified
- file: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/templates/current-context.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/brownfield-adoption/SKILL.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/brownfield-adoption/references/migration.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/SKILL.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/references/report-template.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-entrypoints/SKILL.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-entrypoints/references/backfill.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-plan/SKILL.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/SKILL.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja
  resolution: modified
- file: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md
  resolution: modified
---

# Formal document lifecycle reconciliation

## Ownership and current source agreement

`CAP-DLV-proposal-planning` owns change-specific formal impact prompts and generated blueprint behavior.
`CAP-DLV-delivery-workflows` rules 9 and 15 own existing review/reconcile obligations and source-agreement
comparison. `CAP-DLV-adaptive-development` owns source-identified documenter/current-context maintenance without
implicit SDD records. `CAP-DLV-sdd-baseline-adoption` owns retained coverage/gaps/evidence freshness. The accepted
`ADR-formal-document-delivery-integration` now traces these implemented clauses and their actual verification.

`CAP-TRACE-code-entrypoints` §§3.4–3.7 consumes shared core eligibility and describes reviewed DESIGN mechanism
anchors. CAP/UC doorway/whole-package heuristics remain review guidance; DESIGN may use a bounded mechanism
directory excluding unrelated shared paths. Generic runtime safe-path, selector, atomicity and output semantics
stay unchanged. No typed Kind policy, registry or cross-feature edge is duplicated. Core §§1,3.1–3.3 is unchanged.

Existing use-case flows/examples now include formal impact selection, canonical brownfield destinations, required
baseline formal gaps/stale source, eligible DESIGN derivation and same-change retirement anchor repair. The structural
consistency use case makes no semantic drift-engine claim. Domain meanings, distribution/recovery guarantees and
operational action permissions have no owner transfer. Canonical five role examples and glossary/architecture
subjects remain unchanged; their responsibilities warrant no empty edits.

## Source guidance and distribution

All changed SDD/adaptive agent assets are targets, alongside their normative capability/use-case/ADR owners.
Core docs supplies neutral per-kind writing/templates/schema; each approach extends only its own existing bodies,
source-identified assignments and maintenance procedure. Installed guidance agrees after native sync; only tracked
sync output .devkit/installation.json changed and is annotated Task1. Managed/projected files were never hand-edited.
No TierB scope extension was used. The existing spec UX inventory assertion was formatted to satisfy owned-package
lint, with no semantic change. No public CLI flag, error code, JSON key or selector contract changed.

## Entrypoints and verification

Entrypoint derivation is reviewed for this unit before apply. Broad package task boundaries create cross-product
candidates for documentation owners changed for procedure/wording; they do not establish an appropriate reading
start. Existing exact owning entrypoints remain useful, so no broad new package anchor is applied. Actual DESIGN
ID/alias/file/directory apply, body preservation, idempotence and ineligible/metadata-only controls are exercised
separately in real new-kind tests. Ineligible roles never acquire fabricated anchors.

The [development evidence](../../../docs/materials/2026-11/20261116-design-document-lifecycle/development-evidence.md)
separates source-identified author/reviewer comparison from scripted procedure proof. The kind × approach × root
matrix executes composed canonical/artifact maintenance and staged orphan/deleted-source negatives. SDD additionally
checks resolved modified/deleted canonical/support targets and unchanged-target native rejection. Explicit author
comparison detects omitted impact; native reconciliation validates declared diff evidence and does not discover
reverse impact. Adaptive preserves effective approach and pre-existing SDD history bytes with no implicit Unit,
envelope or gate. Baseline source-invalidation and required formal gaps remain unready until rechecked.

Code review round1 found three issues; all were fixed, and fresh independent round2 verified six focused regressions,
nine strengthened SDD E2E and22 rules. Frozen source b691875efb19cf504997e23c04657bcf32dfdf8f passed developer
1878 affected unit/integration tests and sync check. Earlier unchanged adaptive/baseline matrix and installed-wheel
consumer evidence remains recorded; source-specific exact commands/outcomes are in envelopes. Reconciliation remains
pending until its separate HIGH reviewer verifies this whole reflection.

## Required later work

`PROP-design-document-viewer` remains the required V1–V4 owner for presentation/public/static/handbook integration.
Its accepted destination exists. No L1–L4 requirement or known implementation defect is deferred; this phase does
not claim milestone completion. The Host retains integration and final landed-head verification.
