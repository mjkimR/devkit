---
reconcile_id: REC-rename-incubation-to-adaptive-dev
status: resolved
targets:
  - file: docs/README.md
    resolution: modified
  - file: docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    resolution: modified
  - file: docs/architecture/ARCH-04-2-delivery-policy.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
    resolution: modified
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-delivery-classification.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-document-id-aliases.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-orchestration-workers.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-proposal-acceptance.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-roadmap-and-milestones.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-worktrees-branches-and-scope.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-merge-proposal-materials-per-leaf-at-handoff.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-adopt-sdd-through-an-evidenced-baseline-playbook.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-keep-incubation-guidance-opt-in-and-current-state-based.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-own-development-approach-policy-outside-sdd.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-adaptive-dev-approach-name.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-retain-research-as-cited-materials.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-split-deep-research-bundle.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/development/workflow.md
    resolution: modified
  - file: docs/proposals/README.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/steering/glossary.yaml
    resolution: modified
  - file: docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md
    resolution: modified
  - file: docs/usecases/delivery/UC-advance-an-idea.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
  - file: docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
    resolution: modified
  - file: docs/usecases/delivery/UC-route-development-intent.md
    resolution: modified
  - file: docs/usecases/harness/UC-adopt-in-an-existing-repository.md
    resolution: modified
---

# Reconciliation

The change renames names only; no rule, scenario or interface behavior changes (`SPEC-rename-incubation-to-adaptive-dev`
Non-Goal 2). Every target below is a Living Spec file whose current text named a renamed concept.

## Renamed documents

`CAP-DLV-adaptive-development`, `CAP-DLV-sdd-baseline-adoption`, `CAP-DLV-proposal-planning`, `UC-advance-an-idea`,
`UC-adopt-sdd-from-adaptive-development` and `UC-plan-and-hand-off-a-proposal` moved to their new paths with the new
ID, title and H1, and keep the old ID in `aliases` (`ADR-document-id-aliases`). Their bodies name the `adaptive-dev`
value and bundle, `/adaptive-dev`, `product-researcher`, `.devkit/adaptive-dev.md` and the renamed tests, and the
proposal capability says Planning. `CAP-DLV-adaptive-development` now also cites `ADR-adaptive-dev-approach-name` as
the owner of the names; its entrypoint follows the moved skill.

## References and prose

`devkit rules fix` rewrote every alias reference in current capabilities, use cases, ADRs and the listed `feedback/`
files to the canonical ID; plain-text old IDs in feedback prose and `target` fields were rewritten by hand, fenced
evidence and past file paths keep their recorded wording. Prose that named the approach, bundle or entry as current
was rewritten in `CAP-DLV-deep-research`, `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`,
`CAP-DLV-spec-bundles`, `CAP-DLV-workflow-orchestration` (the example workflow ID), `CAP-DIST-sync-and-transactions`
(value set, fix text, snapshot parsing and no compatibility reading), `CAP-GOV-spec-rules`, `CAP-HARN-agent-guidance`,
`CAP-INT-mcp-services` (`LIFECYCLE=omitted:adaptive-dev`), `UC-research-an-idea-and-shape-a-roadmap`,
`UC-route-development-intent`, `UC-adopt-in-an-existing-repository`, `ARCH-04-1-ecosystem-boundaries`,
`ARCH-04-2-delivery-policy`, `ARCH-05-2-components`, `ARCH-07-deployment`, `docs/development/workflow.md`,
`docs/development/reference/integration.md`, `docs/README.md` and `docs/proposals/README.md`. The split's
legacy-location mentions in `CAP-DLV-deep-research` stay. `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`,
`CAP-DOCS-namespaces`, `CAP-HARN-command-mount`, `CAP-HOST-lifecycle-observation` and
`UC-drive-development-to-integration` changed only by the canonical-ID rewrite.

## Decisions

`ADR-own-development-approach-policy-outside-sdd`, `ADR-keep-incubation-guidance-opt-in-and-current-state-based`,
`ADR-adopt-sdd-through-an-evidenced-baseline-playbook`, `ADR-retain-research-as-cited-materials` and
`ADR-split-deep-research-bundle` each gained one "Superseded in part by `ADR-adaptive-dev-approach-name`" line after
the statement whose name it replaces. The first two get it because `ADR-adaptive-dev-approach-name` names them in its
outcome, although `ADR-keep-incubation-guidance-opt-in-and-current-state-based` is itself superseded by
`ADR-extend-incubation-with-optional-discovery-teams`. The other three are accepted, not superseded ADRs whose outcome
names the value, bundle, entry or context file. `ADR-keep-discovery-plans-distinct-from-delivery-commitments` and
`ADR-extend-incubation-with-optional-discovery-teams` are superseded and named by no outcome, so they get none, and
`ADR-document-package` and `ADR-document-and-sdd-bundles` mention the old name outside their outcome. The other changed ADRs, including
`ADR-adaptive-dev-approach-name`, changed only by canonical-ID rewrites. Decision text is otherwise unchanged.

## Glossary

**Development approach** names `sdd` or `adaptive-dev`; **Adaptive development** is new with "incubation" under
Avoid; **Incubation current context** became **Adaptive-dev current context** (`.devkit/adaptive-dev.md`);
**Proposal Planning** is new with "proposal incubation" under Avoid. `glossary.yaml` adds both terms with
"incubation" as a search synonym.

## Deferred work and source feedback

The spec names no source feedback and defers no work. The two feedback files captured during Planning
(`FB-answer-envelope-has-no-decider`, `FB-rename-write-scope-unstated`) stay open for Backlog.

## Entrypoints

`devkit spec entrypoints derive` proposed broad package and test directories for every target, because the tasks'
boundaries span the whole rename. None was applied: each target changed only by names, and the three documents
whose entrypoint pointed at the moved skill (`CAP-DLV-adaptive-development`, `CAP-HARN-agent-guidance`,
`UC-advance-an-idea`) now name `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md`.
