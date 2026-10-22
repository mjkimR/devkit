---
reconcile_id: REC-integration-rewritten-merge
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
---

# Reconciliation

`CAP-INT-mcp-services` now states immediate post-hook no-ff equivalence, recorded landed identity, ff-only exclusion and strict resume ancestry. The existing integration directory entrypoint covers the changed service; test-file candidates are not runtime entrypoints.

`CAP-WT-task-worktrees` needs no change: its finish validation retains exact result ancestry and source identity semantics; no worktree code or public interface changed. Reference guides remain accurate because their command and API surfaces are unchanged. No architecture, ADR or new term changes are needed.

## Source feedback disposition for the Host

`FB-integration-cleanup-stale-after-merge-rewrite` is directly addressed: an executable Git post-merge hook reproduces stale cleanup before the fix, and now completes using the equal-tree, equal-ordered-parent replacement. Negative content, parent, source and policy cases retain the worktree and branch; interrupted cleanup resumes from the adopted identity. The Host validated the committed worker range, reran lint, types and 1,245 affected tests after incorporating the current base, and resolved the external source feedback with that evidence. No assertion of integration is made.

## Deferred work

None. The specific installed external hook responsible for the original host incident was not inspected; real Git hook ordering and the characterized transformation were reproduced in isolated repositories. Retained server processes require reload to use changed imported Python code.
