---
id: PROP-high-effort-review-loop
title: Bounded high-effort review procedure
summary: 'Redefines the high activity-effort procedure: whole-batch review rounds that end when a round finds nothing or every fix is minor, hand-over for persistent, recurring or contested P1s, P1-P3 severity, mandatory scout in high Planning, and session reclassification advice.'
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
    - packages/devkit-spec/src/devkit_spec/bundle/
    - packages/devkit-spec/tests/
    - docs/decisions/2026-10/20261016-medium-review-delegation.md
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-high-effort-review-loop] Bounded high-effort review procedure

- **Origin**: `ADR-medium-review-delegation` defined `medium` in detail and kept `high` as it was: "High retains code
  re-review after fixes and independent reconcile verification". `high` was never designed on its own.
- **Decided in Backlog**: the direction (review loop that hands over persistent P1s, minor-fix exception for code and
  reconcile, severity levels, mandatory `scout` in `high` Planning, session reclassification advice). Out of scope: a
  plan-review role and model or reasoning settings.
- **Planning effort**: `medium` by the user's choice, though the change replaces a clause of an accepted ADR: the
  options were compared before Backlog closed, so one `challenger` pass (`envelopes/challenger-01.yaml`) reviews how
  they are specified.
- **Decision record**: `PADR-bounded-high-effort-review-loop` (promoted to an ADR at handoff).
- **Related**: `ADR-medium-review-delegation`, `ADR-reconcile-check-envelope`, `CAP-DLV-delivery-workflows`,
  `CAP-DLV-workflow-envelopes`, `CAP-DLV-proposal-incubation`.

## 1. Background & Hypothesis

### 1.1 Problem

- **Unbounded re-review.** At `high`, every path says only "re-review after the fixes" (`effort.md`, the
  `sdd-session-*` and `sdd-spec-*` workflow bodies, `spec-review`, both worker contracts, `CAP-DLV-delivery-workflows`).
  Nothing states a round's scope, its inputs, when the loop ends, or what happens when it does not converge.
- **No priority among findings.** A finding's `severity` is an optional free label with no effect on open-finding
  counts or checks (`CAP-DLV-workflow-envelopes`); the envelope reference's example value is `medium`.
- **Every fix costs a subagent round.** `medium` lets the implementer verify fixes; `high` leaves no room to close a
  typo or a fix the reviewer itself prescribed without another isolated review.
- **High Planning lacks evidence by rule.** `high` is proposed for work that reverses an accepted decision, creates a
  contract or document kind, or spans packages, yet `scout` runs only "when the direction needs evidence".
- **High session work.** Two of the three `high` triggers describe work that is not `session` depth; nothing says so.

### 1.2 Hypothesis

A `high` loop that runs fresh isolated review rounds until no P1 remains, sends each batch of fixes to the next round
unless every fix in it is strictly minor, and hands over to the user only when P1s persist to the cap, recur, or are contested
gives `high` a defined end and a higher bar than `medium` without spending a subagent round on each trivial fix.

## 2. Technical Spike Questions

All answered in Planning; the decisions are `PADR-bounded-high-effort-review-loop`.

- **Q1. Severity scale.** `P1`, `P2`, `P3` as exact strings, one P1 definition per review kind (§3.3). The reviewer
  owns the label; the implementer records it unchanged, and `reverify` already carries it forward. It is required on
  every finding at every effort; it still has no effect on checks.
- **Q2. Recurrence.** No new finding key: the schema accepts only `issue`, `evidence`, `failure_condition`,
  `suggested_action`, `resolution`, `waiver` and `severity`. The fresh reviewer receives the earlier findings and
  marks a recurrence with a fixed prefix in `issue` (`recurs: <envelope> #<n>;`). The cap is 3 rounds after the
  initial review.
- **Q3. Out-of-scope findings.** Derived, not marked: a finding is out of scope when its `evidence` path is not in
  the round's diff file list. It is fixed with the rest of the batch and never counts as a recurrence.
- **Q4. Planning loop.** The same loop applies to `challenger` rounds in `high` Planning with the Planning P1
  definition; `Decision needed:` findings stay out of it and go to `plan-accept`. A `challenger` envelope has no
  reverify: each round is a new `challenger-NN` envelope whose summary states what the previous round's findings
  became.
- **Q5. Session reclassification.** A SHOULD in the `spec` skill (`effort.md`) only: effort is never stored and a
  session is never evaluated by a command, so nothing can raise a notice.

## 3. Proposed Design & Impact

### 3.1 Review loop at `high`

Applies to code review (`code-reviewer`), reconcile verification (`reconcile-reviewer`) and `high` Planning
(`challenger`).

A round hands the reviewer the whole batch of work since the previous round; the implementer then handles every
finding of that round together, whatever its severity.

| Item | Rule |
| --- | --- |
| Round | A fresh reviewer instance. Round 1 reviews the whole change; each later round reviews every fix made since the previous round and what it affects. Input: the earlier rounds' findings, the round's diff scope and the effort. |
| Fixing | The implementer fixes every finding of the round, P1, P2 and P3 together (a P2 or P3 may be waived with a reason), and closes the round: `reverify` for code; for reconcile, a new `reconcile-check` naming the earlier one; for Planning, the next `challenger-NN` summary or the `worker` envelope's summary. |
| Next round | Runs when any fix of the batch fails the minor-fix conditions (§3.2). The whole batch goes to the next round, never a subset. |
| End | The round returns no finding, or every fix of the batch meets §3.2 and is self-verified. |
| Round count | Counted across `devkit workflow return` within one segment, from the round envelopes' summaries; a return does not reset it. |

Hand-over to the user:

