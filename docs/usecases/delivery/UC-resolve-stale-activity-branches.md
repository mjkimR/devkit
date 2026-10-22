---
id: UC-resolve-stale-activity-branches
title: Resolve Stale Activity Branches
summary: "An AI coding agent reports the plan-* and dev-* branches idle beyond [worktree] stale_after, with their resume and discard paths, and resumes, discards or keeps each one only as the user decides, deleting nothing on its own."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - User (decides to resume, discard or keep each stale branch)
  - GitHub (`gh` authentication and pull request activity)
status: active
created_at: 2026-10-22
capabilities:
  - CAP-WT-task-worktrees
  - CAP-GOV-evaluation-lifecycle
  - CAP-HARN-agent-guidance
---

# [UC-resolve-stale-activity-branches] Resolve Stale Activity Branches

## 1. Goal

- **Goal**: The agent finds the activity branches nobody has moved for longer than the project allows and brings each
  one to the user's decision, so that abandoned Planning and Development work is resumed or dropped deliberately
  instead of lingering in progress, and nothing is deleted without the user.
- **Scope**: `devkit worktree status --stale`, the `worktree-stale` hygiene extension of `devkit rules check -p
  hygiene`, `devkit worktree start --existing-branch` and `devkit worktree finish --discard`.
- **Trigger**: The agent runs a whole-workspace hygiene check or the stale-branch report, for example in the
  `feedback-hygiene` playbook the user invoked.
- **Preconditions**: The repository is a devkit project with `devkit-agt` installed, the agent works in its base
  checkout, and branches made elsewhere have been fetched: devkit fetches nothing.

---

## 2. Main Success Scenario

1. The agent runs the stale-branch report, on its own or as part of a whole-workspace hygiene check
   (`CAP-WT-task-worktrees`, `CAP-GOV-evaluation-lifecycle`).
2. The system confirms that the GitHub CLI is logged in and takes the last activity of each `plan-*` and `dev-*`
   branch, local and remote-tracking, as the later of its last commit and its pull request's last update
   (`CAP-WT-task-worktrees`).
3. The system reports each branch idle longer than `[worktree] stale_after`, most idle first, with its unit, last
   activity, pull request state and where it exists, and warns about each with `WORKTREE_STALE_BRANCH`, naming how to
   resume it and how to discard it; it changes nothing (`CAP-WT-task-worktrees`).
4. The agent reports each stale branch to the user with both paths and takes neither unasked
   (`CAP-WT-task-worktrees`).
5. The user decides to discard the branch.
6. The agent closes the branch's open pull request and deletes its remote copies, which devkit leaves to the caller
   (`CAP-WT-task-worktrees`).
7. From the base checkout the agent drops the local branch: the system removes its worktree, when it has one, and
   deletes the unmerged branch, reporting a finish without a merge (`CAP-WT-task-worktrees`).

---

## 3. Extensions

- **1a.** The check runs in the `linter` phase, with explicit targets, or as the commit gate or CI: hygiene extensions
  are not called and no branch is judged (`CAP-GOV-evaluation-lifecycle`); the use case ends.
- **1b.** `[worktree] stale_after` is not `<N>d` or `<N>w`: the stale-branch report refuses with
  `WORKTREE_CONFIG_INVALID` (`CAP-WT-task-worktrees`), and a hygiene check reports the extension as
  `HYGIENE_EXTENSION_FAILED` without failing its run (`CAP-GOV-evaluation-lifecycle`); once the configuration is
  corrected, resumes at step 1.
- **2a.** `gh` is missing or not logged in: the system judges nothing and reports the `WORKTREE_STALE_SKIPPED` notice,
  which is not a failure (`CAP-WT-task-worktrees`); the use case ends.
- **2b.** `gh pr list` fails: the system judges the branches by their last commit alone, with pull request state
  `unknown`, and reports the `WORKTREE_STALE_PR_UNKNOWN` notice (`CAP-WT-task-worktrees`); resumes at step 3.
- **3a.** No activity branch is idle longer than `stale_after`: the summary reports no stale branch and no warning is
  raised (`CAP-WT-task-worktrees`); the use case ends.
