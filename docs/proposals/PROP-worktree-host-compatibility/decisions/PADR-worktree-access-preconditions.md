---
id: PADR-worktree-access-preconditions
title: Worktree access stays a host session precondition
summary: Keeps task worktrees as sibling checkouts, projects no host access settings and sets no repository Git profile; each host's access to a worktree and its two git dirs is a documented session precondition in the worker contracts and the spec-delegate hosts reference.
proposal: PROP-worktree-host-compatibility
status: draft
created_at: 2026-10-19
---

# [PADR-worktree-access-preconditions] Worktree access stays a host session precondition

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q1, Q2, Q5 and Q6 of `PROP-worktree-host-compatibility`; options O1, O2 and O5. Evidence:
  `MAT-worktree-host-spike-evidence`, `envelopes/scout-01.yaml`, `envelopes/scout-02.yaml`.

---

## 1. Context & Problem Statement

A worker in a sibling worktree writes three places when it commits: the worktree, its own git dir
`<repo>/.git/worktrees/<name>/` and the shared `<repo>/.git/` (`ADR-worker-delivers-committed-result`). No host gives
a subagent its own working directory or a per-agent extra directory. Each host's access is a property of the session:

- Claude Code: the auto or bypass mode, or the worktree as a session working directory (`/add-dir`, `--add-dir`, or
  `permissions.additionalDirectories` after workspace trust); with the Bash sandbox on, a session rooted in the base
  checkout cannot write the base's `.git` `objects/` and `refs/`. This repository's orchestrated runs work in auto
  mode without a sandbox or configured directories.
- Codex: both git dirs of each worktree named exactly as writable (profile entries, legacy writable roots or
  `--add-dir`), and the project trusted for project configuration; subagents inherit the parent's cwd and sandbox.
- Antigravity: access outside the project folders is off by default (`allowNonWorkspaceAccess`, `/add-dir`).

The spike asked whether devkit should project these grants (O1), move worktrees inside the repository (O2) or set
repository Git settings (O5).

## 2. Decision Drivers

- The Host's post-run check of the committed range stays the guarantee (`spec-delegate` `references/worker.md`).
- `CAP-DIST-agent-projections`: devkit never touches host settings, credentials or trust configuration.
- A grant must name per-worktree literal paths, which exist only after `devkit worktree start`.
- No change that makes the repository unreadable for a Git a host or tool still ships.

## 3. Considered Options

- **O1, project host access configuration from `devkit sync`.** Cons: paths are per worktree (Codex needs the exact
  `<repo>/.git/worktrees/<name>`; Claude Code documents only literal paths), project files apply only after host
  trust, Codex profiles and legacy `sandbox_mode` exclude each other, and writing host settings breaks the projection
  boundary. Pros: none beyond what a session precondition gives.
- **O2, worktrees inside the repository** (for example `.devkit/worktrees/<branch>`). Pros: Claude Code
  `acceptEdits` covers edits inside the cwd; one mount carries repository and worktrees. Cons: Codex and the Claude
  Code sandbox still protect the git dirs, so commits stay blocked; consumer tools that ignore `.gitignore` traverse
  every worktree; `CAP-WT-task-worktrees`, `ARCH-07-deployment` and recorded scope paths change.
- **O5, an opt-in repository Git profile** (`worktree.useRelativePaths`, `extensions.worktreeConfig`). Cons:
  `extensions.relativeWorktrees` makes the repository unreadable for Apple Git 2.39, libgit2 before 1.9.4 and go-git
  v5; no host in scope mounts the repository at another path; nothing needs per-worktree configuration.
- **Session precondition, documented per host (selected).** The access stays the session's; devkit states it where
  the Host decides to spawn and where the worker reports a refusal.

## 4. Decision Outcome

- Task worktrees MUST stay at `<parent of base>/<base name>-wt-<branch>` (`CAP-WT-task-worktrees` unchanged).
- `devkit sync` MUST NOT write host permission, sandbox, directory or trust settings for worktree access, and devkit
  MUST NOT set or check `worktree.useRelativePaths`, `extensions.relativeWorktrees` or `extensions.worktreeConfig`.
- The `spec-delegate` hosts reference MUST state, per host, what the session needs before a worker is spawned into a
  sibling worktree, and the worker contracts' host-block comments MUST name the same verified reasons:
  - **Claude Code** (`native`): the auto or bypass permission mode, or the worktree added as a working directory
    (`/add-dir <worktree>` or `--add-dir`), and no Bash sandbox for the session, whose protected `.git` paths block
    the worker's commit from a base-rooted session.
  - **Codex** (`unsupported` as a subagent): `spawn_agent` keeps the parent's cwd and sandbox, and a commit needs
    `<repo>/.git` and `<repo>/.git/worktrees/<name>` writable; the Codex worker path is `PADR-codex-process-worker`.
  - **Antigravity** (`unverified`): the worktree must be reachable through the project's folders, `/add-dir` or
    non-workspace access; `.git` handling is undocumented.
- A worker whose write, command or commit in its worktree is refused MUST stop through its contract's problem
  procedure, naming the refused path or command; the Host then runs the activity in `direct`.
- A Claude Code session rooted above the project (Q5) MAY load the projected roles with `/add-dir <project>` or
  `--add-dir <project>` before falling back to emulation; the hosts reference states it once Development has verified
  it, and keeps emulation as the stated path otherwise.

## 5. Consequences

- Development changes only devkit-spec assets and their Living Spec mirrors: the hosts reference of
  `spec-delegate`, the host-block comments of `planning-worker` and `development-worker`, and the role descriptions in
  `CAP-DLV-delivery-workflows` and `CAP-DLV-workflow-orchestration` where they name host behaviour.
- No change to `devkit.worktree`, `devkit.distribution` or the projected key allowlists.
- A user who runs Claude Code in `default` or `acceptEdits` mode, or with the sandbox, must add the worktree or use
  direct mode; the precondition is stated, not enforced.
- Revisit O2 or O5 when a supported host runs workers in a container or another mount of the repository.
