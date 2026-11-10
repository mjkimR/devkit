---
id: MAT-adaptive-runtime-references
created_at: 2026-11-10
summary: "Source-level survey of the CLI, hook and state mechanisms in oh-my-codex and oh-my-openagent and of three subagent packs, mapped to what adaptive development could implement as deterministic code."
---

# [MAT-adaptive-runtime-references] CLI, Hook and State Mechanisms in Agent Orchestration References

## 1. Purpose and Evidence Boundary

`MAT-adaptive-swarm-references` compared role catalogs and team topologies. It described the two orchestration
harnesses as prompt libraries with slash commands and did not examine their runtime code. This material records what
their CLIs, hooks and state files do in code, to inform whether adaptive development needs a package that carries
code (`MS-adaptive-development-runtime`).

Evidence is a read of shallow clones on 2026-11-10. Nothing from the clones was installed, built or run, so live
hook delivery and runtime behavior are unverified.

| Repository | Commit | License |
| --- | --- | --- |
| [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) (OMX) | `3219807de706` | MIT |
| [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) (OMO) | `2faeda01eaee` | Sustainable Use License 1.0 |
| [VoltAgent/awesome-codex-subagents](https://github.com/VoltAgent/awesome-codex-subagents) | `9abe3279a0aa` | MIT |
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | `8ae6164602c9` | MIT |
| [wshobson/agents](https://github.com/wshobson/agents) | `9c61ab243def` | MIT |

OMO's license restricts redistribution. This material describes its mechanisms and reproduces none of its text.

## 2. oh-my-codex

### 2.1 Hooks

`plugins/oh-my-codex/hooks/hooks.json` registers one command for eight Codex events; the handler is
`src/scripts/codex-native-hook.ts`.

| Event | Behavior in code | Failure it addresses |
| --- | --- | --- |
| `Stop` | Returns `decision: "block"` while an active mode has no terminal run state, a completion audit lacks evidence, or a team worker's assigned task is non-terminal. A persisted stop signature releases a repeated identical block. An explicit cancel is exempt. | Stopping with unfinished work; reporting completion without evidence; an endless block loop |
| `SessionStart` | Injects context built from per-mode state files and project memory. Blocks nothing. | Losing the active mode after resume or clear |
| `UserPromptSubmit` | Classifies keywords, injects a hint naming the matched or active skill and seeds mode state. | Forgetting the requested workflow |
| `PreToolUse` | Advisory only. A code comment records that planning and conductor hard gates were deleted; deny results are converted to messages except an exact-session cancel. | None enforced |
| `PostToolUse` | Records capacity and transport blockers; renews a team worker's task lease. | Stale task ownership |
| `PreCompact`, `PostCompact` | Build a context and discard it, because Codex accepts no hook output there. | None |
| `SubagentStop` | Registered; separate nudges for subagents and leaders. | Not traced |

### 2.2 CLI and state

- `omx team` starts workers in tmux panes and keeps tasks as `.omx/state/team/<name>/tasks/task-<n>.json`.
  Worktrees are used only with `--worktree`.
- A worker claims a task under a directory lock with a version compare-and-swap, dependency readiness and a random
  token with a 15-minute lease. An expired claim can be reclaimed. A wrapper renews the lease every five minutes.
- Marking a code-changing task completed requires an evidence JSON that carries the team, task and claim-token hash,
  is newer than the claim and has a summary, passing checks and an `unverified` array. The check covers shape and
  binding, not content.
- Overlap detection flags tasks that declare the same exact file path string. It changes the completion requirement
  and prevents no edit.
- `.omx/ultragoal/goals.json` and an append-only `ledger.jsonl` hold a durable plan and its checkpoints.
- Notes, plans and the evidence content are written by the model through prompt instructions.

## 3. oh-my-openagent

### 3.1 Plugin hooks

The OpenCode edition runs about 60 hook factories inside the host process.

- Continuation on `session.idle`: a todo enforcer, a plan-progress continuation and a completion-tag loop re-prompt
  the same session while work remains. Each has a stop guard: three idle cycles without progress, five consecutive
  failures, three continuations without a file or shell tool call, or an iteration cap.
- Context limits: a summarize call at 78% of the context limit, recovery after a context-limit error, and a snapshot
  of todos and agent identity around compaction. These use in-process host APIs.
- A guard blocks overwriting an existing file the session has not read.
- A background manager queues subagents per model key (default 5), limits spawn depth to 3 and live descendants to
  24, aborts sessions stale for 45 minutes and wakes the parent on completion.

### 3.2 Codex edition

`packages/omo-codex/plugin/hooks/` holds 21 manifests that run external commands, the same model as a host command
hook:

- `Stop` checks decide whether a loop or plan execution must continue.
- `SubagentStop` verifies that an executor wrote an evidence file inside the evidence root, at least 40 characters
  long and newer than the transcript start, and blocks up to three times.
- A `PreToolUse` guard caps a session at 24 spawns and denies spawns until manual QA artifacts exist.
- State is `.omo/ulw-loop/{brief.md,goals.json,ledger.jsonl}`, written under a lock.

### 3.3 CLI and state

- The CLI is mostly setup and diagnostics. `run` is a headless wrapper that polls until todos are done, child
  sessions are idle and no continuation marker is active.
- `.omo/boulder.json` records the active plan, sessions, per-work status and a stale marker. Code writes it at the
  moment of each event; the model never does. Plan progress is the checkbox count of the plan Markdown.
- A new session reconciles dead works to paused before injecting the state.
- The default background path has no worktree isolation, and no file-ownership conflict prevention was found.

## 4. Subagent Packs

The three packs ship agent definition files and no orchestration runtime. `agency-agents` has conversion and
install scripts; `wshobson/agents` has per-host adapters and two plugins with hooks unrelated to orchestration.
Their formats and conversion findings are applied in the `adaptive-dev` bundle's import skill and conversion
playbook (`CAP-DLV-adaptive-development`).

## 5. Findings

1. **Stop gates are the main investment of both harnesses.** Each pairs the gate with a loop breaker.
2. **State is written by code at the event, not by the model before a pause.** Claims, transitions and work status
   are recorded when they happen. Adaptive development writes `.devkit/adaptive-dev.md` "when useful and before
   pausing", which an unplanned interruption or compaction skips.
3. **Compaction cannot be handled through Codex hooks.** OMX's handlers are no-ops there, and OMO's handling needs
   in-process APIs.
4. **Completion evidence checks are shape-only in both.** Neither compares a result with the repository.
5. **Neither prevents ownership conflicts between parallel writers.** Adaptive development's per-writer worktree and
   exclusive ownership rules are stricter by design.
6. **Hard `PreToolUse` gates were withdrawn in OMX.**
7. **Most code volume serves owned process spawning**: tmux panes, lease renewal, background queues, stale reaping
   and parent wake. A bundle that delegates through the host's native subagents needs none of it.

## 6. Mapping to Adaptive Development

devkit's hook assets target Codex only. A handler can return context of at most 4096 characters for `SessionStart`,
`UserPromptSubmit`, `PreToolUse` and `PostToolUse`; `Stop` accepts an empty response, and `PreCompact` and
`SubagentStop` are not supported events (`CAP-HOST-lifecycle-observation`).

| Candidate | Failure addressed | Feasible with current devkit | Assessed value |
| --- | --- | --- | --- |
| Assignment ledger commands | Assignment board lost after interruption or compaction | Yes, without hooks, on every host | High |
| Return verification command | Out-of-scope writes; completion without evidence | Yes | High |
| `Stop` and `SubagentStop` gate | Ending with outstanding assignments | No: needs a blocking response, the `SubagentStop` event and a Claude Code adapter | High, after the ledger exists |
| `SessionStart` injection | Next action forgotten on resume | Codex only | Medium with a ledger, low without |
| `PreToolUse` path guard or spawn cap | Out-of-scope writes; excess spawns | Advisory context only | Low |
| Process runner, model or keyword routing | None | Covered by hosts and subagent levels | None |

Two differences from the references follow from adaptive development's design:

- The Host assigns work directly, so a ledger needs assignment records, status transitions and stale detection on
  resume. Claim locks, leases and heartbeats exist in OMX because workers take tasks from a shared queue.
- Each assignment already has a worktree, a base identity and a write scope, so a verification command can compare
  the actual changed paths with the scope, check that the final commit descends from the base and check that each
  declared check has a recorded outcome. The references check only the shape of an evidence file.

The repository's test support `packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py` already scores
supplied combined-check and interrupted-writer evidence; those two scenarios are the ones a ledger and a
verification command would make deterministic.

## 7. Unverified

- OMX: the merge path, resume command internals, HUD and the `SubagentStop` handler.
- OMO: the code that enforces its read-only advisor, exact install writes and the live behavior of the Codex hooks.
- Whether a `Stop` gate on Claude Code can share one handler contract with Codex.
