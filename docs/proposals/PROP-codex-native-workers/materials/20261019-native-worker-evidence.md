---
id: MAT-codex-native-worker-evidence
title: Codex native worker execution evidence
summary: "A native Codex Development worker completed a scoped change with command-scoped approvals and nested reviews; default sandbox probes identify the permissions that approvals supplied."
---

# [MAT-codex-native-worker-evidence] Codex native worker execution evidence

## Verified Development run

- Source: `SPEC-summary-length-guard`, integrated locally at `1b8478093a44cf2d0b74c412bffc93f259459ef0`.
- Invocation: fresh-context `collaboration.spawn_agent`, generic role explicitly following the worktree's managed
  development-worker contract. The role was emulated; no `codex exec` ran.
- Input head: `471b19a0245bee80240dc68174e976b8add747ea`; last work head:
  `8a86e6de0dfb8145927a6f2179cff20949033b26`; final head:
  `1b8478093a44cf2d0b74c412bffc93f259459ef0`. Host verified ancestry, allowed paths, clean return and unchanged base.
- Stages included characterization, plan/tasks, Red, fix/Green, independent nested code and reconcile reviews,
  feedback, final report and a committed worker envelope.
- Red: six expected failures, seventeen passes. Green: twenty-three passes. Host full suite: 3,563 passed,
  fourteen skipped. Lint, types, package build and cumulative rules passed; both reviews had no findings.
- After user approval, Host integrated locally and removed the worktree/branch. No remote push occurred.

## Observed permissions

- Default cwd was the base checkout; explicit command cwd worked in a linked fixture worktree.
- Default access denied a write-mode open of the real base `.git/index` and creation of a directory beside the
  base. The index probe wrote zero bytes. A fixture under `/private/tmp` could commit, so that success alone did
  not establish real sibling/Git access.
- The same native subagent's approved `require_escalated` call could open that index without writing bytes and
  create a disposable sibling fixture with a linked worktree and commits. Cleanup succeeded; real HEAD/status
  stayed unchanged.
- The real worker used individual approved calls for source/unit writes, scope updates and normal commits.
  No automatic review rejection occurred. Sandboxed dependency-metadata DNS failures resolved through approved
  verification reruns. These outcomes establish operation-specific success, not persistent authority.

## Remaining verification

- Native Planning with a nested challenger has not yet been run.
- Generic-role success does not establish named-role loading in a newly started host.
- Denied approval, unavailable approval tools, failed emergency commits and other host/version configurations
  were not exercised. The support contract must state those limits.
- Prior cross-host research remains in Git at `1b8478093a44cf2d0b74c412bffc93f259459ef0` under
  `docs/proposals/PROP-worktree-host-compatibility/`. Its process-worker direction is being replaced.
