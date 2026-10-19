---
id: PROP-worktree-host-compatibility
title: Worktree access for subagents across hosts
summary: "Investigate how worker subagents on Claude Code, Codex and Antigravity can read, write and run commands in a sibling devkit worktree, and choose a portable approach for orchestration mode."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-15
target_area: delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundle/subagents/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worker-records.md
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
workflow_hash: sha256:90918c632715461d07f99f683b8381bdbe6381ad6689a7575a72c002c18c1399
---

# [PROP-worktree-host-compatibility] Worktree access for subagents across hosts

## 1. Background & Hypothesis

`SPEC-orchestration-mode` has worker subagents implement in their own devkit worktree
(`<parent of base>/<base name>-wt-<branch>`). Its spike found that no host gives a subagent its own working directory:
on Claude Code a worker shares the session's directory and must use absolute paths and `git -C`, and the session must
already allow the sibling path; Codex `workspace-write` confines writes to the project root, which excludes the
sibling worktree; Antigravity has no documented working-directory control. Orchestration mode therefore starts as
Claude Code `native`, Codex `unsupported` (the main session substitutes) and Antigravity `unverified`.

Hypothesis: a documented host mechanism, a different worktree location or a separate worker process makes worker
delegation work on every supported host without weakening the post-run diff check.

## 2. Technical Spike Questions

- **Q1**: Per host, what documented mechanism grants a subagent (or the session) read, write and command access to an
  extra directory (Claude Code permission settings for additional directories, Codex writable roots or added
  directories, Antigravity workspace settings), and can `devkit sync` project it without per-user setup? Workers commit
  their build (`ADR-worker-delivers-committed-result`), so the access includes the Git common directory of a linked
  worktree, not only the worktree directory.
- **Q2**: Does a worktree inside the repository (for example under an ignored `.devkit/` path) avoid the sandbox
  limits, and what breaks: project discovery climbing to the base, `rg` and tool scans, scope registry attribution,
  `devkit worktree` path conventions and cleanup?
- **Q3**: Is a separate worker process started in the worktree (a headless host session with that directory as its
  root) viable for each host, and how does it return the envelope fields and keep the host's diff check?
- **Q4**: Can a host-native worktree isolation be adopted and registered with devkit (scope registry, setup, sync,
  `finish`) instead of `devkit worktree start`, or does it stay excluded?
- **Q5**: Projected roles load only in a session rooted in the project; a session started in a parent workspace has
  no `worker` subagent. Does the chosen option also cover that case, or does the caller always emulate there?
- **Q6**: Which repository Git settings help across hosts and sandboxes: `worktree.useRelativePaths` (and the
  `extensions.relativeWorktrees` it enables) so worktrees survive another mount path, `extensions.worktreeConfig` for
  per-worktree settings? What Git version does every tool reading the repository need, and should devkit set or check
  them (`[worktree]` config, `devkit worktree start`) for a repository that opts in? A personal repository can meet
  such conditions even where the defaults could not be assumed.
- **Q7**: How do the hosts' own worktree flows fit devkit's: Claude Code `isolation: worktree` subagents with
  `WorktreeCreate`/`WorktreeRemove` hooks and `worktree.baseRef`, and the ChatGPT Codex app's managed worktrees
  (detached HEAD, handoff between local and worktree, `.worktreeinclude`, `.codex` local environment setup scripts)?
  Desk research: `MAT-host-worktree-flows`.

## 3. Proposed Design & Impact

Options to compare after the spike:

- **O1, host access configuration**: project the extra-directory permission per host from devkit; worktrees stay
  where they are.
- **O2, worktree inside the repository**: change the worktree location so every sandbox covers it.
- **O3, worker process per worktree**: start the worker as its own host session rooted in the worktree.
- **O4, host-native isolation**: let the host create the worktree and register it with devkit. On Claude Code a
  `WorktreeCreate` hook could run `devkit worktree start` and hand its path to `isolation: worktree` subagents.
- **O5, repository Git settings**: an opt-in repository profile (for example relative worktree paths) that devkit
  sets or checks, alone or combined with O1 to O4.

Impact depends on the choice: the worker contract's host blocks and `spec-delegate` (all options), devkit's
`worktree` path convention and config (O2, O4, O5), the distribution projections (O1, O4 hooks), and a worker launch
procedure (O3).

### 3.1 Spike findings

Evidence and the option table: `MAT-worktree-host-spike-evidence`; scout returns `envelopes/scout-01.yaml` and
`envelopes/scout-02.yaml`.

