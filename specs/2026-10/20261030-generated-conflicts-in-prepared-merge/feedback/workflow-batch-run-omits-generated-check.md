---
id: FB-workflow-batch-run-omits-generated-check
title: The development workflow guide omits the generated check before the batch test run
scope: repo
kind: change-request
category: other
target: docs/development/workflow.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-workflow-batch-run-omits-generated-check] The development workflow guide omits the generated check before the batch test run

Documentation drift outside the unit's write scope.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current**: `docs/development/workflow.md` says that after a local-orchestrated run `just test-affected --base
  <batch start>` runs once on `main`. Since `ADR-generated-conflicts-in-prepared-merge`, the `spec-orchestrate`
  batch completion first runs `devkit generated check` and commits `devkit generated regen <ids>` for stale artifacts.
- **Proposal**: Add the regeneration step before the test run in that paragraph.
- **Benefit**: The repository guide and the skill describe the same batch completion.
