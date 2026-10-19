---
id: PROP-direct-planning-procedure
title: Planning procedure reachable from the spec skill for any executor
summary: Moves the ordered Planning steps out of the planning-worker contract into a spec skill reference that direct-mode Hosts and workers both follow, so the procedure lives in one place.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: harness/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - harness/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-direct-planning-procedure] Planning procedure reachable from the spec skill for any executor

## 1. Background & Hypothesis

- **Problem**: The `spec` skill's routing table says Planning "runs on `plan-<slug>` to `plan-accept`", and
  `effort.md` gives the review depth per effort, but the ordered Planning steps (set `status: reviewing` and commit,
  record decisions as PADRs, gather questions in one round, update `dev_effort`, sweep feedback, end with one `worker`
  envelope) are written only in the `planning-worker` role contract. A Host running Planning in `direct` mode has to
  read a subagent contract written for another actor (`FB-direct-planning-procedure-location`).
- **Hypothesis**: One Planning reference in the `spec` skill, which the `planning-worker` contract cites instead of
  owning, gives every executor the same steps and leaves one place to change them.

## 2. Technical Spike Questions

- **Q1**: Which steps are executor-neutral and move to the reference, and which stay in the role contract (nested
  delegation, returning the head to the Host)?
- **Q2**: Can the move fit the existing bundle byte budgets of the `spec` skill and the role contract, or does another
  reference need trimming?

## 3. Proposed Design & Impact

- A new `spec` skill reference for Planning, linked from the routing table's proposal row.
- The `planning-worker` contract keeps only its role-specific obligations and points to the reference.
- Affected: the devkit-spec bundle (`spec` skill, `planning-worker` contract) and `CAP-HARN-agent-guidance` if it
  describes where procedures live. No CLI or schema change.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr direct-planning-procedure "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff direct-planning-procedure`.
- On rejection: `status: rejected` with the user's reason in the commit message.
