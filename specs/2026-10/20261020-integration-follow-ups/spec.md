---
id: SPEC-integration-follow-ups
title: 'Integration base advances: merge commits, effective policy digest and readiness on the result'
summary: 'Lets an approved local integration absorb target commits that land during its confirmation: tasks land as merge commits built outside the base checkout, the approval binds the effective integration policy instead of raw file bytes, and readiness runs again on the merged result.'
status: planned
created: 2026-10-20
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-WT-task-worktrees
  - CAP-DLV-delivery-workflows
  - CAP-DLV-project-policy
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-integration-follow-ups] Integration base advances: merge commits, effective policy digest and readiness on the result

## 1. Problem Statement & Motivation

Handed off from proposal PROP-integration-follow-ups on 2026-10-20.

- **Preserved Materials**: `docs/materials/2026-10/20261020-integration-follow-ups` (the option comparison of
  Planning).
- **Decisions**: `ADR-merge-commit-outside-checkout`, `ADR-effective-policy-digest` and
  `ADR-target-advance-readiness`, promoted at the handoff; `ADR-integration-approval-asserted` stays in force.
- **Split in Planning**: this spec keeps the base advances. Pull request cleanup is
  `PROP-integration-pull-request-cleanup` and host confirmation `PROP-integration-host-confirmation` (both drafts);
  automatic dispatch stays the open feedback `FB-auto-integration-dispatch`, since no policy grants merge or deletion
  authority under `ADR-integration-approval-asserted`.

`SPEC-hook-driven-integration-cleanup` shipped approval-bound local integration under `dev-integration = ask`. An
accepted `integration_integrate` confirmation is refused with `INTEGRATION_REQUEST_STALE` whenever another activity's
commit lands on the target during the confirmation (`FB-integration-stale-on-base-advance`), for three reasons:

- **Raw receipt digest**: the request binds the raw bytes of `.devkit/config.toml` and `.devkit/installation.json`;
  the receipt lists every managed asset hash, so any bundle edit on the target voids every open confirmation though
  no integration policy changed.
- **Fast-forward only**: the request fixes `merge_method: ff-only` and `devkit worktree finish --merge` runs
  `git merge --ff-only`, so any advance makes the merge impossible (`WORKTREE_MERGE_NOT_FF`).
- **Exact target binding**: readiness evidence and `validate_finish` bind the exact target SHA, so each retry is a
  new confirmation that can be overtaken again on a busy base.

With this change an approval binds the approved source, the confirmation target and its descendants within one call:
the task lands as a merge commit built in the object store, under an unchanged effective policy, with readiness
checked again on the merged result, without a second confirmation.

### Source feedback

- `FB-integration-stale-on-base-advance` (specs/2026-10/20261019-high-effort-review-loop): delivered by this spec.
- `FB-auto-integration-dispatch` (specs/2026-10/20261017-hook-driven-integration-cleanup): open, split out in
  Planning; not delivered here.
- `FB-multi-host-integration-ergonomics` (same directory): promoted to `PROP-integration-host-confirmation`; not
  delivered here.
- `FB-pr-remote-and-squash-integration` (same directory): promoted to `PROP-integration-pull-request-cleanup`; not
  delivered here.

## 2. User Stories

- **US-1**: As the user approving a local integration, I want one confirmation to land the approved work even when
  other tasks land on the target meanwhile, so that I am not asked again for the same change.
- **US-2**: As the integrating agent, I want a refusal to change nothing on the target and to name a SHA-preserving
  fix, so that I can recover within the existing authority.
- **US-3**: As a project maintainer, I want the history to keep one first-parent line per task with every recorded
  SHA reachable, or linear history when I configure it.

## 3. Non-Goals

1. **Scope Excluded**: automatic dispatch under `dev-integration = auto` (`authority="policy-auto"`).
   - **Rationale**: no policy grants merge or deletion authority (`ADR-integration-approval-asserted`).
   - **When to Reconsider**: the user decides on `FB-auto-integration-dispatch`.
2. **Scope Excluded**: remote push, pull request merge or cleanup after a pull request, and squash or rebase
   integration (`PROP-integration-pull-request-cleanup`).
3. **Scope Excluded**: new host confirmation adapters (`PROP-integration-host-confirmation`) and any change to
   `devkit.host` (packages/devkit-dist).
4. **Scope Excluded**: an `ff` merge method (a merge commit only when needed), squash or rebase as local options, an
   in-call retry when the target moves between a build and its fast-forward, and running tests on the merged result.
5. **Scope Excluded**: approval lifetime beyond the approving call: `integration_resume` never absorbs a later target.

## 4. Acceptance Criteria & Behavioral Contracts

Fixtures are disposable Git repositories with a configured fixture readiness provider. "Nothing changed on the
target" means the base branch ref, the base working tree and the source branch are as before the call.

### [AC-01] Merge commit by default when the target did not advance