| Cause | Unit path (worker or Host) | Session |
| --- | --- | --- |
| The round cap (3 rounds after the initial review) is reached and a P1 is still found | `problem` in the `worker` envelope; recovery names the open P1s | Reported in the conversation; not integrated |
| The same P1 recurs after its fix (marked `recurs:`) | Same | Same |
| A P1 the implementer holds invalid, still asserted after one more round given the implementer's counter-evidence (tests or output) | `questions` entry with the reviewer's and the implementer's positions as options | Asked in the conversation |

When the cap is reached with only P2 or P3 findings, the implementer fixes them and ends the loop, recording the
closures as self-verification.

This is not the `exception` stage; stages, checks and gates are unchanged. The stop reasons join the problem rule
of `CAP-DLV-delivery-workflows`.

### 3.2 Minor-fix self-verification at `high`

The initial `code-reviewer` and `reconcile-reviewer` calls stay mandatory, and so does the initial `challenger` in
`high` Planning. After a round, its batch of fixes MAY be self-verified instead of starting the next round only when
every fix in it meets all of these conditions:

| Condition | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| Location | Only the location the finding's `evidence` names | Only the document or entry the finding names | Only the proposal section the finding names |
| Nature | Typo, comment, formatting, in-scope rename, test-only addition, or the `suggested_action` applied as written when it names a concrete edit | Wording only, or a concrete `suggested_action` applied as written | Wording only, or a concrete `suggested_action` applied as written |
| Contract | No public API, schema, error code, CLI output or other package touched | The contract's meaning is unchanged | No decision changed |
| Evidence | Behavior fixes: a test or check reproducing the `failure_condition` passes (for a P1, it failed before the fix). Text-only kinds: the diff is limited to the named location | The edited text and the actual diff are shown to agree | The edited text is shown to agree with the finding |

- Uncertainty on any condition, for any fix, requires the next round for the whole batch.
- Recorded as self-verification with the reason and evidence: in `reverify` for code, in the new `reconcile-check`
  for reconcile, in the `worker` envelope's summary for Planning.
- A recurring finding can no longer be closed by self-verification.

### 3.3 Severity levels

| Level | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| P1 | Violates an acceptance criterion or contract; a correctness defect, data loss or a security issue | A missing target for a changed behavior or contract, or a reflection that contradicts the implementation or contract | The design fails, or conflicts with an accepted ADR or capability |
| P2 | A defect with a workaround | An incomplete or imprecise reflection with no contradiction | A defect in how a decision is specified, with a workaround |
| P3 | An improvement | An improvement | An improvement |

Severity is the reviewer's; the implementer records it as returned and never relabels it. It has no effect on checks;
the stage exits still count every open finding.

### 3.4 Mandatory `scout` in `high` Planning

`high` Planning runs `scout`, starting from `devkit spec refs <ID> --direction in` for each capability and ADR the
proposal touches, so its output is a list the `challenger` input cites. The `plan-accept` request reports a missing
`scout` envelope at `high` as it does a missing `challenger`.

### 3.5 Reclassification advice for `high` session work

When `high` is proposed for a `session` task, the advice follows the trigger: creating a contract or document kind
proposes `spec` depth; reversing an accepted decision proposes `proposal` depth; a multi-package change alone gives
no advice. If the user keeps `session`, the work runs at `high` as defined.

### 3.6 Out of scope

- **Plan review role.** A separate `plan-reviewer` before implementation. Reconsider when feedback records
  design-level P1s from `high` code review in two or more units.
- **Model and reasoning settings.** `activity-effort` stays independent of them.
- **Envelope schema.** No new finding key, envelope kind, stage or check.

### 3.7 Impact

- **Decision**: `PADR-bounded-high-effort-review-loop`, promoted to an ADR that supersedes
  `ADR-medium-review-delegation`: it restates the `medium` rules unchanged and adds the `high` rules. Development
  sets `supersedes` on the new ADR and `status: superseded` with `superseded_by` on the old one (its frontmatter
  only). `ADR-reconcile-check-envelope` keeps holding: the initial reconcile verification at `high` stays independent.
- **`devkit-spec` bundle** (`packages/devkit-spec/src/devkit_spec/bundle/`):
  - `skills/spec/references/effort.md` (table, rules, reclassification advice), `skills/spec/references/envelope.md`
    (severity example and values)
  - `skills/spec-review/SKILL.md` (loop, round order, severity), `skills/spec-delegate/SKILL.md` and
    `skills/spec-delegate/references/payload.md` (round inputs: earlier findings, round diff scope, effort)
  - role contracts `code-reviewer`, `reconcile-reviewer`, `challenger`, `scout`, `development-worker`,
    `planning-worker`
  - workflow bodies `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`, `sdd-spec-bugfix`,
    `sdd-proposal` (prose only; stage ids, checks and gates unchanged)
- **Tests**: `packages/devkit-spec/tests/` where they assert the contracts' or workflows' text.
- **Living Spec**: `CAP-DLV-delivery-workflows` (effort rules, problem rule), `CAP-DLV-workflow-envelopes` (severity
  meaning; no schema change), `CAP-DLV-proposal-incubation` (`plan-accept` gap report for `scout`).

### 3.8 Decisions

Decided by the user in Planning (`envelopes/answer-01.yaml`):

- Each round takes the whole batch of fixes since the previous round; all findings are fixed together and the next
  round is skipped only when every fix is minor. P2 and P3 findings may still be waived with a reason.
- A contested P1 gets one more fresh round with the implementer's counter-evidence and goes to the user only if
  asserted again.
- The new ADR supersedes `ADR-medium-review-delegation`.
- The round cap is 3 rounds after the initial review.
- Severity is required on every finding at every effort.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions are recorded as PADRs in `decisions/`; research goes in `materials/`.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff high-effort-review-loop`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
