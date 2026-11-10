---
id: PROP-adaptive-lifecycle-hooks
title: Lifecycle hook gates for adaptive delegation
summary: "Investigate the measured effect and exact work scope of Stop, SubagentStop and SessionStart hooks that read the adaptive assignment ledger, and deliver them only if the investigation supports it."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: capabilities/host/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-adaptive-development-runtime
depends_on: [SPEC-adaptive-assignment-cli]
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
host configuration boundary). A gate therefore needs host adapter changes in `devkit-dist` before any adaptive
handler.

This proposal is investigation first. Planning measures the effect and sizes the work, and accepts delivery only
when both support it. A rejection with its evidence is a valid outcome.

Hypothesis: once assignments are recorded (`SPEC-adaptive-assignment-cli`), a `Stop` and `SubagentStop` gate that
reads the ledger prevents sessions and workers from ending with outstanding assignments at a host-adapter cost that
is bounded and reusable by other bundles.

## 2. Technical Spike Questions

- **Q1 Effect**: How often do real adaptive runs end with outstanding or unverified assignments, or lose the next
  action on resume, when only the ledger commands exist? Measure with observed runs or the evaluation scenarios
  (`combined-check`, `interrupted-writer`), and state what the commands alone already prevent.
- **Q2 Host contracts**: What do Codex, Claude Code and Antigravity support for `Stop`, `SubagentStop` and
  `SessionStart`: blocking responses, payload fields that distinguish a Host session from a subagent, timeouts and
  repeated-stop signals? Verify against current primary documentation and one live probe per host, not by reading
  third-party code.
- **Q3 Host adapter scope**: What changes in `devkit_dist.features.host`: a blocking response in the handler
  contract, new events, a Claude Code adapter and its registration file? Does managing a Claude Code settings file
  change the host configuration boundary, and which receipt and removal rules follow?
- **Q4 Gate behavior**: Which ledger states block a stop? How does the gate release: a loop breaker on a repeated
  block, an explicit cancel, a stale or unreadable ledger? State the failure cost of a wrong block and of a wrong
  release.
- **Q5 Session start**: What does a `SessionStart` handler inject within 4096 characters, and what does it add over
  the existing guidance pointer?
- **Q6 Applicability**: Do the gates apply to callers under SDD that select only the `agents` preset, and how does a
  project opt in or out?
- **Q7 Decomposition**: Is the work one spec, or a host adapter spec plus an adaptive handler spec? If two, set
  `size: XL` and return for decomposition.
- **Q8 Decision criteria**: Which measured effect and which scope make delivery worthwhile, stated before the
  measurements are read?

## 3. Proposed Design & Impact

Candidate design, subject to the investigation:

- `devkit_dist.features.host`: a blocking response for `Stop`, the `SubagentStop` event and a second host adapter.
- `devkit-adaptive`: handlers that read the assignment ledger, a gate with a loop breaker and a session-start
  summary; hook assets in the `adaptive-dev` bundle under an opt-in preset.
- No `PreToolUse` enforcement, no compaction handling and no process runner.

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
