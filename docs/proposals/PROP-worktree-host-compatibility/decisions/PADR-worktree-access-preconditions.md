---
id: PADR-worktree-access-preconditions
title: Worktree access stays a host session precondition
summary: Keeps task worktrees as sibling checkouts, projects no host access settings and sets no repository Git profile; each host's access to a worktree and its two git dirs is a documented session precondition that the Host probes before the first worker turn.
proposal: PROP-worktree-host-compatibility
status: draft
created_at: 2026-10-19
---

# [PADR-worktree-access-preconditions] Worktree access stays a host session precondition

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q1, Q2, Q5 and Q6 of `PROP-worktree-host-compatibility`; options O1, O2 and O5. Evidence:
  `MAT-worktree-host-spike-evidence`, `envelopes/scout-01.yaml`, `envelopes/scout-02.yaml`; reviewed in
  `envelopes/challenger-01.yaml`.

---

## 1. Context & Problem Statement

A worker in a sibling worktree writes three places when it commits: the worktree, its own git dir
`<repo>/.git/worktrees/<name>/` and the shared `<repo>/.git/` (`ADR-worker-delivers-committed-result`). No host gives
a subagent its own working directory or a per-agent extra directory; access is a property of the session, and a
subagent has the session's. Observed (O) and documented (D) per host:

- Claude Code: auto mode without a sandbox or configured directories works for Planning and Development workers in
  this repository (O). `acceptEdits` with the worktree as a working directory (`/add-dir <worktree>`, `--add-dir`, or
  `permissions.additionalDirectories` after workspace trust) auto-approves edits there, while other Bash commands
  follow the Bash rules (D); `default` prompts for edits and commands (D). With the Bash sandbox on, a session rooted
  in the base checkout cannot write the base's `.git` `HEAD`, `objects/` and `refs/` (D; escape hatches not examined).
- Codex: `spawn_agent` keeps the parent's cwd and sandbox; a commit needs `<repo>/.git` and
  `<repo>/.git/worktrees/<name>` named exactly as writable (O, `codex sandbox`); a sandboxed Host itself escalates its
  writes to a sibling worktree, so `direct` under `[tool.spec] worktree = "required"` already depends on approvals.
- Antigravity: access outside the project folders is off by default (`allowNonWorkspaceAccess`, `/add-dir`) (D).

The spike asked whether devkit should project these grants (O1), move worktrees inside the repository (O2) or set
repository Git settings (O5).

## 2. Decision Drivers

- The Host's committed-range check stays the guarantee (`spec-delegate` `references/worker.md`).
- `CAP-DIST-agent-projections`: devkit never touches host settings, credentials or trust configuration.
- A grant must name per-worktree literal paths, which exist only after `devkit worktree start`.
- A missing access must surface before a worker leaves uncommitted work that nobody can commit.
- No change that makes the repository unreadable for a Git a host or tool still ships.

## 3. Considered Options

- **O1, project host access configuration from `devkit sync`.** Cons: paths are per worktree (Codex needs the exact
  `<repo>/.git/worktrees/<name>`; Claude Code documents only literal paths), project files apply only after host
  trust, Codex profiles and legacy `sandbox_mode` exclude each other, and writing host settings breaks the projection
  boundary.
- **O2, worktrees inside the repository** (for example `.devkit/worktrees/<branch>`). Pros: Claude Code
  `acceptEdits` covers edits inside the cwd. Cons: Codex and the Claude Code sandbox still protect the git dirs, so
  commits stay blocked; consumer tools that ignore `.gitignore` traverse every worktree; `CAP-WT-task-worktrees`,
  `ARCH-07-deployment` and recorded scope paths change.
- **O5, an opt-in repository Git profile** (`worktree.useRelativePaths`, `extensions.worktreeConfig`). Cons:
  `extensions.relativeWorktrees` makes the repository unreadable for Apple Git 2.39, libgit2 before 1.9.4 and go-git
  v5; no host in scope mounts the repository at another path; nothing needs per-worktree configuration.
