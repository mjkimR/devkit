---
id: FB-docs-list-status-unknown-for-valid-status
title: docs list --status open warns DOCS_LIST_STATUS_UNKNOWN when no feedback is currently open
scope: repo
kind: friction
category: tool-error
target: devkit docs list --status
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-docs-list-status-unknown-for-valid-status] docs list --status open warns DOCS_LIST_STATUS_UNKNOWN when no feedback is currently open

## 1. Friction / Question (friction, question)

- **Context**: A consumer worker ran `devkit docs list feedback --status open` in a repository whose feedback was
  all resolved or promoted.
- **Expectation**: `total=0` with no warning, because `open` is a defined feedback status.
- **Actual**: `DOCS_LIST_STATUS_UNKNOWN`: "no feedback document carries this status", with an action to pass one of
  the statuses that occur. The notice reads as a typo in the filter and sent the worker to check its command.
- **Workaround (or Interpretation Chosen)**: Treated as "none open".
- **Suggestion**: `CAP-DOCS-document-lookup` 3.4 specifies this notice for any status no indexed document shows,
  so the change is to that contract: check requested statuses against the kind's declared status set (the feedback
  template's values) and report the notice only for a value outside it; an empty result for a declared status
  needs no notice.

## Diagnostic Details

- **Reproduction**: In a repository with feedback records but none `open`, run
  `uv run devkit docs list feedback --status open`.
- **Expected / Actual**: Expected silent `total=0`; actual the notice.
- **Versions**: devkit `569379a06`: `_unknown_statuses` in
  `packages/devkit-docs/src/devkit_docs/features/documents/usecases/browse.py` compares with statuses present in the
  index, not declared ones; `test_a_status_only_stored_under_a_shown_one_is_unknown` asserts the notice for an
  empty valid status.
- **Conditions**: consumer repository.
- **Workarounds Attempted**: none needed.
- **Related Assets**: `CAP-DOCS-document-lookup`, `browse.py::_unknown_statuses`.

## Evidence

```text
browse.py: "DOCS_LIST_STATUS_UNKNOWN for the requested statuses that no indexed document of the wanted kinds ...
shows"; fix: "Pass one of the statuses these documents carry: ..."
```
