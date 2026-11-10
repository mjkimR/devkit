---
id: PROP-adaptive-lifecycle-hooks
title: Lifecycle hook gates for adaptive delegation
summary: "Investigate the measured effect and exact work scope of Stop, SubagentStop and SessionStart hooks that read the adaptive assignment ledger, and deliver them only if the investigation supports it."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: capabilities/host/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-adaptive-development-runtime
depends_on: [PROP-adaptive-assignment-cli]
boundaries:
  owns:
    - packages/
    - packages/devkit-dist/src/devkit_dist/features/host/
    - docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    - docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    - docs/capabilities/distribution/CAP-DIST-agent-projections.md
  excludes:
    - packages/devkit-spec/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-adaptive-lifecycle-hooks] Lifecycle hook gates for adaptive delegation

## 1. Background & Hypothesis

`MAT-adaptive-runtime-references` found that the two orchestration harnesses it surveyed invest most in a `Stop`
gate: a hook that reads recorded state and refuses to end a session while work is outstanding, paired with a loop
breaker. Both also inject recorded state at session start. The survey read code only; it ran no hook and measured
no effect.

devkit's hook assets target Codex only. A handler returns context for `SessionStart`, `UserPromptSubmit`,
`PreToolUse` and `PostToolUse`; `Stop` accepts an empty response, and `SubagentStop` is not a supported event
(`CAP-HOST-lifecycle-observation`). devkit manages no Claude Code hook registration (`CAP-DIST-agent-projections`,
host configuration boundary).

This proposal is investigation first. Planning establishes what is missing and what it costs to provide. Delivery
is a separate decision. A rejection with its evidence is a valid outcome.

Hypothesis: once assignments are recorded (`PROP-adaptive-assignment-cli`), a `Stop` and `SubagentStop` gate that
reads the ledger prevents sessions and workers from ending with outstanding assignments at a host-adapter cost that
is bounded and reusable by other bundles.

Planning's finding on the hypothesis, before any measurement:

- The host-adapter cost is bounded and sized (§3.3). It is small on Codex and concentrated in a second host.
- The `Stop` half is buildable on the candidate ledger with three small additions to it (§3.4).
- The `SubagentStop` half is buildable only narrowly. Under the candidate ledger a worker always ends with its
  assignment `open`, so the status is no block condition. A gate for an assignee in its own worktree can use other
  conditions, with one more ledger addition and one host fact that is not established. A gate for every assignee
  needs the assignment design changed (§3.4, §3.5).
- The effect is unmeasured and cannot be measured before the commands exist (§3.6).

## 2. Technical Spike Questions

The evidence is in `materials/`; each answer names its file. No host was run in Planning: every host fact is classed
`documented`, `code` or `probe` in `materials/host-capability-matrix.md`.

| Question | Answer | Where |
| --- | --- | --- |
| Q1 Effect | Not measured: the failures are defined against a ledger that does not exist yet. The commands and guidance already keep the board across an interruption and report scope and check failures; they leave three failures to the Host's attention (F1 ending with unnamed outstanding assignments, F2 acting before reading the ledger on resume, F3 a failed verification the worker could have repaired). The measurement is defined with six observations, each with its source, and four scenarios | §3.6; `materials/gate-behavior-and-measurement.md` §4 |
| Q2 Host contracts | Codex and Claude Code document the same contract for all three events: `decision: "block"` with a reason the model receives, `stop_hook_active`, `session_id` and `cwd`, subagent identity on `SubagentStop`, context injection at session start. Antigravity documents `Stop` and `SessionStart` with other shapes and no subagent event. No live probe ran in Planning; the procedures are written. One earlier record shows Codex delivering `SessionStart` and `Stop` to a prototype logger | §3.2; `materials/host-capability-matrix.md`, `materials/host-documentation-extraction.md`, `materials/live-probes.md` |
| Q3 Host adapter scope | Gaps G1 to G16, one of them not applicable. A stop decision and the `SubagentStop` event are small changes to the Codex adapter. A Claude Code adapter is a complex module: it puts a settings file that also holds permission settings under management, which changes the host configuration boundary in three capabilities. A new host needs no new receipt field, but the ownership and removal rules carry over unchanged only for a tracked shared file; which Claude Code file is written and where its ownership is recorded is an open decision inside that adapter | §3.3; `materials/devkit-gaps-and-work-breakdown.md` §3, §3.1 |
| Q4 Gate behavior | Two block conditions are possible: block when an outstanding ID is not named in `.devkit/adaptive-dev.md`, which matches F1 and reads a file the capability says is not parsed; or block when the outstanding set changed, which touches no contract and blocks about once per turn end in an active build. Both release on every failure and on the repeated stop. A wrong release costs what the absence of the gate costs; a wrong block is a new cost and can push an agent to close assignments to pass | §3.5; `materials/gate-behavior-and-measurement.md` §3 |
| Q5 Session start | Counts per status, one line per outstanding assignment (about 30 fit in 4,096 characters) and the commands to read next, injected only when something is outstanding. Over the static pointer it adds the state itself | `materials/gate-behavior-and-measurement.md` §3.3 |
| Q6 Applicability | A preset of its own in the `adaptive-dev` bundle; a project opts in by selecting it. A caller that selects only `adaptive-dev:agents` gets no hook. The gate makes no approach check, like the commands | `materials/gate-behavior-and-measurement.md` §3.4 |
| Q7 Decomposition | It follows from the Claude Code adapter, which is a complex module by itself. Without it the delivery is one spec. With it the delivery is two specs, and the proposal is then returned for decomposition with the two children named in the material. The design as first drafted, with a `SubagentStop` gate, is three | §3.7; `materials/devkit-gaps-and-work-breakdown.md` §5, §6 |
| Q8 Decision criteria | Fixed before measurement, as conventions for small samples: a Host `Stop` gate on a host when F1 recurs there (2 observed runs, or 2 of 5 `combined-check` runs), the chosen block condition would not have blocked correct pauses (fewer than 3 of 5 pause runs) and the host's probes pass; session-start injection when F2 recurs (2 of 5 `interrupted-writer` runs); the narrow `SubagentStop` gate when F3 is at least 20% of ten or more returns and the host reports a subagent's own directory; otherwise no delivery. The measurement ends at ten observed runs per host or 30 days after the commands are delivered | §3.6; `materials/gate-behavior-and-measurement.md` §4.4 |

