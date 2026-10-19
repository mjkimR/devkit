---
id: PROP-envelope-record-gaps
title: 'Close gaps in Planning records: folded challenger findings, settled assumptions, proposal boundaries'
summary: Lets folded challenger findings close in the record, gives answer envelopes a place for assumptions the user settled, and checks that a proposal's boundaries name existing areas, so Planning records match what actually happened.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-envelope-record-gaps] Close gaps in Planning records: folded challenger findings, settled assumptions, proposal boundaries

## 1. Background & Hypothesis

- **Folded challenger findings stay open** (`FB-challenger-findings-stay-open`): a planning worker folds every
  `challenger` finding into the proposal, but the envelope keeps them `open`, because only a `reverify` closes findings
  and it must name a `review-NN.yaml`. On 2026-10-19 both high-effort Planning units reported findings as open that
  had been fixed, and both counted earlier unmarked challenger rounds toward the review-loop cap, so the record no
  longer showed the real state of the review.
- **Settled assumptions have no slot** (`FB-answer-envelope-no-slot-for-settled-assumptions`): when the user's answer
  also settles a worker assumption, the answer envelope can only carry it as free text in a constraint.
- **Proposal boundaries are unchecked** (`FB-proposal-boundaries-unchecked`): `boundaries.owns` may name a capability
  area that does not exist (`capabilities/core/`), and no rule reports it.
- **Hypothesis**: small record and rule changes make Planning records match the work, without changing gates.

## 2. Technical Spike Questions

- **Q1 (Challenger closure)**: a `reverify`-like closing record for `challenger` envelopes, `--resolve` on a later
  `challenger` round, or a rule that a folded finding is resolved by the next round's summary; and how the review-loop
  round count treats rounds recorded before the `round <N>;` marker.
- **Q2 (Settled assumptions)**: a field in the `answer` item (for example `settles: [<assumption text or id>]`) or a
  convention in `decision`; whether worker assumptions need ids for this.
- **Q3 (Boundaries rule)**: a rule that every `boundaries.owns` and `target_area` entry names an existing area or path,
  with the placeholder `capabilities/<area>/` reported separately.

## 3. Proposed Design & Impact

- Affected: `devkit.workflow` envelope kinds and validation (Q1, Q2), `CAP-DLV-workflow-envelopes`, the planning-worker
  contract and `review-loop.md`, and a devkit-spec rule for proposal frontmatter (Q3).
- No gate or policy change.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr envelope-record-gaps "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff envelope-record-gaps`.
- On rejection: `status: rejected` with the user's reason in the commit message.
