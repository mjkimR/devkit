---
id: MAT-workflow-record-commit-planning
title: Workflow record commit Planning evidence
summary: "Source inspection and observed Git hook behavior supporting an explicit single-envelope commit command, with unimplemented runtime behavior identified."
created_at: 2026-10-30
---

# [MAT-workflow-record-commit-planning] Workflow record commit Planning evidence

## Inspection scope

Base: d85ce8c1. Planning began with ad442872 after the reviewing-status commit. All paths below are repository-relative.
No production code or scratch implementation was written. No external documentation was needed for repository-owned
contracts. Findings are source inspection or observed commits, not live evidence of the proposed command.

| Evidence | Observation | Design consequence |
| :--- | :--- | :--- |
| packages/devkit/src/devkit_agt/features/workflow/usecases/envelopes.py | WriteEnvelopeUseCase returns unit/file/kind/seq/status/skeleton; it does not commit. | Keep authoring stable; commit an existing path. |
| packages/devkit/src/devkit_agt/features/workflow/services/envelope/model.py | write_envelope allocates the next kind sequence; parsing and reference checks already exist. | Retry commit, not authoring; reuse parsing. |
| packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py | skeleton uses needs_input and an empty summary; authored status alone is not a provenance flag. | Require nonempty summary and valid stage/workflow/segment; do not invent a persisted skeleton marker. |
| packages/devkit/src/devkit_agt/features/workflow/services/evaluation/primitives.py | revision_ancestor compares two record head SHAs. | Do not rewrite evidence to the record commit SHA. |
| packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py | Committed source evaluation reads a completed final-report summary. | Commit records before integration preparation; keep existing stale-source handling. |
| packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md | A run records last work commit, then commits its worker envelope; problem record may require unfinished work. | Retain combined work/record commits and original emergency procedure. |
| Observed Git commits in this session | Gate rewrote e914fc0a to d85ce8c1 and e8ee7204 to ad442872. | Read actual post-hook HEAD; do not parse Git's initial progress SHA. |

## Alternatives and remaining validation

PADR-explicit-envelope-commits compares a separate command, authoring --commit, implicit commits and manual Git.
The separate command is recommended because one explicit input path handles both initial commit and retry.
Single-record scope intentionally leaves multi-record stages on their existing combined commit path.

Proposed Git failure handling, output codes and hook postconditions have not been implemented or exercised.
Development must validate AC1 through AC5, including real Git hooks and metadata rewrite, without disabling checks.
No time, cost or token improvement is claimed. Compare invocation with and without explicit commit mode at the same
implemented head; no worker must check out an earlier baseline commit.