## 3. Proposed Design & Impact

### 3.1 Planning decisions

No design decision is settled in this run: the delivery option is the user's (§3.8), and no PADR is written before
it. What the evidence settles:

- **The stop decision is one host-neutral response.** Codex and Claude Code document the same `decision: "block"`
  contract, so a handler returns one value and each adapter renders it.
- **Every failure releases.** A failed dispatch keeps printing `{}` with exit `0`
  (`CAP-HOST-lifecycle-observation` §4). A gate that holds a session because devkit failed is excluded.
- **Antigravity is not carried forward.** Its registration file, input fields and stop response differ from the
  other two hosts, it documents no subagent event and no failure behavior, and its adapter is a complex module of
  its own (`materials/devkit-gaps-and-work-breakdown.md`, W5).
- **`PreToolUse` enforcement stays out of scope.** Nothing in the evidence challenges that exclusion.
- **`boundaries` and `dev_effort` are unchanged.** They are revised with the option that is carried forward.

Left to the specification of whatever is delivered, with the evidence in the materials: the block condition of the
`Stop` gate (§3.5), and the Claude Code settings file with the place of its ownership record
(`materials/devkit-gaps-and-work-breakdown.md` §3.1).

### 3.2 What the hosts provide

| Need | Codex | Claude Code | Antigravity | devkit |
| --- | --- | --- | --- | --- |
| `Stop` hook | Documented | Documented | Documented | Codex only |
| `SubagentStop` hook | Documented | Documented | Absent | Not an event |
| `SessionStart` hook and context | Documented | Documented | Documented, other shape | Codex only |
| Blocking decision with a reason | Documented | Documented | Documented, other shape | Missing from the handler contract |
| Repeated-stop signal | `stop_hook_active`; a host cap is unknown | `stop_hook_active` and a cap of eight continuations without a tool call | Unknown | Passed through |
| Host session against subagent | By event; `Stop` inside a subagent thread is unknown | By event, documented | Unknown | Passed through |
| Project registration file | `.codex/hooks.json`, hook review required | `.claude/settings.json` or `.claude/settings.local.json`, shared with permission settings | `.agents/hooks.json` | `.codex/hooks.json` only |
| Behavior on timeout or failure | Unknown | Released by the documented general rules; no sentence specific to `Stop` was captured | Unknown | Released |

A gate that cannot run releases silently on both documented hosts: an unreviewed hook on Codex, a `devkit` that is
not on the host's PATH, a timeout.

What has been observed on a host is narrow. One earlier spike recorded Codex delivering project-registered
`SessionStart` and `Stop` hooks to a prototype logger
(`docs/materials/2026-10/20261017-hook-driven-integration-cleanup/codex-spike-evidence.md`). Not observed: devkit's
generated hook command run by a host, a block decision, `stop_hook_active`, a subagent event, timeout and failure
behavior, and any hook on Claude Code.

### 3.3 What devkit lacks and what it costs

| # | Work item | Size |
| --- | --- | --- |
| W1 | Stop decision in the handler contract, rendered for Codex | S |
| W2 | `SubagentStop` event for Codex | S |
| W3 | Dispatch observation for every handler, so `devkit host status` shows that a hook ran | S |
| W4 | Claude Code hook adapter, with the decision on its settings file and the host configuration boundary | L |
| W5 | Antigravity hook adapter | L |
| W6 | Ledger additions for a Host gate, in the assignment feature (§3.4) | S |
| W6b | Paths outside the scope in the list observation of an open assignment | S |
| W7 | Session-start handler and hook preset in `devkit-adaptive` | M |
| W8 | Host `Stop` gate handler | M |
| W9a | Narrow `SubagentStop` gate, for an assignee in its own worktree | M |
| W9b | `SubagentStop` gate for every assignee, after a change to the assignment design | L |
| W10 | Probes and measurement | Not a spec |

