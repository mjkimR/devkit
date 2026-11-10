---
id: PROP-adaptive-assignment-cli
title: Assignment ledger and return verification commands for adaptive delegation
summary: "Add commands that record delegated assignments and verify a returned result against its assignment, so a Host resumes outstanding work from recorded state and checks scope, source identity and declared checks deterministically."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-adaptive-development-runtime
depends_on: [PROP-adaptive-package-extraction]
boundaries:
  owns:
    - packages/
    - docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    - docs/usecases/delivery/UC-advance-an-idea.md
    - docs/development/reference/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-dist/src/devkit_dist/features/host/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-adaptive-assignment-cli] Assignment ledger and return verification commands for adaptive delegation

## 1. Background & Hypothesis

In adaptive development the Host delegates to swarm agents with a goal, source identity, exclusive write scope,
checks and return fields (`CAP-DLV-adaptive-development` rules 13 and 13a). The assignment board exists only in the
Host's context. `.devkit/adaptive-dev.md` is free Markdown the Host updates "when useful and before pausing", so an
unplanned interruption or context compaction loses outstanding assignments. The Host checks a returned result by
reading its diff; no command compares the result with the assignment.

`MAT-adaptive-runtime-references` records that comparable harnesses write assignment state in code when each event
happens and gate completion on it, and that their evidence checks stop at the shape of a file. Adaptive assignments
already carry a worktree, a base identity and a write scope, so a command can check the repository itself.

Hypothesis: a small command set that records assignments and verifies returns makes resume and completion checks
deterministic for large parallel builds without a scheduler, a process runner or per-change SDD records.

## 2. Technical Spike Questions

- **Q1 Command surface**: Which command group and verbs follow `CAP-CLI-agent-cli-toolkit`: recording an assignment,
  recording a return, verifying a return and listing outstanding assignments? Which sentinels, codes and exit codes
  does each produce, and is an out-of-scope write exit code `1`?
- **Q2 Ledger**: Where does the ledger live and in which format: tracked project state, `.devkit/transient/` or the
  shared Git directory so every worktree sees it? Is it append-only? Who may write it besides the Host?
- **Q3 Verification**: What does verification compare: committed and uncommitted changed paths against the write
  scope with which glob semantics, the final commit against the assigned base, and declared checks against recorded
  outcomes? Does recording an assignment reject a write scope that overlaps an open assignment?
- **Q4 Nesting**: How does a role lead's assignment relate to its children's assignments and aggregate result?
- **Q5 Reuse**: Which existing code applies: the `scope` and `worker` features of `devkit-spec`, `devkit worktree`
  and `devkit exec`? The package must not import `devkit_spec`; state whether harness features are required or
  optional.
- **Q6 Resume**: How is a stale assignment recognized without a heartbeat: worktree state, a retained commit or
  elapsed time?
- **Q7 Current context**: How do the ledger and `.devkit/adaptive-dev.md` relate? The Markdown stays Host-authored;
  decide whether it links the ledger or a command renders a summary into the reply.
- **Q8 Guidance**: How do the entry skill, its delegation and orchestration references and the swarm archetypes use
  the commands, and what is the fallback where they are unavailable, including callers under SDD that select only
  the `agents` preset?
- **Q9 Evidence scorer**: Is `adaptive_behavior_scorer.py` replaced by the commands, kept as test support or both?

## 3. Proposed Design & Impact

- A command group in `devkit-adaptive` with use cases under `features/` (`ARCH-05-2-components`).
- An assignment record: identifier, owner, role, worktree, base identity, write scope, governing documents, checks,
  dependency and status.
- A return record: final identity, changed paths, check outcomes, unverified areas.
- A verification result with stable codes for scope violation, base mismatch and missing check outcome.
- Guidance changes in the bundle that name the commands at assignment, return, pause and resume.

Excluded: host lifecycle hooks (`PROP-adaptive-lifecycle-hooks`), a scheduler or process runner, model routing and
SDD Units or envelopes.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr adaptive-assignment-cli "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept adaptive-assignment-cli --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff adaptive-assignment-cli.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