- A worker's commit writes the worktree, its own git dir `<repo>/.git/worktrees/<name>/` and the shared `<repo>/.git/`.
  No host gives a subagent its own working directory or a per-agent extra directory: access is the session's.
- Claude Code: the observed orchestrated runs work in auto mode without a sandbox or configured directories. In
  `default` or `acceptEdits` mode the worktree must be a session working directory; with the Bash sandbox on, a
  base-rooted session cannot write the base's `.git` `objects/` and `refs/`, so the worker's commit fails.
- Codex: `spawn_agent` keeps the parent's cwd and sandbox, and `.git` plus the worktree's own git dir are read-only in
  every writable root unless named exactly; with both granted, a session rooted in the worktree commits (verified with
  `codex sandbox`). A sandboxed Codex Host cannot start a nested sandboxed process.
- Antigravity: subagents inherit the parent's scopes; access outside the project folders is off by default; `.git`
  handling is undocumented.
- A worktree inside the repository does not lift the git-dir protection (O2); relative worktree paths make the
  repository unreadable for Apple Git 2.39 and older libgit2 and go-git (O5); host-native worktrees cannot continue
  one devkit branch across worker turns (O4).

### 3.2 Decisions

- `PADR-worktree-access-preconditions`: worktrees stay sibling checkouts; devkit projects no host access settings
  and sets no repository Git profile; each host's access is a documented session precondition, marked observed or
  documented, which every worker probes with its own tools before it writes; a refused probe ends the turn with
  nothing written, and a worker refused later stops through its problem procedure or, when even its emergency commit
  is refused, is reported by the Host as stopped with its uncommitted paths.
- `PADR-host-native-worktrees-excluded`: `devkit worktree start` stays the only source of an activity's worktree.
- `PADR-codex-process-worker`: on Codex a worker turn runs as one approved `codex exec` process rooted in its
  worktree with both git dirs granted, shipped only when one live Development turn passes; a failed or unrun turn
  ships the recorded reasons only. The user runs that turn from a Codex session when Development reaches it; the
  Development worker never runs `codex exec` itself.
- Answers (`envelopes/answer-01.yaml`): `codex-worker-scope` = `process-worker`, `codex-live-turn` =
  `user-codex-host`, `antigravity-verification` = `keep-unverified`.
- Effort: `dev_effort: high` and `size: M` (a new launch procedure, skill and contract changes, the worker probe and a
  live verification handed to the user mid-Development).
- Open, not widened: on every host a worker has the session's access to the shared `.git` (other refs, config, hooks,
  the scope registry), which the Host's range check does not see.

### 3.3 Non-goals

- Moving task worktrees, changing `devkit worktree` or the distribution projections, or writing host settings.
- A `claude -p` process worker for the Claude Code sandbox case (deferred in `PADR-worktree-access-preconditions`),
  and host-native worktree adoption.
- Closing the shared-`.git` gap of the range check.
- Live verification on Antigravity: it stays `unverified` with its documented preconditions.

## 4. Lifecycle & Retirement Criteria

- Restart condition: `SPEC-orchestration-mode` integrated with its Claude Code path working.
- Expected acceptance checks:
  - Contract tests (`packages/devkit-spec/tests/test_role_contracts.py`): both worker contracts keep Claude Code
    `native`, Codex `unsupported` and Antigravity `unverified`, set no `isolation`, and carry `x-process-hosts: [codex]`
    exactly when the Codex live turn passed.
  - A contract test runs both worker contracts' probe commands on a throwaway repository with a linked worktree and
    asserts refs, reflogs of existing refs, the index and `git status` unchanged.
  - `packages/devkit-spec/tests/test_bundle_budgets.py` passes (`spec-delegate/SKILL.md` at most 11776 bytes).
  - The hosts reference states each host's precondition marked observed or documented, matching
    `MAT-worktree-host-spike-evidence` and the Development evidence; the Q5 `/add-dir` statement appears only with a
    session recorded in the spec's `tasks.md` evidence.
  - The live Codex turn's record in the spec's `tasks.md` evidence and the Development `worker` envelope (fields and
    the Passes criterion in `PADR-codex-process-worker` §4) shows either Passes with the launch shipped, or the failed
    condition (a turn the user did not run included) with nothing of the launch shipped.
  - `just lint-check`, `just check`, `just test`, `just rules-check` and `just smoke` pass.
- On acceptance: set `status: accepted` and run `devkit spec proposal handoff worktree-host-compatibility`. On
  rejection: record a rejection ADR and delete the proposal directory.