`materials/devkit-gaps-and-work-breakdown.md` §4 lists the modules, tests, documents, dependencies and risk of each.

### 3.4 What the gate needs from the ledger

Read from `PROP-adaptive-assignment-cli` at commit `0cf00a40` of its Planning branch; that design is not accepted.

| Need | Candidate design |
| --- | --- |
| A read interface for a handler; defined results for a missing or damaged ledger; a stable contract | Supplied |
| A read that fits a hook timeout: statuses without one `git status` per open assignment | Missing; an option on the list use case |
| The assignments of the stopping session: the checkout that recorded each one | Missing; one recorded field on `new`. The ledger is shared by every worktree of the repository, so without it a gate blocks unrelated sessions |
| Git calls that ignore the hook process's Git environment | Left open there |
| A mapping from a stopping subagent to its assignment | Derivable only for an assignee in its own worktree, and only if the host reports that directory |
| A condition that is true when a worker must not stop yet | Not the status: the delegating agent records the return after the worker has stopped. Unclosed children and uncommitted paths are derivable; paths outside the scope need an addition to the list observation |

The first three missing rows are W6; the scope observation is W6b.

### 3.5 Gate behavior

`materials/gate-behavior-and-measurement.md` §3 holds the decision tables. The properties the sizing rests on:

- The `Stop` gate has two candidate block conditions (Q4). The name-aware one keeps no state and needs one sentence
  of `CAP-DLV-adaptive-development` changed; the state-only one keeps one small record per session.
- The second stop is the explicit cancel. No cancel command is added.
- A missing or empty ledger releases silently; an unreadable ledger releases with the existing warning.
- On Claude Code a stop while subagents still run is released, if `background_tasks` lets a running subagent be told
  from a background shell (probe CC-4).
- devkit finds the project from the event's `cwd`. An event whose `cwd` is another worktree is checked against that
  checkout and releases where its registration is absent (gap G16).

### 3.6 Effect and decision criteria

The criteria of `materials/gate-behavior-and-measurement.md` §4.4 are fixed before any measurement. The measurement
runs on the hosts the user works on, after the commands exist, with the hook preset absent; after a delivery it is
repeated with the preset selected. The Host or the user takes both, in live host sessions: a development worker
cannot run a host with a hook registered.

### 3.7 Delivery options

| Option | Items | Specs | Prevents |
| --- | --- | --- | --- |
| (a) Codex only: blocking `Stop` and session start | W1, W3, W6, W7, W8 | 1, size L | F1 and F2 on Codex |
| (b) Codex and Claude Code | (a) plus W4 | 2 | F1 and F2 on both |
| (c) Session-start injection only | W7 and W3; W4 for Claude Code | 1, size M; 2 with Claude Code | F2 |
| (d) No delivery | None | 0 | Nothing beyond the commands |
| (e) Decide after the measurement | W10, then (a) to (d) by the criteria | 0 now | Nothing until the decision |

The narrow `SubagentStop` gate (W2, W6b, W9a) is an addition to (a) or (b): one further spec of size M after the
Host gate.

Recommendation: (e), for two reasons. No option as packaged can start before the commands exist: W1 to W5 could,
but they would deliver a contract without a consumer. And the cost of a wrong release is the cost of having no
gate, while a wrong block is a new one, so the gate is worth its cost only where the failure recurs.
`materials/devkit-gaps-and-work-breakdown.md` §5 states what (e) consists of: the trigger, who measures, when it
ends, and what happens to this unit and its materials while it waits.

If a delivery is wanted without the measurement, the smallest depends on the host of the user's adaptive Host
sessions (q1): on Codex it is (c), which changes no hook contract and blocks nothing; on Claude Code it starts with
W4.

Under (b), or (c) with Claude Code, the proposal is returned for decomposition into a host child and an adaptive
child.

### 3.8 Open questions

- **q1 Host of the adaptive Host sessions**: Codex, Claude Code or both. The repository does not say, and it decides
  what each option prevents.
- **q2 Delivery option**: which of (a) to (e) is carried forward. Recommended: (e), with this unit ended without
  acceptance and its materials retained.
- **q3 Live probes**: when the probes of `materials/live-probes.md` run. Recommended: now, before the measurement.
- **q4 Session start after compaction**: whether session-start injection also fires when the host reports the
  `compact` source. Recommended: yes; it applies only if an option with session-start injection is delivered.

One item is for the Host, not the user: whether W6 enters `PROP-adaptive-assignment-cli` while it is in Planning.
The recorded checkout cannot be added to assignments recorded before the field exists, and observed runs in a
repository with concurrent sessions are counted only once it exists.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr adaptive-lifecycle-hooks "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept adaptive-lifecycle-hooks --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff adaptive-lifecycle-hooks.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