- **5a.** The user decides to resume the branch: the agent runs the resume command the warning names, deriving the unit
  from the slug when none is recorded; the branch gets its worktree with nothing reset or rewritten, and its unit
  continues where it stopped (`CAP-WT-task-worktrees`); the use case ends.
- **5b.** The user keeps the branch as it is: nothing changes, and since nothing expires an activity branch, every later
  report warns about it again (`CAP-WT-task-worktrees`); the use case ends.
- **5c.** The branch carries the Development of an accepted proposal that is still in the base: discarding it is a
  close; the user decides a supersede or an abandon, and the agent commits the close to the base as Backlog work
  (`CAP-HARN-agent-guidance`); resumes at step 6.
- **6a.** The branch exists only on a remote: the warning names no local discard, and once its remote copies are
  deleted nothing is left to drop (`CAP-WT-task-worktrees`); the use case ends.
- **7a.** The worktree holds uncommitted or untracked changes: the system refuses with `WORKTREE_DIRTY` and never
  removes it by force (`CAP-WT-task-worktrees`); the user decides what happens to the changes; resumes at step 7.
- **7b.** The base checkout is on the branch, which was started there without a worktree: the system refuses with
  `WORKTREE_BASE_ON_BRANCH`, whose fix switches the base checkout back to the branch it started from
  (`CAP-WT-task-worktrees`); resumes at step 7.
- **7c.** The worktree is locked: the system refuses with `WORKTREE_LOCKED`, whose fix unlocks it once the user agrees,
  and changes nothing (`CAP-WT-task-worktrees`); resumes at step 7.

---

## 4. Postconditions

- **Success guarantee**: Each stale activity branch the user decided on is either resumed in its worktree with its unit
  intact, or discarded: its pull request closed, its remote copies deleted, its local branch and worktree gone, and an
  accepted proposal it carried closed in the base. A branch the user keeps stays as it was and is reported again.
- **Minimal guarantee**: The report changes nothing, and no branch, worktree or pull request is touched without the
  user's decision. A refused discard deletes neither the branch nor its worktree, and uncommitted changes are never
  removed by force. A skipped check is a notice, and a failing hygiene extension never fails the rules run.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Stale activity branches trigger hygiene warnings without deletion
- **Covers**: main success scenario
- **Given**: an activity branch `dev-<slug>` whose latest commit and pull request activity are older than
  `[worktree] stale_after`, with `gh` authenticated
- **When**: the agent runs `devkit rules check -p hygiene`
- **Then**: a `WORKTREE_STALE_BRANCH` warning reports the branch, its unit, its last activity, its pull request state
  and where it exists, with a `[FIX]` naming the resume command and the discard commands, and no branch is deleted

### Scenario 2: A discarded branch leaves with its pull request and remote copies
- **Covers**: main success scenario
- **Given**: a stale `dev-<slug>` with a clean worktree, which the user decided to discard, its pull request closed and
  `origin/dev-<slug>` deleted
- **When**: the agent runs `devkit worktree finish dev-<slug> --discard` from the base checkout
- **Then**: the output is `[WORKTREE_FINISHED: ...]` with `merged=no discarded=yes`, and the worktree and the local
  branch are gone

### Scenario 3: The commit gate never judges stale branches
- **Covers**: 1a
- **Given**: a stale `dev-<slug>` with `gh` authenticated
- **When**: the agent runs `devkit rules check` with explicit targets
- **Then**: no `WORKTREE_STALE_BRANCH` warning is reported

### Scenario 4: An invalid threshold fails the extension, not the hygiene run
- **Covers**: 1b
- **Given**: `.devkit/config.toml` sets `[worktree] stale_after = "2 weeks"`
- **When**: the agent runs `devkit rules check -p hygiene`
- **Then**: a `HYGIENE_EXTENSION_FAILED` warning names the `worktree-stale` extension, no branch is judged, and the
  rules run completes without the warning changing its exit code unless `--strict` is given

