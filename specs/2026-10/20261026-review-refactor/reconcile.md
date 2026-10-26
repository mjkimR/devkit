---
reconcile_id: REC-review-refactor
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-review-refactor.md
    resolution: modified
  - file: docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation: Maintenance review and refactoring playbook

The Living Spec states the delivered contract of `SPEC-review-refactor` under
`ADR-bound-review-refactor-runs-by-surface-batch`, `ADR-apply-approved-contract-removals-as-separate-work-items`,
`ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` and
`ADR-require-reachability-evidence-and-layered-placement`:

- `CAP-DLV-review-refactor` (new): entry and unattended stop, intake, surface batches, cross-surface assignment,
  following edits and receipt-owned exclusion, subagent review, findings with a named cost, dispositions and the
  decision round's authority (§3); reduction grounds, shared-implementation threshold, preservation evidence, helper
  placement, route and single-module test, direct mode with subagent edits and foreign dirty work kept, commits and
  verification, review, report and integration, contract removals (§4); the report interface (§5). Entrypoint: the
  playbook's `SKILL.md`.
- `UC-review-and-refactor-accumulated-slop` (new): the developer's goal, main scenario, extensions for missing scope,
  hosts without subagents, unconfirmed claims, unselected surfaces, contract mismatches, unattended runs, contract
  removals, single-module routing, out-of-scope subagent edits and exercises, with eight scenarios.
- `CAP-DIST-content-packages` §6: the third playbook, `upkeep` with `drift-reconciliation` and `review-refactor`,
  solo `refactoring`, `all` deploying three playbooks, the directory form.
- `CAP-DIST-context-and-playbooks`: lists the new use case (traceability link).
- `CAP-DLV-delivery-workflows` rule 1: a review-refactor work item spanning more than one feature or module is
  `overall-refactor` work, a single-module one follows the feature workflows, under the refining ADR.

Consumer mirrors (not Living Spec targets): `packages/devkit-catalog/README.md` preset table and maintenance section,
`guides/install/bundle-recommendations.md` maintenance row.

No impact: `docs/glossary.md` (no new domain term); `docs/architecture/` for resources (the resource taxonomy
already covers directory-form package playbooks; no new resource kind). The playbook adds no delivery stage.

Not reflected, outside the write scope: `ARCH-04-delivery-strategy` defines `overall-refactor` as a structural change
across the project and cites only `ADR-overall-refactor-workflow`; the refinement for review-refactor work items is
stated in `CAP-DLV-delivery-workflows` rule 1 and `CAP-DLV-review-refactor` §4.5. Aligning that architecture text belongs to the
Host with `FB-classification-maintenance-playbook-case`.

## Entrypoints

`devkit spec entrypoints derive` proposed the catalog README, the install guide, the bundle tests and the whole
`maintenance` package for each document; none was applied. `CAP-DLV-review-refactor` keeps the playbook's
`SKILL.md` as its doorway (narrower than the shared package), `CAP-DIST-content-packages` already declares the
package, and the README, guide and tests are hubs or tests, not doorways.

## Deferred work

- `FB-classification-maintenance-playbook-case`: the `spec` bundle classification criteria name no
  maintenance-playbook case (outside the write scope, `packages/devkit-spec/`).
- `FB-workspace-root-help-resolution-order`: finding RR-1 of the read-only sweep, pending a real decision round.
- `MS-maintenance-operations` (roadmap, outside the write scope) names the review and refactoring outcome; its status
  update belongs to the Host at integration.
