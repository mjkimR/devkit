---
id: ADR-reject-adaptive-lifecycle-hooks
title: Reject lifecycle hook gates for adaptive delegation
summary: "For Host-orchestrated adaptive runs with the user present, we reject hook gates over the assignment ledger, to avoid a second host adapter and wrong blocks for little gain, accepting that a Host ending a turn with unnamed outstanding assignments is caught only by the user."
status: accepted
created_at: 2026-11-10
---

# [ADR-reject-adaptive-lifecycle-hooks] Reject lifecycle hook gates for adaptive delegation

- **Status**: Accepted
- **Date**: 2026-11-10
- **Deciders**: the repository owner
- **Involved Components/Capabilities**: `capabilities/host/`, `CAP-DLV-adaptive-assignments`, the `adaptive-dev` bundle

---

## 1. Context & Problem Statement

The proposal ~~`PROP-adaptive-lifecycle-hooks`~~ (rejected in commit `8a725e5d`, deleted in this ADR's commit)
hypothesized that a `Stop` and `SubagentStop` hook gate reading the adaptive assignment ledger would keep sessions
and workers from ending with outstanding assignments, and that session-start injection would put the recorded state
in front of a resumed Host. Two orchestration harnesses surveyed in `MAT-adaptive-runtime-references` invest most in
such a gate.

Its first Planning turn, retained as `MAT-adaptive-lifecycle-hooks`, found:

- A worker always ends with its assignment `open`, because the delegating agent records the return after the worker
  stops. The status is no `SubagentStop` block condition; only a narrow gate for an assignee in its own worktree is
  buildable, on a host fact not established.
- A Host `Stop` gate must release a stop while subagents run in the background. What it adds is one failure: the
  Host ending a turn with outstanding assignments it does not name.
- devkit registers hooks on Codex only (`CAP-HOST-lifecycle-observation`). A Claude Code gate first needs a host
  adapter, size M with a registration the user installs or L with one devkit manages in a settings file that also
  holds permission settings. Antigravity documents another contract and no subagent event.
- No effect was measured and no host ran a hook; the host facts come from vendor documentation.

---

## 2. Decision Drivers

- A gate is worth its cost only where the failure it catches recurs; a wrong block is a new cost and can push an
  agent to close assignments to pass.
- In the owner's usage a Host session orchestrates the subagents and the owner stays in the conversation, so a turn
  end is seen when it happens.
- A capability that cannot be delivered on the host in use is not delivered for one host alone.

---

## 3. Considered Options

### Option 1: Reject without delivery (Selected)
- **Overview**: no hook gate and no session-start injection; the assignment commands and the static guidance stay
  as delivered.
- **Pros**: no handler contract change, no second host adapter, no wrong blocks.
- **Cons**: the failures F1 (ending with unnamed outstanding assignments) and F2 (acting before reading the ledger on
  resume) keep the cost they have without a gate.

### Option 2: Defer the decision until a measurement
- **Overview**: run the live probes and count F1 to F3 over ten runs per host or 30 days, then decide by criteria
  fixed in advance.
- **Cons**: a measurement program for a failure the owner's usage pattern rarely exposes.

### Option 3: Deliver session-start injection or a `Stop` gate now
- **Overview**: the smallest deliveries, sized at one spec of size M on Codex or size L with a Claude Code adapter.
- **Cons**: delivered without evidence of effect, and on Codex alone it prevents nothing in Claude Code sessions.

---

## 4. Decision Outcome

We decided to adopt **Option 1**, because the owner judged in the rejection commit that lifecycle hook gates would
not help much in their usage pattern.

- devkit adds no `Stop`, `SubagentStop` or `SessionStart` handler that reads the assignment ledger, and the host hook
  contract gains no blocking decision for this purpose.
- The Planning evidence (host capability matrix, gaps and sized work items, gate behavior, measurement criteria and
  live probe procedures) is retained as `MAT-adaptive-lifecycle-hooks`.
- A later gate starts as a new proposal that cites recurring F1 or F2 observations from real adaptive runs.

---

## 5. Consequences

- **Positive**: the host feature keeps one adapter and its release-on-failure contract; the assignment ledger keeps
  no reader beyond its commands.
- **Negative / Risks**: a Host that forgets outstanding assignments at a turn end is caught only by the user.
- **Follow-ups**: none. Recurring F1 or F2 reopens the question as a new proposal.

---

## 6. Confirmation

Review only: `CAP-HOST-lifecycle-observation` lists no blocking stop decision, and the `adaptive-dev` bundle ships no
hook preset.