- **Given** a prepared task branch whose tip contains the target and `[worktree] merge` unset in both policies
- **When** the user approves `integration_integrate`
- **Then** the base branch points at a new commit whose first parent is the confirmation target, whose second parent
  is the approved source tip, whose tree equals the source tree and whose message is
  `chore(merge): integrate <branch> into <target>`; the result reports `merge_method: no-ff`, the confirmation target,
  the build target and the result commit; the worktree is removed and the branch deleted with `git branch -d`

### [AC-02] ff-only policy keeps linear history

- **Given** `[worktree] merge = "ff-only"` in the base's or the source's policy
- **When** the user approves an integration whose target did not advance
- **Then** the base fast-forwards to the source tip with no new commit and the request reports `merge_method: ff-only`
- **And When** the target advanced during the confirmation
- **Then** the call reports `WORKTREE_MERGE_NOT_FF` and nothing changed on the target

### [AC-03] A clean target advance during the confirmation is merged in

- **Given** a commit lands on the target during the confirmation and merges cleanly with the source
- **When** the user approves
- **Then** the service builds the tree with `git merge-tree --write-tree`, runs the finish guards with
  `merge-base(build target, source)` and the source tip, runs the readiness provider with the execution context
  (source, build target, result), and lands a merge commit whose first parent is the build target; the result
  reports the confirmation target and the build target as different SHAs

### [AC-04] A conflicting advance changes nothing

- **Given** a target commit that conflicts with the source lands during the confirmation
- **When** the user approves
- **Then** the call reports `WORKTREE_MERGE_CONFLICT` whose `[FIX]` merges the target into the branch in its
  worktree, re-verifies and prepares again; the merge step is `failed`, nothing changed on the target and the
  worktree remains

### [AC-05] Build failures are refused before anything lands

- **Given** an advanced target and Git older than 2.38 (probed only on this path)
- **When** the build runs
- **Then** it reports `WORKTREE_GIT_UNSUPPORTED` and nothing changed on the target
- **And Given** `git commit-tree` fails or exceeds its 30-second bound (a failing signature program)
- **Then** it reports `WORKTREE_COMMIT_FAILED` and nothing changed on the target
- **And Given** no committer identity is configured under `merge = "no-ff"`
- **Then** `prepare` (and `devkit worktree finish --merge` before any change) refuses with `WORKTREE_COMMIT_FAILED`

### [AC-06] Target descent and compare-and-swap

- **Given** the target was reset to a commit that does not descend from the confirmation target
- **When** the approved call builds
- **Then** it reports `INTEGRATION_REQUEST_STALE` and nothing changed
- **And Given** the base branch moves after the build and before its fast-forward
- **Then** it reports `INTEGRATION_TARGET_MOVED`, the merge step stays `not_run` and nothing changed on the target

### [AC-07] Effective policy digest

- **Given** a target commit during the confirmation that changes only `.devkit/installation.json` asset hashes and
  bundle files
- **When** the user approves
- **Then** the integration completes (no `INTEGRATION_REQUEST_STALE`)
- **And Given** the advance changes `[workflow.approvals] dev-integration`, `[worktree] pull_request`,
  `delete_branch` or `merge`, or `[integration] provider`
- **Then** the call reports `INTEGRATION_REQUEST_STALE` and nothing changed on the target

### [AC-08] Receipt records the merge makes inconsistent

- **Given** an advanced target where the merged `.devkit/installation.json` records a hash for a tracked path that
  matches neither parent's (record, blob) pair and does not match the merged blob, or the merged receipt does not parse
- **When** the build checks the result
- **Then** it reports `INTEGRATION_RECEIPT_CONFLICT` and nothing changed on the target; a record whose path is
  untracked in the result, or whose pair equals a parent's, is skipped

### [AC-09] Readiness on the result and provider declarations

- **Given** a provider whose `Readiness` omits the result-check disclosure, or whose disclosure is not one line of 1
  to 200 characters
- **When** `prepare` runs
- **Then** it reports `INTEGRATION_PROVIDER_FAILED`
- **And Given** an approved request whose provider returns, at the build, evidence that differs from the approved
  evidence in a code not declared target-bound, or any reason
- **Then** the call reports `INTEGRATION_REQUEST_STALE` (changed evidence) or `INTEGRATION_NOT_READY` (reasons) and
  nothing changed on the target

### [AC-10] Confirmation text

- **Given** a prepared no-ff request
- **When** the confirmation form is built
- **Then** it starts with `Approve local integration of "<branch>" into "<target>" with a merge commit?`, shows the
  confirmation target SHA, states that later target commits are merged in without another confirmation only if the
  merge is clean, the integration policy is unchanged and readiness provider `<provider>` passes again on the merged
  result, followed by the provider's disclosure, and states that otherwise nothing changes on the target;
  `approval_scope()` and `to_dict()` carry the configured `merge_method`

### [AC-11] Already merged sources

- **Given** a task branch the target already contains (after a completed no-ff merge)
- **When** `devkit worktree finish --merge` reruns
- **Then** no commit is built and only the cleanup continues
- **And When** `integration_integrate` prepares it
- **Then** the request is cleanup-only: the form says the branch is already merged and lists only the cleanup, the
  merge step is `skipped`, guards and readiness run with `merge-base(target, source)` (the source), and execution
  removes the worktree and branch without a build
