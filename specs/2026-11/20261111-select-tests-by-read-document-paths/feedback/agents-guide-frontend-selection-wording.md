---
id: FB-agents-guide-frontend-selection-wording
title: The repository agent guide still says a viewer frontend change selects no pytest test
scope: repo
kind: change-request
category: docs-mismatch
target: AGENTS.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-11
---

# [FB-agents-guide-frontend-selection-wording] The repository agent guide still says a viewer frontend change selects no pytest test

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The Verification section of `AGENTS.md` says "A viewer frontend change selects no pytest
  test: run the command its `[FRONTEND_CHECK: ...]` line names."
- **Proposed Procedure**: Say that a viewer frontend change also runs the command its `[FRONTEND_CHECK: ...]` line
  names, whether or not the selection includes pytest tests, matching `docs/development/ci-cd.md` after
  `SPEC-select-tests-by-read-document-paths`.
- **Expected Benefit**: The quick reference stays in step with the selector; an agent changing `scripts/viewer.sh`
  is not surprised that `test_viewer_script.py` runs.
- **Cost & Risk**: One sentence in the repository-owned part of `AGENTS.md`; no behavior change.
- **Attempted**: Not changed: `AGENTS.md` was outside the Development write scope of
  `SPEC-select-tests-by-read-document-paths`.

## Evidence

```text
AGENTS.md (Verification): "A viewer frontend change selects no pytest test: run the command its [FRONTEND_CHECK: ...] line names."
select(ROOT, ["scripts/viewer.sh"]) -> mode=partial, paths=(packages/devkit/tests/integration/package/test_viewer_script.py,), reason=frontend
```
