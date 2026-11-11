---
reconcile_id: REC-remove-unused-cli-options
status: pending
targets:
  - file: docs/decisions/2026-11/20261111-remove-unused-cli-options-without-shims.md
    resolution: modified
  - file: docs/decisions/2026-11/20261111-single-local-landing-route.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-definitions.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
---

# Reconciliation: `SPEC-remove-unused-cli-options`

`ADR-remove-unused-cli-options-without-shims` records the no-shim removal of the six options and supersedes in part
the `--local-only` clause and follow-up of `ADR-single-local-landing-route`, which carries the matching pointer line
and keeps its decision text (AC-03).

`CAP-WT-task-worktrees` §3 keeps the network-free `finish` without the `--local-only` sentence; `CAP-INT-mcp-services`,
`CAP-COLL-work-scope-registry`, `CAP-DLV-delivery-workflows` and the integration and worktree references name
`devkit worktree finish <branch>` for the remaining cleanup (AC-01, AC-02). The host reference drops `--host` from
`host status` (AC-04); the rules reference drops `--summary-only` and the `[RULE_COUNTS]` line (AC-05).
`CAP-DLV-cli-and-output` drops `next --workflow` and `handoff --date` from the synopsis and attributes
`[BOUND_ELSEWHERE]` to library callers; `CAP-DLV-workflow-definitions` states that only the library evaluates against
an unbound definition file, that an unbound anchor follows the configured default and that `completed` is the date the
handoff ran; `CAP-DLV-workflow-orchestration` limits `--workflow` anchor resolution to `bind` (AC-06, AC-07).
`CAP-DOCS-document-lookup` drops the `--query` filter and points ID and title lookup at `devkit docs search` (AC-08).

The spec bundle text (`spec-integrate/SKILL.md.jinja`, `spec/references/worktree.md.jinja`,
`spec-orchestrate/references/git-operator-operations.md`) is agent guidance, covered by Task 2.2 and its sync output.
No use case, architecture document or glossary term changes: no use case step names a removed option. No work was
deferred and no source feedback was assigned.

Follow-up observation outside this unit's write scope: the devkit entry skill text in
`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/workflow_skill.py` still explains
`[BOUND_ELSEWHERE]`, which the CLI can no longer print; it stays accurate for library callers and was left unchanged.

Entrypoints are unchanged: every derived candidate joins the whole unit boundary (six features in four packages) with
each document; the documents changed only for the removed options and their existing doorways
still hold.
