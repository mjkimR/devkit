---
reconcile_id: REC-lightweight-general-subagent
status: pending
targets:
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-design-exploration.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-role-worker-subagent.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconcile: `SPEC-lightweight-general-subagent`

## Changed contracts

| Document | Change | AC |
| --- | --- | --- |
| `CAP-DIST-agent-projections` | New "Shared General Subagent" section: the `role-worker` host table and rules 1 (projection per selected agent, no model or effort field) and 2 (role-file procedure), both enforced by `test_guide_bundle.py`. | AC-01, AC-03 |
| `CAP-DIST-content-packages` | The `devkit` bundle row names the `role-worker` subagent next to the distribution instructions. | AC-02 |
| `CAP-DLV-deep-research` | Rule 11 names `role-worker` for every role and the stop-and-report rule for a missing `role-worker`. | AC-04 |
| `CAP-DLV-uiux-improvement` | Rule 7 names `role-worker`, the running-UI `general-purpose` exception and the stop-and-report rule; it now cites its test. | AC-05 |
| `CAP-DLV-design-exploration` | Rule 3 names `role-worker`, the running-UI exception and the stop-and-report rule. | AC-06 |
| `CAP-HARN-agent-guidance` | Skill-local delegation guidance names the per-role subagent type, the `general-purpose` and commit-authority exceptions and the no-fallback rule, with the authoring test. | AC-07 |
| `ADR-role-worker-subagent` | The planned trace to `CAP-DIST-agent-projections` became a current reference; the decision is unchanged. | AC-01 |
| `docs/development/reference/distribution.md` | §4 lists `role-worker` among the `devkit` bundle's assets (Tier B extension restating `CAP-DIST-content-packages`). | AC-02 |

`ADR-skill-local-research-roles` and `ADR-package-ownership-and-release-version` already carry their partial
supersession pointers from the handoff; no further repair is needed.

## No-impact reasoning

- Use cases `UC-research-an-idea-and-shape-a-roadmap`, `UC-improve-an-interface-and-user-flow` and
  `UC-explore-a-design-problem` describe optional delegation at goal level and name no subagent type. A missing
  `role-worker` is an instance of their existing "delegation unavailable, report missing coverage" extensions, so
  their steps, extensions and postconditions hold unchanged.
- `docs/architecture/` names projection directories, not individual subagents; no structural element, package,
  feature or feature edge changed.
- The glossary already defines devkit bundles as shipping subagents; `role-worker` is an asset name, not a new domain
  term.
- `guides/` and `packages/devkit-dist/README.md` list no `devkit` bundle asset, so they need no change.

## Deferred work and feedback

- No source feedback is linked to this spec.
- Release notes that mention the new projection files belong to release preparation, not to this unit (Non-Goal 5);
  no in-scope work is deferred.
- The manual first-call token check (spec §6) is pending Host evidence in a fresh session after landing.

## Entrypoints

- Applied: `CAP-DIST-agent-projections` gains
  `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/subagents/role-worker.md`, the doorway to the shared
  subagent it now documents.
- Rejected: the catalog and authoring candidates for the delivery and harness capabilities. Their existing
  `SKILL.md` entrypoints stay the doorways; the edited orchestration and `roles.md` references are helpers, and the
  test paths and package-wide directories are not doorways. `CAP-DIST-content-packages` already lists
  `packages/devkit-catalog/src/devkit_catalog/`.