- **A `claude -p` process worker for the Claude Code sandbox case.** Pros: rooted in the worktree, the sandbox allows
  the shared `.git`; it would reuse a process launch and validation. Cons: its own live verification and an unattended
  permission-mode choice; this repository's sessions run without the sandbox. Deferred: a later change can add it by
  naming `claude-code` in the process-launch key of `PADR-codex-process-worker` after its own verified turn.
- **The user starts the session in the worktree for `direct` work.** A session rooted in a linked worktree may write
  the shared `.git` under the Claude Code sandbox; it is the documented remedy for `direct`, not a worker path.
- **Session precondition, documented per host and probed by the Host (selected).**

## 4. Decision Outcome

- Task worktrees MUST stay at `<parent of base>/<base name>-wt-<branch>` (`CAP-WT-task-worktrees` unchanged).
- `devkit sync` MUST NOT write host permission, sandbox, directory or trust settings for worktree access, and devkit
  MUST NOT set or check `worktree.useRelativePaths`, `extensions.relativeWorktrees` or `extensions.worktreeConfig`.
- The `spec-delegate` hosts reference MUST state, per host and marked observed or documented, what the session needs
  before a worker is spawned into a sibling worktree, and the worker contracts' host-block comments MUST name the same
  reasons:
  - **Claude Code** (`native`): auto or bypass mode (observed: auto); `acceptEdits` with the worktree added by the
    user (`/add-dir <worktree>` once per worktree; the Host cannot run it), where Bash commands still prompt; not
    `default`; no Bash sandbox, whose protected `.git` paths block the commit from a base-rooted session.
  - **Codex** (`unsupported` as a subagent): `spawn_agent` keeps the parent's cwd and sandbox, and a commit needs both
    git dirs writable; a Codex worker path exists only where `PADR-codex-process-worker` verified one.
  - **Antigravity** (`unverified`): the worktree reachable through the project's folders, `/add-dir` or non-workspace
    access; `.git` handling undocumented.
- Before the first worker turn in a worktree, the Host MUST probe with its session's own tools that it can create and
  remove a file in the worktree and write the worktree's git dir and the shared objects and refs, leaving no trace
  (Development fixes the commands, and a test shows they leave refs, index and status unchanged). A failed probe
  spawns no worker: the Host reports the missing precondition and its per-host remedy to the user and starts no work
  in that worktree.
- A worker whose write, command or commit is refused after the probe passed MUST stop through its contract's problem
  procedure; when its own emergency commit is refused it returns the problem in its final report, and the Host records
  it as its own blocking `worker` envelope (`references/worker.md`). When the Host cannot commit that either, it stops
  and reports to the user with the worktree left as it is.
- A Claude Code session rooted above the project (Q5) MAY load the projected roles with `/add-dir <project>` or
  `--add-dir <project>`; the hosts reference states it only after Development records, in the spec's materials, a
  session that loaded a role that way, and keeps emulation as the stated path otherwise.

## 5. Consequences

- Development changes devkit-spec assets and their Living Spec mirror: `spec-delegate` (`references/hosts.md`,
  `references/worker.md` for the probe and the uncommittable problem, `SKILL.md` Step 3 only when a process path is
  added), `spec-orchestrate`, the host blocks of `planning-worker` and `development-worker`, their contract tests, and
  `CAP-DLV-delivery-workflows`.
- No change to `devkit.worktree`, `devkit.distribution` or the projected key allowlists.
- The precondition is stated and probed, not enforced by devkit.
- Not widened, not closed: on every host a worker has the session's access to the shared `.git` (other refs, config,
  hooks, the scope registry), which the range check does not see; recorded as an open finding of this Planning.
- Revisit O2 or O5 when a supported host runs workers in a container or another mount of the repository.
