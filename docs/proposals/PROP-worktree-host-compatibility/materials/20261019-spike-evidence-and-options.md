---
id: MAT-worktree-host-spike-evidence
title: Worktree host access spike evidence and option comparison
created_at: 2026-10-19
---

# [MAT-worktree-host-spike-evidence] Worktree host access spike evidence and option comparison

Planning material for `PROP-worktree-host-compatibility`: the answers to spike questions Q1 to Q7 and the comparison of
options O1 to O5 behind `PADR-worktree-access-preconditions`, `PADR-host-native-worktrees-excluded` and
`PADR-codex-process-worker`. Sources: the host documentation as fetched on 2026-10-19 (`envelopes/scout-01.yaml`,
`envelopes/scout-02.yaml`), local probes on throwaway repositories (codex-cli 0.160.1, Git 2.49.0 and Apple Git 2.39.5,
macOS), and this repository's own local-orchestrated runs on Claude Code 2.1.303. `<repo>` is the base checkout,
`<worktree>` a sibling task worktree `<parent of repo>/<repo name>-wt-<branch>`, `<name>` its entry under
`<repo>/.git/worktrees/`. Corrects `MAT-host-worktree-flows` §2: workers commit their result
(`ADR-worker-delivers-committed-result`), so the Git common directory must be writable, not only the worktree.

## 1. What a worker needs

A worker reads, writes and runs commands in `<worktree>` and commits there. A commit writes three places: the
worktree's files, its own git dir `<repo>/.git/worktrees/<name>/` (index, `HEAD`, logs) and the shared
`<repo>/.git/` (`objects/`, `refs/`). The Host validates the committed range afterwards
(`spec-delegate` `references/worker.md`); that check is unchanged by every option below.

## 2. Observed behaviour per host

### 2.1 Claude Code (observed in this repository)

- Planning and Development workers ran as `native` subagents in sibling devkit worktrees, with absolute paths and
  `git -C`, committed through the commit gate there, and the Host validated their ranges. The session was rooted in
  the base checkout.
- The settings in effect: user-level `permissions.defaultMode = "auto"`, no `additionalDirectories` at any level, no
  sandbox. Access to the sibling path came from the auto mode's classifier, not from a configured directory.
- Documented preconditions that this run did not exercise (scout-01):
  - `default` and `acceptEdits` modes: Edit/Write outside the session's working directories prompts. The sibling path
    must be a working directory (`/add-dir <worktree>`, `--add-dir`, or a literal path in
    `permissions.additionalDirectories`, which a checked-in project file applies only after workspace trust and never
    under an untrusted `claude -p`).
  - Subagents start in the session's working directory, have no `cwd` or per-agent directory key, and ignore their
    `permissionMode` when the parent runs in `auto`, `acceptEdits` or `bypassPermissions`.
  - Sandbox on: inside the cwd, `.git` `HEAD`, `objects/`, `refs/`, `hooks/` and `config` are write-protected and
    `allowWrite` cannot exempt them; only a session whose cwd is itself a linked worktree may write the shared `.git`.
    A base-rooted session with the sandbox on therefore cannot commit from a sibling worktree through Bash.

### 2.2 Codex (local probes, scout-02)

`codex sandbox -P <profile> -C <root> -- <cmd>` on a throwaway repository outside `/tmp` (the built-in `:workspace`
profile always allows `/tmp`, which hides denials there):

| # | Root | Extra grant | Action | Result |
| :-- | :-- | :-- | :-- | :-- |
| 1 | base | none | write a file in a sibling worktree | denied |
| 2 | sibling worktree | none | write a file in it | allowed |
| 3 | sibling worktree | none | `git commit` | denied (`.git/worktrees/<name>/index.lock`) |
| 4 | sibling worktree | `<repo>/.git` | `git commit` | denied (worktree git dir stays read-only) |
| 5 | sibling worktree | worktree git dir only | `git commit` | denied (objects in the shared dir) |
| 6 | sibling worktree | `<repo>/.git` and `<repo>/.git/worktrees/<name>` | `git commit` | allowed |
| 7 | base | none | write a file in an in-repository worktree (`.devkit/worktrees/<b>`) | allowed |
| 8 | base | none | `git commit` in that in-repository worktree | denied |
| 9 | base | none | `git commit` in the base itself | denied |
| 10 | inside `:workspace` | none | start a nested `codex sandbox` | refused (`sandbox_apply: Operation not permitted`) |
| 11 | inside `:workspace` | none | write `~/.codex`, reach the model API | denied, no network |

