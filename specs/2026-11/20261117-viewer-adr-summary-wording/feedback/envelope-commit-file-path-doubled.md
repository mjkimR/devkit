---
id: FB-envelope-commit-file-path-doubled
title: envelope commit joins a workspace-relative --file to the unit and its fix repeats the failing path
scope: repo
kind: friction
category: tool-error
target: devkit workflow envelope commit
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-17
---

# [FB-envelope-commit-file-path-doubled] envelope commit joins a workspace-relative --file to the unit and its fix repeats the failing path

## 1. Friction / Question (friction, question)

- **Context**: Committing `review-01.yaml` after `devkit workflow envelope review` printed
  `[ENVELOPE: envelopes/review-01.yaml ...]`.
- **Expectation**: `--file` accepts the workspace-relative path of the envelope, or the advisory's fix names a form
  that works.
- **Actual**: `--file specs/<unit>/envelopes/review-01.yaml` was joined to the unit, giving
  `[TARGET] specs/<unit>/specs/<unit>/envelopes/review-01.yaml`, and the `[FIX]` line told the agent to rerun with
  the same workspace-relative `--file` value.
- **Workaround (or Interpretation Chosen)**: Passed the unit-relative `--file envelopes/review-01.yaml`, which
  committed.
- **Suggestion**: Accept a workspace-relative path that already starts with the unit directory, or make the `[FIX]`
  line name the unit-relative form the `[ENVELOPE: ...]` line prints
  (`packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py`).
