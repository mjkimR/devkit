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

This proposal is investigation first. Planning establishes what is missing and what it costs to provide, and
accepts delivery only when a measured effect supports it. A rejection with its evidence is a valid outcome.

Hypothesis: once assignments are recorded (`PROP-adaptive-assignment-cli`), a `Stop` and `SubagentStop` gate that
reads the ledger prevents sessions and workers from ending with outstanding assignments at a host-adapter cost that
is bounded and reusable by other bundles.

Planning's finding on the hypothesis, before any measurement:

- The host-adapter cost is bounded and sized (§3.3). It is small on Codex and concentrated in a second host.
- The `Stop` half is buildable on the candidate ledger with three small additions to it (§3.4).
- The `SubagentStop` half is not: under the candidate ledger a worker always ends with its assignment `open`, so
  the ledger holds no condition that separates a finished worker from an unfinished one (§3.4).
- The effect is unmeasured and cannot be measured before the commands exist (§3.6).

## 2. Technical Spike Questions

The evidence is in `materials/`; each answer names its file. No host was run in Planning: every host fact is classed
`documented`, `code` or `probe` in `materials/host-capability-matrix.md`.

| Question | Answer | Where |
| --- | --- | --- |
| Q1 Effect | Not measured: the failures are defined against a ledger that does not exist yet. The commands and guidance already keep the board across an interruption and report scope and check failures; they leave three failures to the Host's attention (F1 ending with unnamed outstanding assignments, F2 acting before reading the ledger on resume, F3 a rejected return the worker could have repaired). The measurement is defined with five mechanical observations and four scenarios | §3.6; `materials/gate-behavior-and-measurement.md` §4 |
| Q2 Host contracts | Codex and Claude Code document the same contract for all three events: `decision: "block"` with a reason the model receives, `stop_hook_active`, `session_id` and `cwd`, subagent identity on `SubagentStop`, context injection at session start. Antigravity documents `Stop` and `SessionStart` with other shapes and no subagent event. No live probe ran; the procedures are written | §3.2; `materials/host-capability-matrix.md`, `materials/live-probes.md` |
| Q3 Host adapter scope | Fifteen gaps. A stop decision and the `SubagentStop` event are small changes to the Codex adapter. A Claude Code adapter is a complex module: it puts a settings file that also holds permission settings under management, which changes the host configuration boundary in three capabilities. The receipt needs no new field and the removal rule applies unchanged | §3.3; `materials/devkit-gaps-and-work-breakdown.md` §3 |
| Q4 Gate behavior | Block once when a top-level assignment recorded from this checkout is not `closed`, the host's `stop_hook_active` is false and the outstanding set differs from the one this session was last blocked for. Release on everything else, every failure included. A wrong release costs what the absence of the gate costs; a wrong block is a new cost and can push an agent to close assignments to pass | §3.5; `materials/gate-behavior-and-measurement.md` §3 |
| Q5 Session start | Counts per status, one line per outstanding assignment (about 30 fit in 4,096 characters) and the commands to read next, injected only when something is outstanding. Over the static pointer it adds the state itself | `materials/gate-behavior-and-measurement.md` §3.3 |
| Q6 Applicability | A preset of its own in the `adaptive-dev` bundle; a project opts in by selecting it. A caller that selects only `adaptive-dev:agents` gets no hook. The gate makes no approach check, like the commands | `materials/gate-behavior-and-measurement.md` §3.4 |
| Q7 Decomposition | It depends on the option carried forward. Codex only is one spec. With a Claude Code adapter it is two specs, and the proposal is then returned for decomposition with the two children named in the material. The design as first drafted, with a `SubagentStop` gate, is three | §3.7; `materials/devkit-gaps-and-work-breakdown.md` §5, §6 |
| Q8 Decision criteria | Fixed before measurement: a Host `Stop` gate on a host when F1 occurs in at least 2 of 10 observed runs or 2 of 5 `combined-check` runs there and the host's probes pass; session-start injection when F2 occurs in at least 2 of 5 `interrupted-writer` runs; a `SubagentStop` gate when F3 is at least 20% of returns and the assignment design is changed first; otherwise no delivery | §3.6; `materials/gate-behavior-and-measurement.md` §4.4 |

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
- **A `SubagentStop` gate is in no delivery option.** It needs the assignment design changed first (§3.4).
- **`boundaries` and `dev_effort` are unchanged.** They are revised with the option that is carried forward.

