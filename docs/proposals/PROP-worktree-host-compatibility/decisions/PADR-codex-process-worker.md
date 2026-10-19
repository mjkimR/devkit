---
id: PADR-codex-process-worker
title: Codex worker as a separate process rooted in its worktree
summary: Offers a Codex Planning or Development worker turn as a codex exec process rooted in the activity's worktree with both git dirs granted, only once one live turn has passed the Host's range check; until then, or when it fails, the Codex main session keeps running the activity in direct.
proposal: PROP-worktree-host-compatibility
status: draft
created_at: 2026-10-19
---

# [PADR-codex-process-worker] Codex worker as a separate process rooted in its worktree

- **Status**: Draft; applies only if the user answers `codex-worker-scope` with `process-worker` (otherwise it is
  deleted before handoff and `PADR-worktree-access-preconditions` alone records the Codex reasons)
- **Date**: 2026-10-19
- **Answers**: Q3 and Q5 of `PROP-worktree-host-compatibility`; option O3. Evidence: `MAT-worktree-host-spike-evidence`
  §2.2, `envelopes/scout-02.yaml`; reviewed in `envelopes/challenger-01.yaml`.

---

## 1. Context & Problem Statement

On Codex the worker roles are `unsupported`, so the main session runs every activity in `direct`. The reason is
structural, not the worktree's location: `spawn_agent` keeps the parent's cwd, approval policy and permission profile,
a custom agent cannot override `sandbox_mode`, and `.git` plus the linked worktree's own git dir are read-only inside
every writable root unless named exactly. A process rooted in the worktree with both git dirs granted can commit there
(verified with `codex sandbox`); a subagent of a base-rooted session cannot.

## 2. Decision Drivers

- Worker delegation on Codex without weakening the Host's committed-range check.
- No host settings written by devkit (`PADR-worktree-access-preconditions`).
- No new projection status or allowlisted key in `devkit.distribution`; the change stays in devkit-spec assets.
- Codex sandboxes the Host's own commands: inside `:workspace` a nested sandbox cannot be applied, `~/.codex` is not
  writable and the network is off, so the Host cannot start the process inside its sandbox.
- What is shipped stays true whichever way the live verification ends.

## 3. Considered Options

- **Keep Codex `unsupported`; the main session runs each activity in `direct`.** Pros: no new procedure. Cons: no
  orchestration on Codex; `direct` in a sibling worktree already needs the Host's escalated writes.
- **A Codex session started by the user per worktree with the grants (O1 per run).** Cons: the user starts a session
  per activity and turn by hand; it is a second Host, not a worker the Host coordinates.
- **A `codex exec` process per worker turn, rooted in the worktree (selected).** Pros: the worker's cwd is its
  worktree; projected roles and skills are read from it (Q5). Cons: a separate model session and one escalated launch
  per turn; approval `never` inside `exec`, so any other blocked action fails; nested roles, trust for the linked
  worktree, the gate's tooling and the Host's command timeout are unverified until the live turn.

## 4. Decision Outcome

- The worker contracts MUST declare the process launch with the top-level extension key `x-process-hosts`, a list of
  host ids, and their Codex block stays `status: unsupported` (no `.codex/agents/<worker>.toml`). The key is added only
  in the verified branch below.
- **Launch** (verified branch): in `local-orchestrated` mode on a host named in `x-process-hosts`, after the access
  probe of `PADR-worktree-access-preconditions`, the Host runs each `planning-worker` or `development-worker` turn as
  one `codex exec -C <worktree> -s workspace-write --add-dir <repo>/.git --add-dir <repo>/.git/worktrees/<name>`
  process. The Host adds only these two grants and the sandbox mode; grants the user's own Codex configuration holds
  stay the user's. The prompt is the effective contract body (`.devkit/overrides/spec/subagents/<role>.md` when it
  exists, else `.devkit/managed/spec/subagents/<role>.md`) followed by the payload `spec-delegate` defines.
- The Host starts the process outside its own sandbox (an escalated command approved by the user or the configured
  auto review); a Host that cannot do so runs the activity in `direct`. The committed `worker` envelope and the final
  head are the return, validated exactly as for a subagent worker (`references/worker.md`); the process's last
  message is not trusted beyond them.
- `spec-delegate` Step 3 and `spec-orchestrate` MUST name the process launch as the path for a host listed in
  `x-process-hosts`, in place of substitution and of the nested-subagent precondition for that host;
  `spec-delegate/SKILL.md` stays within its tested budget (`BUDGET - 512` = 11776 bytes,
  `packages/devkit-spec/tests/test_bundle_budgets.py`).
- **Live verification** (Development): one Planning or Development turn through this launch on a Codex Host, recorded
  in the spec's materials with the command line, the codex version, the configuration mode (legacy `sandbox_mode` or
  a profile), the base and final head, the range-check result, a commit through the real commit gate, the affected
  tests, a nested role spawned inside the process and the turn's duration against the Host's command timeout.
  - **Passes**: the key, the launch text in `spec-delegate` and `spec-orchestrate`, and `CAP-DLV-delivery-workflows`
    ship as above.
  - **Fails**: nothing of the launch ships; the hosts reference and the contract comments record the failed
    condition, and Codex keeps the main session running the activity in `direct`.

## 5. Consequences

- Changes `spec-delegate` (`SKILL.md` Step 3, `references/hosts.md`), `spec-orchestrate`, the two worker contracts and
  their tests, and `CAP-DLV-delivery-workflows`; no devkit package change.
- Each Codex worker turn costs a separate model session and an approval.
- The two grants give the process the same shared `.git` access a Claude Code worker has through its session; the
  range check does not see it on either host (`PADR-worktree-access-preconditions` §5).
- Claude Code keeps the native subagent; a `claude -p` launch can be added later by listing `claude-code`.