- `.git` (and the git dir a worktree pointer names) is read-only inside every writable root by design; only an
  explicit rule on that exact path lifts it (openai/codex#14338 is the open request).
- `spawn_agent` has no `cwd` or writable-root parameter, and a role keeps the parent's cwd, approval policy and
  permission profile: a Codex subagent cannot reach what the parent session cannot.
- Profiles (`[permissions.<name>]`) do not combine with the legacy `sandbox_mode`; a project `.codex/config.toml`
  applies only when the project is trusted and holds only absolute paths, so it cannot name a future worktree.
- `codex exec -C <worktree> --add-dir <repo>/.git --add-dir <repo>/.git/worktrees/<name> --json --output-schema <f>
  -o <f>` is the documented shape of a worker process rooted in its worktree. `exec` forces approval `never` (unless
  auto review is selected), so any other blocked action fails rather than prompts. Rows 10 and 11 mean a sandboxed
  Codex Host must start that process outside its own sandbox: one escalated command per turn, approved by the user or
  by `approvals_reviewer = "auto_review"`. Not run end to end (it starts a model session).

### 2.3 Antigravity (documentation only)

- Subagents (`.agents/agents/*.md`, `invoke_subagent`) inherit the parent's file scopes and sandbox; a workspace mode
  `inherit`, `branch` (its own Git worktree, removed when the subagent is killed) or `share` exists, without
  documented parameters, location or base.
- Access outside the project folders is off by default (`allowNonWorkspaceAccess`, CLI `/add-dir <path>`); the
  sandbox's treatment of `.git` and sibling directories is undocumented. Installed locally, not exercised.

## 3. Answers to the spike questions

- **Q1 (access mechanisms)**: every mechanism is session-level and names literal paths: Claude Code working
  directories (`--add-dir`, `/add-dir`, `additionalDirectories` after trust) or the auto mode; Codex profile or
  legacy writable roots, `--add-dir`, which must name both git dirs of each worktree; Antigravity
  `allowNonWorkspaceAccess` or `/add-dir`. None can be projected by `devkit sync` without per-user setup: the paths
  are per worktree, project files need host trust, and `CAP-DIST-agent-projections` keeps devkit out of host settings.
- **Q2 (worktree inside the repository)**: does not avoid the binding limit. Codex and the Claude Code sandbox still
  protect the git dirs (rows 7 to 9); the only gain is that Claude Code `acceptEdits` covers edits inside the cwd.
  Inside devkit little breaks (project discovery stops at the worktree's own top level, rules use
  `git ls-files --exclude-standard`, ruff honours `.gitignore`, Pyright and pytest skip dot directories), but consumer
  tools that ignore `.gitignore` (Docker build contexts, indexers, watchers) would traverse every worktree, and
  `CAP-WT-task-worktrees`, `ARCH-07-deployment` and recorded scope paths change.
- **Q3 (worker process per worktree)**: viable in principle on Claude Code (`claude -p --agent <role>` rooted in the
  worktree loads its roles, and its sandbox allows the shared `.git` from a linked worktree) and on Codex (`codex exec`
  above). The return stays the committed `worker` envelope and head, so the diff check is kept. Codex costs one
  escalated launch per turn; Antigravity's headless CLI documents no cwd or directory flag.
- **Q4 (host-native isolation)**: stays excluded. Claude Code `isolation: worktree` makes a fresh
  `.claude/worktrees/<name>` per run from `fresh` or `head`, while a devkit activity continues one `plan-`/`dev-`
  branch across turns; the `WorktreeCreate` hook receives a generated `name`, not the slug, and replaces creation for
  every session, subagent and workflow worktree. Codex worktrees are detached and branchless; Antigravity's `branch`
  mode is undocumented in detail.
- **Q5 (parent-workspace session)**: Claude Code discovers project agents upward from the cwd only, but `--add-dir`
  and `/add-dir` (v2.1.257+) load an added folder's agents and skills; a process worker (O3) is rooted in the project
  and needs no projection in the Host's root. Otherwise the caller emulates as today.
- **Q6 (repository Git settings)**: `worktree.useRelativePaths` sets `extensions.relativeWorktrees`, which Apple Git
  2.39.5 (`/usr/bin/git`), libgit2 before 1.9.4 and go-git v5 refuse for the whole repository; no host in scope mounts
  the repository at another path. `extensions.worktreeConfig` is widely supported but nothing needs it. devkit sets
  and checks neither.
- **Q7 (host worktree flows)**: answered with Q4; `MAT-host-worktree-flows` holds the desk research.

## 4. Option comparison

| Option | Claude Code | Codex | Antigravity | Cost | Verdict |
| :-- | :-- | :-- | :-- | :-- | :-- |
| O1 host access configuration projected | per-worktree literal paths, trust; auto mode already works | per-worktree exact git dirs; trust; profile vs legacy conflict | unknown | breaks the projection boundary; stale paths per worktree | rejected as projection; kept as documented session precondition |
| O2 worktree inside the repository | edits covered in `acceptEdits`; sandbox still blocks commits | commits still denied | unknown | path convention, docs, consumer tool scans | rejected |
| O3 worker process per worktree | possible, not needed while the subagent works | the only Codex path; escalated launch per turn | no documented cwd flag | launch procedure, live verification | Codex only, subject to the user's scope choice |
| O4 host-native isolation | fresh worktree per run, no slug in the hook | detached, branchless | undocumented | conflicts with branch-per-activity and `spec-orchestrate` | excluded |
| O5 repository Git settings | no need found | no need found | no need found | repository unreadable for older Git | rejected |