- **And Given** a branch the target neither contains nor is contained in
- **Then** `prepare` reports `WORKTREE_MERGE_NOT_FF`, whose `[FIX]` merges the target into the branch (no rebase)

### [AC-12] Approval lifetime and the integration lock

- **Given** another devkit executor holds the Git common-directory integration lock when the user approves
- **When** it is released within the approving call's lock wait
- **Then** the build runs; **When** it is not, the call reports `LOCK_HELD` with nothing changed, and its `[ACTION]`
  names `integration_resume` while the target still equals the confirmation target, else a new
  `integration_integrate`
- **And When** `integration_resume` meets a held lock
- **Then** it refuses at once with `LOCK_HELD`
- **And Given** an approved request whose approving call ran a build and the target moved after it
- **When** `integration_resume` is called
- **Then** it reports `INTEGRATION_REQUEST_STALE` without building onto the later target; a request whose approving
  call ran no build resumes only while the target equals the confirmation target

### [AC-13] Recovery after a failed or unknown merge step

- **Given** a merge step left `unknown` or `failed`
- **When** `integration_resume` inspects the base
- **Then** a base that contains the latest result commit (the source under `ff-only`) is treated as merged and
  cleanup continues without a second merge; a base equal to the last build target is not merged and the fast-forward
  is retried; any other base is `INTEGRATION_REQUEST_STALE`
- **And** after the merge every step accepts later commits on the base as long as it contains the result

### [AC-14] CLI finish --merge

- **Given** `devkit worktree finish <branch> --merge` under the default policy and a target that is an ancestor of
  the branch
- **When** it runs
- **Then** the base fast-forwards to a devkit-built merge commit (first parent the old base HEAD, tree the branch
  tree); under `ff-only` it fast-forwards to the tip; an advanced target is `WORKTREE_MERGE_NOT_FF` with nothing
  changed; it takes the Git common-directory integration lock (`LOCK_HELD` when another executor holds it)
- **And Given** `[worktree] merge` set to any value other than `"no-ff"` or `"ff-only"`
- **Then** commands reading the table report `WORKTREE_CONFIG_INVALID`

### [AC-15] Push-rejected fix keeps the unit's SHAs

- **Given** a base whose upstream moved on so the push after a merge commit is rejected
- **When** `WORKTREE_PUSH_REJECTED` is reported
- **Then** its `[FIX]` no longer runs `git pull --rebase`; a fixture shows the command it names keeps every source
  commit SHA as an ancestor of the base after integrating the upstream

### [AC-16] devkit-spec readiness provider on the result

- **Given** the spec readiness provider
- **When** it checks a unit or session task
- **Then** it declares `TARGET_SHA` and `RESULT_SHA` target-bound and the disclosure
  `CI rules only on the merged result; tests and review ran on the source only`; it adds `SPEC_POLICY` (a digest of
  the parsed `[tool.spec]` of the build target and the result, or the source before a build), which is not
  target-bound; with a result commit it runs the CI rules on the result tree with the diff from the build target, and
  a target change inside the unit directory since the merge base is a reason

### [AC-17] devkit-spec scoped cleanup after a merge commit

- **Given** an integration that landed a merge commit and removed the worktree
- **When** the spec cleanup validates and runs its targets
- **Then** it treats the base as post-merge when HEAD contains the result commit (the source under `ff-only` or for a
  cleanup-only request), so later commits on the base do not make it refuse

## 5. Assumptions

- The approving call's lock wait is 20 seconds, below the 30-second upper bound Planning named: Codex's default MCP
  `tool_timeout_sec` is 60 seconds, and a 20-second lock wait plus the 30-second `commit-tree` bound leaves time for
  readiness on the result. A host whose timeout cuts the call leaves the request inspectable with
  `integration_status`.
- `prepare` runs the readiness provider without a result commit; `IntegrationContext.result_sha` is `None` there and
  set at each build. The execution context replaces `finish.target_sha` with the build target.
- The provider declares its target-bound codes and disclosure in the `Readiness` it returns (`target_bound`,
  `disclosure`); both are part of the approved readiness and so of the request digest.
- After the merge, the policy check compares the base's current effective policy with the approved post-merge policy
  (the target's at `prepare` for a cleanup-only request).
- The project root of the integration service is the repository root (as today), so `.devkit/` paths in commits are
  repository-relative.
- The build reuses `WORKTREE_MERGE_FAILED` for a `git merge-tree` exit status other than 0 or 1.

## 6. Security, Privacy & Compliance Considerations

- No new authority: the approval still binds the repository, task, source branch and SHA, the confirmation target and
  its descendants within one call, cleanup scope, effective policy, target-bound evidence codes and the disclosure.
- The merge commit message is composed from validated branch names only; no caller text reaches it.
- No network operation is added; `commit-tree` never prompts (`GIT_TERMINAL_PROMPT=0`).
