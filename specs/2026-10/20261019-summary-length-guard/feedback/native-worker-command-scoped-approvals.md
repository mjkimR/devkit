---
id: FB-native-worker-command-scoped-approvals
title: Native Codex worker completes sibling-worktree mutations through command-scoped approvals
scope: upstream
kind: friction
category: missing-capability
target: Codex native subagent exec_command sandbox for sibling worktrees
skill: spec-delegate
agent: codex
origin: agent
severity: workaround
recurring: true
status: dismissed
created_at: 2026-10-19
---

# [FB-native-worker-command-scoped-approvals] Native Codex worker completes sibling-worktree mutations through command-scoped approvals

## 1. Friction / Question

- **Context**: an experimental native development worker ran a bounded bugfix in a sibling linked worktree with the base checkout as the session's writable root.
- **Expectation**: a delegated worker needs a concrete way to write its assigned files and commit its stage boundaries while retaining narrow authority.
- **Actual**: file-writing Python calls, scope-registry updates and normal Git commits executed successfully when each tool request used `sandbox_permissions=require_escalated`, an explicit worktree directory and a precise justification. No approval rejection was observed. There was no persistent worktree write grant demonstrated by these results.
- **Workaround (or Interpretation Chosen)**: request each mutation separately, keep the approved path scope explicit, and inspect the actual HEAD after the commit gate rewrites it. Independent nested reviewers used read-only calls and explicit worktree paths.
- **Suggestion**: document or provide a host-supported way to grant a native worker only its assigned worktree and required shared Git administration paths. Successful individual escalations do not establish general support for the managed worker contract.

## Diagnostic Details

- **Reproduction**: invoke a native subagent with a sibling-worktree assignment; issue bounded file writes, scope updates and stage commits through separately escalated exec calls.
- **Expected / Actual**: the worker needed mutation access; explicit command-scoped requests executed without changing host configuration or the base checkout.
- **Versions**: repository starting worker input head `471b19a`; native backend version unknown.
- **Conditions**: Codex native subagent, workspace-write, automatic approval reviewer, experimental emulation of the managed development-worker role, fixed allowed paths and no push or merge authority.
- **Workarounds Attempted**: precise escalation for each mutation succeeded. Privilege-free sibling writes were not retried in this worker; earlier parent preflight evidence was supplied as context, not reproduced here.
- **Related Assets**: `exec_command`, `development-worker`, `spec-delegate`, and the managed worker's unsupported Codex host status.

## Evidence

```text
request: workdir=<worktree>, sandbox_permissions=require_escalated
write: approved unit spec/plan/tasks only -> exit 0
scope update: SCOPE_ACK status=applied overlaps=0
normal commit: cgate Commit rewritten; subsequent rev-parse returned actual HEAD
independent code-reviewer and reconcile-reviewer: completed, no findings, HEAD unchanged
```

- **Disposition**: dismissed. The observation records experimental spike evidence regarding native subagent execution across sibling worktrees in Codex. Host-level support for persistent scoped worktree access is an upstream Codex platform capability, not a devkit repository defect.

