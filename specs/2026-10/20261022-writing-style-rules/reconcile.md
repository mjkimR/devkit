---
reconcile_id: REC-writing-style-rules
status: resolved
targets:
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
---

# Reconcile: `SPEC-writing-style-rules`

- `ARCH-08-2-resource-taxonomy`: the `skill-authoring` preset sentence names `RULE-agent-asset-wording` as the check
  of the instruction's mechanical part.
- `CAP-DIST-content-packages` and the distribution reference: the `authoring` bundle row lists the wording rule.
- Rules reference: the authoring table lists the rule, its scope and guide.
- `CAP-GOV-rules-engine`: the authoring bundle sentence names the wording rule and the instruction.
- Outside `docs/`, kept in step: the consumer install guide (`guides/install/bundle-recommendations.md`) and the
  `devkit` package README name the wording rule.
- The guidance test helper is test support only; no Living Spec document describes the test layout.
- `CAP-GOV-rule-authoring` needs no change: the rule follows its bundle-owned rule contract unchanged.

## Source feedback

- `FB-writing-style-rules`: resolved (rule, guide, tests, review round, clean hygiene run).
- `FB-guidance-tests-pin-line-layout`: resolved (shared reader, rewrap experiment, review round).
- `FB-parallel-pruning-cuts-both-owners`: dismissed on this branch by the user's decision; not a source.

## Entrypoints

`devkit spec entrypoints derive` proposed 11 paths for `CAP-DIST-content-packages`; all are rejected: the bundle
touched that capability only for one row of its package table, and the paths belong to the authoring bundle and the
spec bundle tests, not to the content-package contract.
