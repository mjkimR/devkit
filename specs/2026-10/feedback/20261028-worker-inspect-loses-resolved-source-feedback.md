---
id: FB-worker-inspect-loses-resolved-source-feedback
title: Worker inspection cannot derive scope after source feedback is resolved
scope: repo
kind: friction
category: tool-error
target: devkit spec worker inspect source feedback scope derivation
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-28
---

# [FB-worker-inspect-loses-resolved-source-feedback] Worker inspection cannot derive scope after source feedback is resolved

## 1. Friction / Question (friction, question)

- **Context**: Host validation of a committed bugfix worker range whose two source feedback files were resolved by the fix.
- **Expectation**: Derived source-feedback scope still identifies the committed files after their completion status update.
- **Actual**: Scope was not run because the first source FB ID resolved to zero feedback files; other inspection checks passed.
- **Workaround (or Interpretation Chosen)**: Passed the original complete authorized boundaries with `--scope-file`; scope then passed with no outside paths.
- **Suggestion**: Resolve source-feedback paths from the inspected committed tree including terminal feedback, while retaining status checks for actionable intake. Investigate which index filter caused the lookup failure before changing it.

## Diagnostic Details

- **Reproduction**: Run worker inspection without explicit scope on the completed input-recovery-notices worker range.
- **Expected / Actual**: Derived scope check passes / scope is not run with SPEC_WORKER_SCOPE_UNRESOLVED.
- **Versions**: Worker source head 00b24ea14a64a45efd3c33036d34bfb60439fc8d.
- **Conditions**: Source feedback is listed by full ID in the completed spec and changed from open to resolved on the branch.
- **Workarounds Attempted**: Explicit complete scope file passed the same committed range.
- **Related Assets**: `SPEC-input-recovery-notices`; `devkit spec worker inspect`.

## Evidence

```text
Initial inspection: scope.status=not-run, code=SPEC_WORKER_SCOPE_UNRESOLVED
FB-integrate-asks-for-a-new-request-when-claims-are-missing resolves to 0 feedback files
Inspection with --scope-file: scope.status=pass, outside_scope=[]
```
