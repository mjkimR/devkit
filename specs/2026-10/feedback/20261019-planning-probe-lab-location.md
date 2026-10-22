---
id: FB-planning-probe-lab-location
title: Planning worker has no sanctioned place for throwaway probes that must run outside /tmp
scope: repo
kind: question
category: missing-capability
target: planning-worker role contract (Write boundaries) and spec-delegate references/payload.md (allowed_boundaries)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-planning-probe-lab-location] Planning worker has no sanctioned place for throwaway probes that must run outside /tmp

## 1. Friction / Question (friction, question)

- **Context**: A Planning turn had to answer a spike question with evidence about a host sandbox: whether Codex's
  `workspace-write` profile lets a process commit from a sibling linked worktree. The cheap, deterministic test is
  `codex sandbox` against a throwaway repository with linked worktrees, no model session.
- **Expectation**: The worker's write boundary (the proposal directory) plus the session scratchpad covers throwaway
  experiments.
- **Actual**: The session scratchpad lives under `/private/tmp`, which the Codex `:workspace` profile always allows,
  so every confinement probe there passed and showed nothing. A meaningful probe needed a location outside `/tmp`, and
  the only writable one inside the boundary was the proposal directory itself.
- **Workaround (or Interpretation Chosen)**: Created an untracked `.lab/` directory with nested throwaway
  repositories inside the proposal directory, ran the probes, removed the linked worktrees with
  `git worktree remove` and the directory before the next commit, and kept only the results in `materials/`. I read
  the boundary as allowing temporary, never-committed files inside the proposal directory; nothing states it.
- **Suggestion**: State in the worker contracts (or the payload reference) whether temporary, uncommitted files
  inside the write scope are allowed for experiments and must be gone before the worker's last commit (the Host's
  `git status --short` check already requires a clean worktree), or name a scratch location outside `/tmp`.

## Diagnostic Details

- **Reproduction**: `codex sandbox -P :workspace -C <scratch>/base -- sh -c "echo a > <scratch>/base-wt-x/f"` with
  `<scratch>` under `/private/tmp`: allowed; the same with the lab under the proposal directory: denied.
- **Expected / Actual**: Expected a denial for a write outside the root; observed success under `/tmp` only.
- **Versions**: codex-cli 0.160.1, macOS seatbelt; Claude Code 2.1.303 Host.
- **Conditions**: local-orchestrated Planning turn, write scope limited to the proposal directory.
- **Workarounds Attempted**: `-c sandbox_workspace_write.exclude_slash_tmp=true` and a changed `TMPDIR` had no effect
  under the `:workspace` profile; the in-scope lab worked.
- **Related Assets**: `planning-worker` Write boundaries; `spec-delegate` `references/payload.md`;
  ~~`MAT-worktree-host-spike-evidence`~~ §2.2.

## Evidence

```text
planning-worker.md, Write boundaries:
  Allowed: the proposal directory (proposal.md, decisions/, materials/, target-docs.md, its envelopes) inside the
  worktree, and a new draft proposal for a follow-up.
Probe under /private/tmp: "1 root=base: write file in sibling wt rc=0"
Probe under <worktree>/docs/proposals/PROP-<slug>/.lab: "1 root=base: write file in sibling wt rc=1"
```

Historical source: Git `1b8478093a44cf2d0b74c412bffc93f259459ef0:docs/proposals/PROP-worktree-host-compatibility/feedback/planning-probe-lab-location.md`; relative evidence paths refer to that proposal bundle.

## Disposition

Directly resolved by `SPEC-feedback-planning-parser`. The Planning payload names an ignored probe path within the proposal write boundary, requires temporary-repository cleanup before the last commit and retains only evidence in materials. Unsupported locations require Host boundary expansion.

Independent medium code review passed all four acceptance criteria without findings. The affected suite passed
1,113 tests, including parser default/order/error cases and existing consumer checks; lint, type checks and
cumulative governance checks passed. This disposition records verified branch work, not integration.