### Scenario 5: Without gh the check judges nothing
- **Covers**: 2a
- **Given**: a repository with an idle `plan-<slug>` and `gh auth status` failing
- **When**: the agent runs `devkit worktree status --stale`
- **Then**: a `WORKTREE_STALE_SKIPPED` notice is reported, the summary shows `checked=no` and `stale=0`, and the
  command does not fail

### Scenario 6: An unknown pull request state falls back to the last commit
- **Covers**: 2b
- **Given**: `gh` logged in, `gh pr list` failing, and a `dev-<slug>` whose last commit is older than `stale_after`
- **When**: the agent runs `devkit worktree status --stale`
- **Then**: the branch is reported as `[STALE_BRANCH: dev-<slug> ... pr=unknown ...]`, and a
  `WORKTREE_STALE_PR_UNKNOWN` notice is reported

### Scenario 7: Recent branches are not reported
- **Covers**: 3a
- **Given**: every activity branch has a commit or pull request update within `stale_after`
- **When**: the agent runs `devkit worktree status --stale`
- **Then**: no `[STALE_BRANCH: ...]` line or `WORKTREE_STALE_BRANCH` warning appears, and the summary shows `stale=0`

### Scenario 8: A resumed branch continues where it stopped
- **Covers**: 5a
- **Given**: a stale `plan-<slug>` with no worktree, which the user decided to resume
- **When**: the agent runs `devkit worktree start plan-<slug> --existing-branch plan-<slug> --unit
  docs/proposals/PROP-<slug>`
- **Then**: the branch has its worktree, the output carries `existing=yes unit=docs/proposals/PROP-<slug>`, nothing in
  the branch is reset or rewritten, and the run continues from the stage `devkit workflow next --unit <dir>` names

### Scenario 9: A kept branch is reported again
- **Covers**: 5b
- **Given**: a stale `dev-<slug>` the user decided to keep
- **When**: the agent runs `devkit rules check -p hygiene` again later
- **Then**: the branch still exists and the `WORKTREE_STALE_BRANCH` warning names it again

### Scenario 10: Discarding an accepted proposal's branch is a close
- **Covers**: 5c
- **Given**: a stale `dev-<slug>` whose accepted proposal is still in the base, which the user decided to abandon
- **When**: the agent closes the task
- **Then**: the rejection ADR is written and the accepted proposal deleted in one Backlog commit on the base, and only
  then are the pull request closed, the remote branch deleted and the branch dropped with
  `devkit worktree finish dev-<slug> --discard`

### Scenario 11: A remote-only branch has no local discard
- **Covers**: 6a
- **Given**: a stale `dev-<slug>` that exists only as `origin/dev-<slug>`
- **When**: the stale-branch report warns about it
- **Then**: its `[FIX]` names `git -C <base> push origin --delete dev-<slug>` and no `devkit worktree finish`
  command

### Scenario 12: A dirty worktree is never discarded by force
- **Covers**: 7a
- **Given**: a stale `dev-<slug>` whose worktree holds uncommitted changes
- **When**: the agent runs `devkit worktree finish dev-<slug> --discard`
- **Then**: the command refuses with `WORKTREE_DIRTY`, and the worktree, its changes and the branch remain

### Scenario 13: A branch in the base checkout is discarded after switching back
- **Covers**: 7b
- **Given**: a stale `dev-<slug>` started with `devkit worktree start dev-<slug> --no-worktree`, still checked out in
  the base checkout
- **When**: the agent runs `devkit worktree finish dev-<slug> --discard`
- **Then**: the command refuses with `WORKTREE_BASE_ON_BRANCH`, whose `[FIX]` switches the base checkout back to its
  recorded `devkitBase` for a rerun, and the branch remains

### Scenario 14: A locked worktree waits for the user
- **Covers**: 7c
- **Given**: a stale `dev-<slug>` whose worktree is locked with `git worktree lock`
- **When**: the agent runs `devkit worktree finish dev-<slug> --discard`
- **Then**: the command refuses with `WORKTREE_LOCKED`, whose `[FIX]` is `git worktree unlock <path>` once the user
  agrees, and nothing changes
