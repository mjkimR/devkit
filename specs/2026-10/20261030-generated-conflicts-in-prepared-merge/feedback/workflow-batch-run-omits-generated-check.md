---
id: FB-workflow-batch-run-omits-generated-check
title: The development guides omit the generated check before the batch test run
scope: repo
kind: change-request
category: other
target: docs/development/workflow.md, docs/development/ci-cd.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-workflow-batch-run-omits-generated-check] The development guides omit the generated check before the batch test run

Documentation drift outside the unit's write scope.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current**: `docs/development/workflow.md` and `docs/development/ci-cd.md` say that after a local-orchestrated run `just test-affected --base
  <batch start>` runs once on `main`. Since `ADR-generated-conflicts-in-prepared-merge`, the `spec-orchestrate`
  batch completion first runs `devkit generated check` and commits `devkit generated regen <ids>` for stale artifacts.
- **Proposal**: Add the regeneration step before the test run in both paragraphs.
- **Benefit**: The repository guide and the skill describe the same batch completion.

- **Disposition (resolved)**: `SPEC-generated-conflicts-follow-ups` names `devkit generated check`, and `devkit
  generated regen <ids>` with a commit for stale artifacts, before `just test-affected --base <batch start>` in
  `docs/development/workflow.md`, `docs/development/ci-cd.md` and the root `AGENTS.md` Verification paragraph,
  matching the `spec-orchestrate` batch completion (AC-04, verified by review of the three sentences).
