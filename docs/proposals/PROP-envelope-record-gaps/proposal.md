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
    - governance/
    - packages/devkit/src/devkit/workflow/
    - packages/devkit-spec/src/devkit_spec/
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
  longer showed the real state of the review. The round count is also the subject of two open feedback items,
  `FB-review-loop-round-count-across-procedure-change` and `FB-review-round-count-before-markers`, which both ask
  whether a fold of the user's answers opens a fresh round; Development links them to this proposal.
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

Decisions of this Planning (evidence and the option comparison: `materials/spike-evidence.md`):

- **Q1** (`PADR-reverify-closes-challenger-rounds`): `reverify --from challenger-NN.yaml` closes a challenger round
  (`--resolve`, `--waive`); the `review` key keeps its name and may name a `challenger-NN.yaml`; the deciding state of
  `challenger` follows its last reverify. Planning writes one such reverify after each fold, at `medium` and `high`.
  Review-loop rounds recorded without the `round <N>;` marker count in envelope order within the segment. How a fold
  of the user's answers counts: open question `answer-fold-round`.
- **Q2** (`PADR-answer-envelopes-settle-worker-assumptions`): an `answer` envelope may carry
  `settles: [{assumption: <1-based position in the answered worker's assumptions>, decision}]`, written with
  `devkit workflow envelope answer --settle N=DECISION`; it holds and releases nothing.
- **Q3** (`PADR-proposal-boundaries-name-existing-paths`): a new rule `RULE-proposal-boundaries` checks that each
  `target_area` and `boundaries.owns` entry of a `draft`, `reviewing` or `accepted` proposal resolves (repository
  path, docs-root path, or capability area); the `<...>` placeholder is reported under its own message; warnings in
  `draft`, errors from `reviewing`. How a path the Development creates is declared: open question
  `new-boundary-paths`.

Affected:

- devkit-agt `devkit.workflow` envelope model, authoring and `answer`/`reverify` commands (Q1, Q2) with tests;
  `CAP-DLV-workflow-envelopes`.
- devkit-spec: the new rule with its guide and tests (Q3), the proposal template comment, `CAP-DLV-proposal-incubation`,
  `CAP-GOV-spec-rules`; bundle text `references/review-loop.md`, `references/worker-records.md`, the `planning-worker`
  contract (step 4) and the `plan-accept` request in `workflows/sdd-proposal.md`.
- No gate or policy change; no check of `sdd-proposal` starts reading challenger findings.

Coordination: `PROP-direct-planning-procedure` moves the ordered Planning steps out of the `planning-worker` contract
into a `spec` skill reference. Its Development should integrate first (size S, `dev_effort: low`); this Development
then puts the challenger-reverify step into that reference instead of the contract. If this one integrates first, the
other moves the reworded step 4 as written.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr envelope-record-gaps "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff envelope-record-gaps`.
- On rejection: `status: rejected` with the user's reason in the commit message.