### 3.2 What the hosts provide

| Need | Codex | Claude Code | Antigravity | devkit |
| --- | --- | --- | --- | --- |
| `Stop` hook | Documented | Documented | Documented | Codex only |
| `SubagentStop` hook | Documented | Documented | Absent | Not an event |
| `SessionStart` hook and context | Documented | Documented | Documented, other shape | Codex only |
| Blocking decision with a reason | Documented | Documented | Documented, other shape | Missing from the handler contract |
| Repeated-stop signal | `stop_hook_active`; a host cap is unknown | `stop_hook_active` and a cap of eight continuations | Unknown | Passed through |
| Host session against subagent | By event; `Stop` inside a subagent thread is unknown | By event, documented | Unknown | Passed through |
| Project registration file | `.codex/hooks.json`, hook review required | `.claude/settings.json` or `.claude/settings.local.json`, shared with permission settings | `.agents/hooks.json` | `.codex/hooks.json` only |
| Behavior on timeout or failure | Unknown | Released, documented | Unknown | Released |

Two findings hold on both documented hosts. A gate that cannot run releases silently: an unreviewed hook on Codex, a
`devkit` that is not on the host's PATH, a timeout. And nothing has been observed: the repository records no
delivery of any hook by a host, the existing Codex path included.

### 3.3 What devkit lacks and what it costs

| # | Work item | Size |
| --- | --- | --- |
| W1 | Stop decision in the handler contract, rendered for Codex | S |
| W2 | `SubagentStop` event for Codex | S |
| W3 | Dispatch observation for every handler, so `devkit host status` shows that a gate ran | S |
| W4 | Claude Code hook adapter, with the decision on its settings file and the host configuration boundary | L |
| W5 | Antigravity hook adapter | L |
| W6 | Ledger additions in the assignment feature (§3.4) | S |
| W7 | Session-start handler and hook preset in `devkit-adaptive` | M |
| W8 | Host `Stop` gate handler | M |
| W9 | `SubagentStop` gate, after a change to the assignment design | L |
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
| A mapping from a stopping subagent to its assignment | Missing, and not derivable in general |
| A condition that is true when a worker must not stop yet | Missing by design: the delegating agent records the return after the worker has stopped, and `verify` needs a return |

The first three missing rows are W6. The last two are why W9 needs the assignment design changed.

### 3.5 Gate behavior

`materials/gate-behavior-and-measurement.md` §3 holds the decision table. The properties the sizing rests on:

- The gate blocks at most once per changed set of outstanding assignments in a session. This needs one small record
  per session, kept by the handler's package.
- The second stop is the explicit cancel. No cancel command is added.
- A missing or empty ledger releases silently; an unreadable ledger releases with the existing warning.
- On Claude Code a stop while assigned subagents still run is released, if the `background_tasks` field carries what
  its name says (probe CC-4).

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
| (c) Session-start injection only | W6, W7; W4 for Claude Code | 1, size M; 2 with Claude Code | F2 |
| (d) No delivery | None | 0 | Nothing beyond the commands |
| (e) Decide after the measurement | W10, then (a) to (d) by the criteria | 0 now | Nothing until the decision |

Recommendation: (e). No option can start before the commands exist; the cost of a wrong release is the cost of
having no gate, while a wrong block is a new one; and the milestone asks for a decision based on a measured effect
(`MS-adaptive-development-runtime`, exit condition). Waiting loses no delivery time. If a delivery is wanted without
the measurement, (c) on Codex is the smallest: it changes no hook contract, blocks nothing and gives the first live
observation of the hook path.

Under (b), or (c) with Claude Code, the proposal is returned for decomposition into a host child (W1 to W4) and an
adaptive child (W7, W8).

### 3.8 Open questions

- **q1 Delivery option**: which of (a) to (e) is carried forward. Recommended: (e).
- **q2 Live probes**: when the probes of `materials/live-probes.md` run. Recommended: at the decision point, before
  any delivery option is accepted.
- **q3 Session start after compaction**: whether session-start injection also fires when the host reports the
  `compact` source. Recommended: yes; it applies only if an option with session-start injection is delivered.

One item is for the Host, not the user: whether W6 enters `PROP-adaptive-assignment-cli` while it is in Planning.
The recorded checkout cannot be added to assignments recorded before the field exists.

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
