---
id: FB-integration-cleanup-stale-after-merge-rewrite
title: Integration cleanup rejects rewritten merge commit identity
scope: repo
kind: friction
category: tool-error
target: packages/devkit/src/devkit/integration/service.py
origin: agent
severity: workaround
recurring: true
status: resolved
created_at: 2026-10-21
---

# [FB-integration-cleanup-stale-after-merge-rewrite] Integration cleanup rejects rewritten merge commit identity

## 1. Friction / Question

- **Context**: Approved local MCP integration of one Development and one Planning branch.
- **Expectation**: The checked merge and scoped cleanup complete under the confirmed request.
- **Actual**: Merge completed, but cleanup stopped with INTEGRATION_REQUEST_STALE because the retained build SHA
  differed from the actual target SHA. The two commits had identical trees and expected source/target parents.
  Repository commit operations also visibly report post-commit SHA rewrites. This suggests a merge-hook interaction;
  the precise engine/hook ordering has not been traced.
- **Workaround**: Inspected refs, trees and clean status; a newly confirmed request recognized already_merged=true,
  skipped merge and completed worktree/branch/scope cleanup. No guard was bypassed, but another confirmation was needed.
- **Suggestion**: Establish which commit identity the merge operation actually installs after hooks and preserve
  exact provenance and policy checks. Add a regression for a metadata-only rewrite, and a negative case where
  tree or parent changes must still refuse cleanup. Do not broadly replace ancestry checks with tree equality.

## Diagnostic Details

- **Reproduction**: integration_integrate on two clean verified branches, native acceptance, then inspect the
  partial result and compare build.result with observed.target_sha. Repeated in the same retained server process.
- **Expected / Actual**: One approved merge/cleanup sequence versus successful merge followed by refused cleanup.
- **Versions**: Landed Development revision 769e0f516dfb7d02ccd02cbd39e2d901b4081bab; server process predated that merge.
- **Conditions**: Local no-ff integration, ask policy, repository commit gate with observed SHA rewriting.
- **Workarounds Attempted**: A new exact-scope native request completed remaining cleanup twice; retained stale
  requests were not forced or modified.
- **Related Assets**: CAP-INT-mcp-services; FB-post-commit-rewrite-stales-the-printed-hash records an earlier
  terminal observation about printed hashes, whereas this item concerns retained integration execution state.

## Evidence

```text
Development build.result=0ce517516b6a073bf1606232ffd1e0c3a4699656
observed.target_sha=769e0f516dfb7d02ccd02cbd39e2d901b4081bab
both tree=6281af041981631c0ba27291a777f2349cd43642
Planning build.result=818928472325aafcb98a5a8a16acef2c39bcd57b
observed.target_sha=4e06de18253c88a6624b10c16ce3f4794323e6f0
git diff --stat between each pair: empty
initial: merge=completed, worktree_remove=not_run, INTEGRATION_REQUEST_STALE
fresh approved cleanup: already_merged=true, merge=skipped, cleanup=completed
```

## Disposition

`SPEC-integration-rewritten-merge` records the immediately observed no-ff landing SHA only after equal tree and ordered-parent verification. The executable post-merge hook regression reproduces the original failure before the fix and completes cleanup after it. Negative content, parent, source, policy and later-resume rewrite cases preserve the guards. Independent code and reconciliation reviews passed; Host verification passed lint, types and 1,245 affected tests on the refreshed branch. This disposition verifies the implementation; integration is reported separately.
