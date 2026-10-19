---
id: MAT-codex-native-worker-evidence
title: Codex native worker execution evidence
summary: "Native Codex Development and Planning workers use command-scoped approvals and nested reviews with emulated contracts. Recorded runtime evidence distinguishes operation-specific access from persistent permission and host confinement."
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

## Native Planning execution

- Invocation: this proposal's real `collaboration.spawn_agent` Planning worker, generic role explicitly following
  the managed Planning contract under experimental authorization. The spawn mechanism is native and the worker
  contract emulated; no `codex exec` ran and no source support contract was changed during Planning.
- Input head: `bca2bb23244100a1ca23a53033892a394d10afad`. Required reviewing commit passed the normal gate and became
  `004971b70dd0814f44b31a44a96771aceba8e0ad` after rewriting. Later actual heads are returned by the worker record.
- The worker settled support status, trust/role fallback, scoped approvals, refusal preservation and verification
  scope in `PADR-codex-native-worker-execution` and `MAT-codex-native-worker-design`.
- A fresh nested challenger completed with no findings; its record is `envelopes/challenger-01.yaml`. The caller
  checked that HEAD, index and draft paths were unchanged by the read-only role. The review covers the draft
  proposal, PADR and design material at its recorded head plus those uncommitted drafts; later evidence/record edits
  are self-verified by the worker and are not represented as challenger-reviewed.
- Every mutation requested a separate, narrowly scoped approval with the explicit sibling-worktree cwd. Approvals
  succeeded; no automatic rejection occurred. Fresh feedback and exactly one worker envelope complete the return.
- The Host must still validate final ancestry, allowed paths, clean worktree and unchanged base. The worker's actual
  final HEAD is supplied after the record commit; this material does not pre-approve that Host validation.

## Remaining verification

- Native Planning execution is recorded here; committed-return acceptance remains the Host's check.
- Generic-role success does not establish named-role loading in a newly started host.
- Denied approval, unavailable approval tools, failed emergency commits and other host/version configurations
  were not exercised. The support contract must state those limits.
- Prior cross-host research remains in Git at `1b8478093a44cf2d0b74c412bffc93f259459ef0` under
  `docs/proposals/PROP-worktree-host-compatibility/`. Its process-worker direction has been retired by Backlog.
