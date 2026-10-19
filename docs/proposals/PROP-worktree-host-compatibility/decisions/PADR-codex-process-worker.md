---
id: PADR-codex-process-worker
title: Codex worker as a separate process rooted in its worktree
summary: Runs a Codex Planning or Development worker turn as a codex exec process rooted in the activity's worktree with both git dirs granted, launched by the Host outside its sandbox, and changes the Codex worker status only after a verified live turn.
proposal: PROP-worktree-host-compatibility
status: draft
created_at: 2026-10-19
---

# [PADR-codex-process-worker] Codex worker as a separate process rooted in its worktree

- **Status**: Draft, pending the user's answer to `codex-worker-scope` (`envelopes/worker-01.yaml`)
- **Date**: 2026-10-19
- **Answers**: Q3 and Q5 of `PROP-worktree-host-compatibility`; option O3. Evidence: `MAT-worktree-host-spike-evidence`
  §2.2, `envelopes/scout-02.yaml`.

---

## 1. Context & Problem Statement

On Codex the worker roles are `unsupported`, so the main session runs every activity in `direct`. The spike found the
reason is structural, not the worktree's location: `spawn_agent` keeps the parent's cwd, approval policy and
permission profile, a custom agent cannot override `sandbox_mode`, and `.git` plus the linked worktree's own git dir
are read-only inside every writable root unless named exactly. A Codex session started in the worktree with both git
dirs granted can commit there (verified with `codex sandbox`); a subagent of a base-rooted session cannot.

## 2. Decision Drivers

- Worker delegation on Codex without weakening the Host's committed-range check.
- No host settings written by devkit (`PADR-worktree-access-preconditions`).
- No new projection status or key in `devkit.distribution`; the change stays in devkit-spec assets.
- Codex sandboxes the Host's own commands: a nested sandbox cannot be applied, `~/.codex` is not writable and the
  network is off inside `:workspace`.

## 3. Considered Options

- **Keep Codex `unsupported`; the main session runs each activity in `direct`.** Pros: no new procedure, nothing
  unverified. Cons: no orchestration on Codex; parallel units are serial in one session.
- **A Codex session started by the user per worktree with the grants (O1 per run).** Cons: the user starts one
  session per activity and turn by hand; it is a second Host, not a worker the Host coordinates.
- **A `codex exec` process per worker turn, rooted in the worktree (selected, if `codex-worker-scope` is
  `process-worker`).** `codex exec -C <worktree> --add-dir <repo>/.git --add-dir <repo>/.git/worktrees/<name>` with the
  managed contract body and the payload as its prompt; the worker commits its records and `worker` envelope as on
  every host, and the Host validates the committed range. Pros: the worker's cwd is its worktree, projected roles and
  skills load from it (Q5 included), nested roles inherit its sandbox. Cons: one escalated launch per turn (the
  Host's sandbox cannot start it), approval `never` inside `exec` so any other blocked action fails, unverified end
  to end.

## 4. Decision Outcome

Proposed outcome for `process-worker`:

- In `local-orchestrated` mode on Codex, the Host MUST run each `planning-worker` or `development-worker` turn as one
  `codex exec` process with `-C <worktree>` and write grants for exactly `<repo>/.git` and
  `<repo>/.git/worktrees/<name>`, never broader; the prompt is the managed contract body (or its override) followed
  by the payload `spec-delegate` defines.
- The Host MUST start the process as an escalated command (the user's or the configured auto review's approval), wait
  for it, and validate the result exactly as for a subagent worker (`spec-delegate` `references/worker.md`): the
  committed `worker` envelope and the final head are the return; the process's last message is not trusted beyond
  them.
- The host block stays `status: unsupported` (no `.codex/agents/<worker>.toml`); the contract marks the process launch
  with a top-level extension key (for example `x-process-hosts: [codex]`), and `spec-delegate` and `spec-orchestrate`
  name it as the Codex path in place of substitution.
- Development MUST verify one live Planning or Development turn through this path (a commit in the worktree only, the
  Host's range check passing) before the hosts reference and `spec-orchestrate` offer it; when the live turn fails,
  only the verified reasons are documented and the main session keeps substituting.

For `keep-unsupported`, only the verified reasons of `PADR-worktree-access-preconditions` are documented and this
PADR is withdrawn before handoff.

## 5. Consequences

- Changes `spec-delegate` (`references/hosts.md`, within its byte budget), `spec-orchestrate`, the two worker
  contracts and `CAP-DLV-workflow-orchestration`; no devkit package change.
- Each Codex worker turn costs a separate model session and an approval; its nested `challenger`, `scout` and
  reviewer roles need the project trusted in Codex (`references/hosts.md`), which also covers the linked worktree.
- Legacy `sandbox_mode` in the user's Codex configuration and permission profiles exclude each other; the launch
  uses `--add-dir`, which both honour (inferred from the source, verified by the live turn).
- Claude Code keeps the native subagent; a `claude -p` process worker is not added.
