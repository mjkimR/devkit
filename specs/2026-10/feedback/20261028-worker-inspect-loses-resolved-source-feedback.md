---
id: FB-worker-inspect-loses-resolved-source-feedback
title: Worker inspection cannot resolve dated source feedback filenames
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

# [FB-worker-inspect-loses-resolved-source-feedback] Worker inspection cannot resolve dated source feedback filenames

## 1. Friction / Question (friction, question)

- **Context**: Host validation of a committed bugfix worker range whose source feedback files use the global dated filename layout.
- **Expectation**: Derived source-feedback scope identifies committed feedback by its frontmatter ID regardless of a filename's date prefix.
- **Actual**: Scope was not run because the first source FB ID resolved to zero feedback files. The lookup requires the filename stem to equal the ID suffix, so a dated filename fails before its frontmatter or status is checked.
- **Workaround (or Interpretation Chosen)**: Passed the original complete authorized boundaries with `--scope-file`; scope then passed with no outside paths.
- **Suggestion**: Resolve source feedback by frontmatter ID within committed feedback paths without requiring an undated filename stem. Keep uniqueness validation and the existing status-dependent write-scope policy.

## Diagnostic Details

- **Reproduction**: Run worker inspection without explicit scope on the completed input-recovery-notices worker range. A read-only probe of `derive_scope` with the same committed files and only the source's status overridden in memory to `open` still fails identically.
- **Expected / Actual**: Derived scope check passes / scope is not run with SPEC_WORKER_SCOPE_UNRESOLVED.
- **Versions**: Worker source head 00b24ea14a64a45efd3c33036d34bfb60439fc8d.
- **Conditions**: Source feedback is listed by full ID in the spec and named `YYYYMMDD-<slug>.md`; the failure is independent of open or resolved status. The original title attributed the observation to completion status before the filename predicate was checked; the stable FB ID is retained for traceability.
- **Workarounds Attempted**: Explicit complete scope file passed the same committed range.
- **Related Assets**: `SPEC-input-recovery-notices`; `devkit spec worker inspect`.

## Evidence

```text
Initial inspection: scope.status=not-run, code=SPEC_WORKER_SCOPE_UNRESOLVED
FB-integrate-asks-for-a-new-request-when-claims-are-missing resolves to 0 feedback files
Inspection with --scope-file: scope.status=pass, outside_scope=[]
Filename stem: 20261027-integrate-asks-for-a-new-request-when-claims-are-missing
Required stem: integrate-asks-for-a-new-request-when-claims-are-missing
Read-only derive_scope probe: open and resolved both raise the same WorkerScopeUnresolvedError.
```
